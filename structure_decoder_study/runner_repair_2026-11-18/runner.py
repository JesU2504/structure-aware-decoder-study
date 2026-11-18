"""Owned os.posix_spawn/wait4 runner. ps is interim telemetry, never an exit oracle."""
from __future__ import annotations
import fcntl,hashlib,json,math,os,re,signal,subprocess,sys,time
from pathlib import Path
from owner import KernelChild
ROOT=Path(__file__).resolve().parent
LAST_LAUNCH={}
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):
    path=Path(path);temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n');temp.replace(path)
def seconds(token):
    if not re.fullmatch(r'\d+:\d{2}(?::\d{2})?(?:\.\d+)?',token):raise ValueError('Malformed TIME')
    fields=token.split(':');sec=float(fields[-1]);assert sec<60
    result=sec+60*int(fields[-2])+(3600*int(fields[0]) if len(fields)==3 else 0)
    if len(fields)==3 and int(fields[1])>=60:raise ValueError('Malformed minutes')
    if not math.isfinite(result):raise ValueError('Nonfinite TIME')
    return result
def parse(raw,pid):
    fields=raw.split()
    if len(fields)!=4 or not fields[0].isdigit() or int(fields[0])!=pid:raise ValueError('Bad PID/fields')
    if not fields[2].isdigit():raise ValueError('Bad RSS')
    stat=fields[1];modifiers='+<>AELNSsVWX'
    if not stat or any(c not in modifiers for c in stat[1:]) or len(stat)>16:raise ValueError('Unknown state/modifiers')
    kind='live' if stat[0] in 'IRSTU' else 'candidate' if stat[0]=='Z' or stat=='?E' else 'invalid'
    if kind=='invalid':raise ValueError('Unsupported state')
    return dict(kind=kind,stat=stat,cpu=seconds(fields[3]),rss=int(fields[2])*1024)
def ps_query(pid):
    start=time.monotonic()
    try:
        p=subprocess.run(['ps','-o','pid=,stat=,rss=,time=','-p',str(pid)],capture_output=True,text=True,timeout=.5)
        return dict(start=start,end=time.monotonic(),raw=p.stdout,stderr=p.stderr,returncode=p.returncode,error=None)
    except Exception as exc:return dict(start=start,end=time.monotonic(),raw='',returncode=-999,error=f'{type(exc).__name__}: {exc}')
def classify(owner,reasons):
    if owner.errors or not owner.final:return 'ownership_or_final_usage_failure'
    if reasons:return 'censored'
    return 'ordinary_exit' if owner.final['returncode']==0 else 'nonzero_or_signal_exit'
def above_stdio(fd,owned):
    if fd>2:return fd
    new=fcntl.fcntl(fd,fcntl.F_DUPFD_CLOEXEC,3);owned.add(new)
    os.close(fd);owned.remove(fd);return new
def validate_config(cfg):
    for key in ('cpu_limit','wall_limit'):
        v=cfg[key]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0:raise ValueError('Invalid limit')
    if isinstance(cfg['rss_limit'],bool) or not isinstance(cfg['rss_limit'],int) or cfg['rss_limit']<=0:raise ValueError('Invalid RSS limit')
    if cfg['OS_CPU_request']!=[5,6]:raise ValueError('Unsupported OS CPU request')

def run(config_path):
    LAST_LAUNCH.clear();LAST_LAUNCH['spawn_returned']=False
    cfg=read(config_path);validate_config(cfg);out=Path(cfg['output']);out.mkdir(parents=True)
    owner=KernelChild();fds=set();stdin_write=None;queries=[];reasons=[];pending=None;injection=None;setup_error=None
    cpu_high=0.;rss_high=0;started=time.monotonic();gap=None
    def reason(value):
        if value not in reasons:reasons.append(value)
    def budgets():
        if cpu_high>=cfg['cpu_limit']:reason('cpu_limit')
        if rss_high>cfg['rss_limit']:reason('rss_limit')
        if time.monotonic()-started>=cfg['wall_limit']:reason('wall_limit')
    try:
        stdin_read,stdin_write=os.pipe();fds.update((stdin_read,stdin_write))
        stdin_read=above_stdio(stdin_read,fds);stdin_write=above_stdio(stdin_write,fds)
        log_fd=os.open(out/'stdout.log',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);fds.add(log_fd)
        log_fd=above_stdio(log_fd,fds)
        actions=[(os.POSIX_SPAWN_DUP2,stdin_read,0),(os.POSIX_SPAWN_DUP2,log_fd,1),(os.POSIX_SPAWN_DUP2,log_fd,2),
            (os.POSIX_SPAWN_CLOSE,stdin_read),(os.POSIX_SPAWN_CLOSE,stdin_write),(os.POSIX_SPAWN_CLOSE,log_fd)]
        save(out/'spawn_attempt.json',dict(nonce=cfg['nonce'],at=started,SIGCHLD=int(signal.getsignal(signal.SIGCHLD))))
        pid=os.posix_spawn(sys.executable,[sys.executable,'-B',str(ROOT/'fixture.py'),str(config_path)],dict(os.environ),
            file_actions=actions,setsigmask=(),setsigdef=(signal.SIGTERM,signal.SIGINT,signal.SIGXCPU))
        try:
            LAST_LAUNCH.update(name=cfg['name'],nonce=cfg['nonce'],pid=pid,spawn_returned=True,at=time.monotonic())
            owner.bind(pid) # No competing reaper exists; this try begins immediately after spawn.
            for fd in (stdin_read,log_fd):os.close(fd);fds.remove(fd)
            save(out/'launch.json',dict(pid=pid,parent_pid=os.getpid(),nonce=cfg['nonce'],at=time.monotonic(),
                executable=sys.executable,config_sha256=sha(config_path)))
            if cfg['name']=='setup_failure':raise OSError('Controlled post-spawn setup failure')
            if cfg['name']=='final_CPU_over_budget':
                gap=dict(start=time.monotonic(),control_only=True,sampling='kernel_only_until_exit')
            while not owner.reaped and not owner.lost:
                owner.poll()
                if owner.reaped or owner.lost:break
                if owner.errors:reason('kernel_owner_error')
                budgets()
                if reasons:break
                if gap is not None:
                    time.sleep(.005);continue # This dedicated control tests final-only CPU accounting.
                if pending is not None:
                    if time.monotonic()-pending>.5:reason('exit_confirmation_timeout');break
                    time.sleep(.005);continue
                before=len(owner.events);q=ps_query(pid)
                owner.poll();q['kernel_events_before_query']=before;q['kernel_events_after_query']=len(owner.events)
                truth=None
                try:
                    if q['error'] or q['returncode'] not in (0,1):raise ValueError('Failed interim query')
                    if q['raw'].strip():
                        if q['returncode']!=0:raise ValueError('Failed query with data')
                        observed=parse(q['raw'],pid)
                        ready=read(out/'ready.json') if (out/'ready.json').exists() else None
                        if cfg.get('fault') and injection is None and cpu_high>0 and observed['kind']=='live' and observed['cpu']>=.1 and ready and q['start']>=ready['at']['monotonic']:
                            truth=dict(q);changed='R' if cfg['fault']=='live_reset' else '?E'
                            q=dict(q,raw=f'{pid} {changed} {observed["rss"]//1024 if changed=="R" else 0} 0:00.00\n')
                            injection=dict(kind=cfg['fault'],truth=truth,mutated=dict(q),at=time.monotonic())
                            observed=parse(q['raw'],pid)
                        if observed['kind']=='live':
                            if observed['rss']==0 or observed['cpu']<cpu_high:raise ValueError('Invalid live telemetry')
                            cpu_high=max(cpu_high,observed['cpu']);rss_high=max(rss_high,observed['rss'])
                        else:
                            cpu_high=max(cpu_high,observed['cpu']);rss_high=max(rss_high,observed['rss']);pending=q['end']
                            q['terminal_candidate']=True
                            if cfg['name']=='exit_candidate_confirmed' and injection:
                                os.write(stdin_write,b'EXIT\n');injection['permission_sent_at']=time.monotonic()
                    else:
                        pending=q['end'];q['PID_absent_pending_confirmation']=True
                except (AssertionError,ValueError,TypeError,OverflowError) as exc:reason('monitor_invalid: '+str(exc))
                queries.append(q);budgets()
                if reasons:break
                time.sleep(.01)
        except BaseException as exc:
            setup_error=f'{type(exc).__name__}: {exc}';reason('setup_or_runner_error')
        finally:
            # The same owner handles cleanup and final usage, including setup failures.
            if owner.pid is None:owner.bind(pid)
            if not owner.reaped and not owner.lost:owner.stop(reasons or ['finally_cleanup'])
            if not owner.reaped and not owner.lost:reason('containment_failure')
    finally:
        for fd in fds:
            try:os.close(fd)
            except OSError:pass
        if owner.pid is not None:LAST_LAUNCH.update(reaped=owner.reaped,ownership_lost=owner.lost)
    if owner.final:
        final=owner.final['usage']
        if final['total_cpu']>=cfg['cpu_limit']:reason('cpu_limit')
        if final['peak_rss_bytes']>cfg['rss_limit']:reason('rss_limit')
        if owner.final['reaped_at']-started>=cfg['wall_limit']:reason('wall_limit')
    if gap is not None:gap['end']=time.monotonic()
    result=dict(name=cfg['name'],nonce=cfg['nonce'],pid=owner.pid,started=started,ended=time.monotonic(),
        classification=classify(owner,reasons),reasons=reasons,setup_error=setup_error,
        kernel_final=owner.final,ownership_errors=owner.errors,kernel_events=owner.events,signals=owner.signals,
        ps_cpu_highwater=cpu_high,ps_RSS_highwater=rss_high,ps_queries=queries,controlled_injection=injection,
        terminal_telemetry_unavailable=pending is not None,observation_gap=gap,
        peak_RSS_and_CPU_sources_kept_separate=True,OS_hard_limit_enforcement_claim=False,
        native_optimizers_called=0,quantum_decoders_called=0)
    save(out/'result.json',result);return result
