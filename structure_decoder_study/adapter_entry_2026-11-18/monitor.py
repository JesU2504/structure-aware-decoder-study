"""Owned-child monitor implementing the frozen prospective accounting policy."""
from __future__ import annotations
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
from accounting_policy import Accounting,parse_record
from result_guard import atomic_json
ROOT=Path(__file__).resolve().parent
ACTIVE_OWNED=[]
LAST_SPAWN={}
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(stream,value):
    stream.write(json.dumps(value,sort_keys=True,allow_nan=False)+'\n');stream.flush()
def poll_record(proc):
    result=proc.poll()
    return dict(at=time.monotonic(),returncode=result)
def query(proc):
    started=time.monotonic()
    try:
        value=subprocess.run(['ps','-o','pid=,stat=,rss=,time=','-p',str(proc.pid)],capture_output=True,text=True,timeout=1.)
        return dict(start=started,end=time.monotonic(),stdout=value.stdout,stderr=value.stderr,returncode=value.returncode,error=None)
    except Exception as exc:
        return dict(start=started,end=time.monotonic(),stdout='',stderr='',returncode=-999,error=f'{type(exc).__name__}: {exc}')

def bounded_stop(proc,reasons,actions):
    """Cleanup independent of Accounting, log writers or child metadata."""
    for signum in (signal.SIGTERM,signal.SIGKILL):
        before=poll_record(proc)
        if before['returncode'] is not None:break
        action=dict(pid=proc.pid,signum=int(signum),requested_at=time.monotonic(),
            before=before,reasons=list(reasons))
        try:proc.send_signal(signum);action['signal_API_returned']=True
        except Exception as exc:action['signal_API_returned']=False;action['signal_error']=f'{type(exc).__name__}: {exc}'
        action['wait_started']=time.monotonic()
        try:action['wait_returncode']=proc.wait(timeout=.5);action['wait_timed_out']=False
        except subprocess.TimeoutExpired:action['wait_returncode']=None;action['wait_timed_out']=True
        except Exception as exc:action['wait_returncode']=None;action['wait_timed_out']=True;action['wait_error']=f'{type(exc).__name__}: {exc}'
        action['wait_finished']=time.monotonic();actions.append(action)
        if action['wait_returncode'] is not None:break

def reap_after_stop(proc,state,actions):
    """Bounded signals/waits; no ps queries, broad waitpid or PID-only cleanup."""
    bounded_stop(proc,state.censor_reasons,actions)
    before=poll_record(proc);after=poll_record(proc)
    if before['returncode'] is not None:
        event=dict(before=before,query=None,after=after,cleanup_reap=True)
        return event,False
    state.fail('containment_failure_unreaped_after_TERM_KILL')
    return None,True

def checked_snapshots(out,identity,pid,state):
    """Child already reaped. Check complete-file identities before adding telemetry."""
    checked=[]
    names=('startup.json','progress.json','raw_metadata.json','handler_restoration.json','final.json',
        'allocation_start.json','allocated.json','ready.json')
    for name in names:
        path=out/name
        if not path.exists():continue
        data=read(path);assert data.get('identity')==identity,('Child identity mismatch',name)
        states=[]
        for key in ('before_limits','after_limits','at','before_call','after_call','finalized_at'):
            if isinstance(data.get(key),dict) and 'cpu_absolute' in data[key]:states.append((key,data[key]))
        for key,at in states:
            assert at['pid']==pid and at['monotonic']>=state.started_at and at['monotonic']<=state.last_at
            assert at['cpu_absolute']>=0 and at['peak_rss_bytes']>=0
            assert abs(at['cpu_absolute']-at['ru_utime']-at['ru_stime'])<.1
            state.checked_child_cpu(pid,at['monotonic'],at['cpu_absolute'])
            state.rss_highwater=max(state.rss_highwater,int(at['peak_rss_bytes']))
            state.budget(state.last_at)
            checked.append(dict(file=name,file_sha256=sha(path),key=key,telemetry=at))
    return checked

def _watch_owned(config_path,cfg,out,identity,started,proc,log,cleanup):
    actions=cleanup["actions"];injection=None;fault=None;permission=None;trace=[];failure=None
    atomic_json(out/'launch.json',dict(identity=identity,pid=proc.pid,parent_pid=os.getpid(),
        started_monotonic=started,parent_observed_spawn_complete=time.monotonic(),
        command=[sys.executable,'-B',str(ROOT/'worker.py'),str(config_path)],
        PID_only_resume_or_cleanup_supported=False))
    state=Accounting(proc.pid,started_at=started,cpu_limit=cfg['limits']['cpu'],wall_limit=cfg['limits']['wall'],rss_limit=cfg['limits']['rss'])
    def ingest(event):
        decision=state.advance(event);item=dict(event=event,decision=decision)
        trace.append(item);record(log,item)
        return decision
    try:
        while state.phase!='REAPED':
            before=poll_record(proc)
            if before['returncode'] is not None:
                ingest(dict(before=before,query=None,after=poll_record(proc)));break
            if state.phase=='REAPING':
                remaining=max(0.,.5-(time.monotonic()-state.reaping_started))
                try:proc.wait(timeout=remaining)
                except subprocess.TimeoutExpired:pass
                decision=ingest(dict(before=before,query=None,after=poll_record(proc),bounded_reaping_wait=True))
            else:
                q=query(proc)
                truth_query=None
                if cfg['mode']=='fault' and fault is None and (out/'ready.json').exists() and not q['error'] and q['returncode']==0:
                    true=parse_record(q['stdout'].strip(),proc.pid)
                    if true['state']!='Z' and true['rss_bytes']>0:
                        truth_query=dict(q);q=dict(q,stdout=f'{proc.pid} {true["stat"]} NOT_A_NUMBER {true["cpu_token"]}\n')
                        fault=dict(kind='controlled_invalid_RSS_field',at=time.monotonic(),true_query=truth_query,corrupted_query=dict(q))
                decision=ingest(dict(before=before,query=q,after=poll_record(proc),controlled_fault=fault if truth_query else None))
            if state.phase=='REAPED':break
            if state.censor_reasons:
                cleanup["attempted"]=True
                if state.terminal_state_observed:
                    # A Z process needs owned reaping, not another live signal.
                    try:proc.wait(timeout=.5)
                    except subprocess.TimeoutExpired:state.fail('containment_failure_unreaped_Z')
                    b=poll_record(proc)
                    if b['returncode'] is not None:ingest(dict(before=b,query=None,after=poll_record(proc),cleanup_reap=True))
                    else:failure='containment_failure_unreaped_Z'
                else:
                    event,unreaped=reap_after_stop(proc,state,actions)
                    if event is not None:ingest(event)
                    if unreaped:failure='containment_failure_unreaped_after_TERM_KILL'
                break
            if cfg.get('inject_signal') and injection is None and decision['injections_allowed']:
                marker=out/('persist_ready.json' if cfg['mode']=='mock' else 'ready.json')
                if marker.exists():
                    ready=read(marker);assert ready['identity']==identity
                    if time.monotonic()-ready['at']['monotonic']>=.02:
                        b=poll_record(proc)
                        if b['returncode'] is None:
                            injection=dict(pid=proc.pid,signum=int(signal.SIGXCPU),at=time.monotonic(),before=b,marker=ready)
                            proc.send_signal(signal.SIGXCPU);injection['signal_API_returned']=True
            if cfg['mode']=='terminal' and permission is None and decision['injections_allowed'] and (out/'ready.json').exists():
                # Validate a positive LIVE sample before opening the exit barrier.
                last=trace[-1]['event'].get('query')
                live=parse_record(last['stdout'].strip(),proc.pid) if last and last['returncode']==0 else None
                ready=read(out/'ready.json');assert ready['identity']==identity
                if live and live['state']!='Z' and live['cpu_seconds']>=.1 and last['start']>=ready['at']['monotonic']:
                    b=poll_record(proc)
                    if b['returncode'] is None:
                        permission=dict(before=b,at=time.monotonic(),positive_live_record=last)
                        proc.stdin.write('EXIT\n');proc.stdin.flush()
                        permission['released_at']=time.monotonic()
                        time.sleep(.05) # Fixed single controlled observation; no poll/wait here.
                        q=query(proc)
                        event=dict(before=b,query=q,after=poll_record(proc),controlled_exit_permission=dict(permission))
                        ingest(event);permission['single_query']=q
                        if state.phase=='REAPED':break
                        # No second ps query is allowed after permission; normal REAPING uses owned wait.
                        if state.phase=='RUNNING':state.fail('controlled_Z_observation_unmet')
                        if state.censor_reasons:
                            cleanup["attempted"]=True
                            event,unreaped=reap_after_stop(proc,state,actions)
                            if event is not None:ingest(event)
                            if unreaped:failure='containment_failure_unreaped_after_TERM_KILL'
                            break
            time.sleep(.01)
    except BaseException as exc:
        failure=f'{type(exc).__name__}: {exc}';state.fail('monitor_exception: '+failure)
    finally:
        # Normal exceptions/interrupts retain owned cleanup. Abrupt parent SIGKILL is outside this test.
        if proc.returncode is None and proc.poll() is None and not cleanup["attempted"]:
            cleanup["attempted"]=True
            event,unreaped=reap_after_stop(proc,state,actions)
            if event is not None:ingest(event)
            if unreaped:failure='containment_failure_unreaped_after_TERM_KILL'
        elif proc.returncode is not None and state.phase!='REAPED':
            b=poll_record(proc);ingest(dict(before=b,query=None,after=poll_record(proc),cleanup_reap=True))
        if proc.stdin is not None:proc.stdin.close()
    checked=[]
    if state.phase=='REAPED':
        try:checked=checked_snapshots(out,identity,proc.pid,state)
        except Exception as exc:state.fail(f'child_snapshot_validation: {type(exc).__name__}: {exc}')
    final=read(out/'final.json') if (out/'final.json').exists() else None
    process=dict(identity=identity,pid=proc.pid,parent_pid=os.getpid(),started_monotonic=started,
        ended_monotonic=time.monotonic(),wall_seconds=time.monotonic()-started,returncode=proc.returncode,
        accounting=state.snapshot(),cpu_sources=state.cpu_sources,checked_child_snapshots=checked,
        termination_actions=actions,controlled_signal=injection,controlled_fault=fault,exit_permission=permission,
        monitor_failure=failure,observations=len(trace),monitor_trace_sha256=sha(out/'monitor.jsonl'))
    atomic_json(out/'process.json',process)
    return process,final

def finalize_owned(proc,cleanup,out,identity):
    """Fallback covers setup/logging failures before Accounting or ingest exists."""
    fallback=False
    try:
        if proc.returncode is None and proc.poll() is None and not cleanup['attempted']:
            fallback=True;cleanup['attempted']=True
            bounded_stop(proc,['outer_monitor_setup_or_persistence_failure'],cleanup['actions'])
    finally:
        reaped=proc.poll() is not None
        if reaped and proc in ACTIVE_OWNED:ACTIVE_OWNED.remove(proc)
        LAST_SPAWN.update(pid=proc.pid,reaped=reaped)
        try:
            if proc.stdin is not None:proc.stdin.close()
        except Exception:pass
        try:
            atomic_json(out/'cleanup_summary.json',dict(identity=identity,pid=proc.pid,reaped=reaped,
                fallback_cleanup=fallback,actions=cleanup['actions'],at=time.monotonic()))
        except Exception:pass # Cleanup itself must not depend on writable metadata.

def watch(config_path):
    cfg=read(config_path);out=Path(cfg['output']);out.mkdir(parents=True)
    identity=dict(cfg['identity'],config_sha256=sha(config_path));started=time.monotonic()
    cleanup=dict(attempted=False,actions=[])
    LAST_SPAWN.clear();LAST_SPAWN.update(identity=identity,spawn_returned=False)
    atomic_json(out/'spawn_attempt.json',dict(identity=identity,at=started,command_worker=str(ROOT/'worker.py')))
    with (out/'stdout.log').open('x') as stdout,(out/'monitor.jsonl').open('x') as log:
        proc=subprocess.Popen([sys.executable,'-B',str(ROOT/'worker.py'),str(config_path)],
            stdin=subprocess.PIPE,stdout=stdout,stderr=subprocess.STDOUT,text=True)
        try:
            LAST_SPAWN.update(pid=proc.pid,spawn_returned=True,at=time.monotonic())
            ACTIVE_OWNED.append(proc)
            return _watch_owned(config_path,cfg,out,identity,started,proc,log,cleanup)
        finally:
            finalize_owned(proc,cleanup,out,identity)
