"""V2 synthetic-only controller with external CPU, wall and RSS monitoring."""
from __future__ import annotations
import hashlib,json,os,re,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'timeout_repair_2026-11-18'
from result_guard import atomic_json
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def cpu_seconds(token):
    # ps formats mm:ss[.fraction], hh:mm:ss[.fraction], optional day prefix.
    if not re.fullmatch(r'(?:[0-9]+-)?[0-9]+:[0-9]{2}(?::[0-9]{2})?(?:\.[0-9]+)?',token):
        raise ValueError('Invalid ps CPU token')
    days=0;has_day_prefix='-' in token
    if has_day_prefix:
        d,token=token.split('-');days=int(d)
    fields=token.split(':')
    if len(fields)==2:
        minutes=int(fields[0]);seconds=float(fields[1])
        if has_day_prefix or seconds>=60:raise ValueError('Invalid minute format')
        return minutes*60+seconds
    hours,minutes=int(fields[0]),int(fields[1]);seconds=float(fields[2])
    if minutes>=60 or seconds>=60 or (has_day_prefix and hours>=24):raise ValueError('Invalid clock format')
    return days*86400+hours*3600+minutes*60+seconds

def parse_ps(line,pid):
    fields=line.split()
    if len(fields)!=3 or not fields[0].isdigit() or int(fields[0])!=pid or not fields[1].isdigit():
        raise ValueError('Invalid PID/RSS/CPU monitor record')
    return dict(pid=pid,rss_bytes=int(fields[1])*1024,cpu_seconds=cpu_seconds(fields[2]),cpu_token=fields[2])

def checked_classification(process,report):
    if process['watchdog_reason'] or process['returncode']!=0:return 'process_censored_or_failed'
    if not isinstance(report,dict):return 'missing_report'
    if report.get('finalized') is not True or report.get('handler_restored') is not True:return 'unfinalized_or_unrestored_report'
    return report.get('classification','invalid_report')

def units():
    for token,value in [('0:00.00',0.),('1:02.34',62.34),('123:45.00',7425.),('1:02:03.45',3723.45),('2-01:02:03.00',176523.)]:
        assert abs(cpu_seconds(token)-value)<1e-8
    for token in ('','nan','-1:00.0','0:60.00','1:60:00','2-24:00:00','1-02:03','0:00.00 extra','0:0.0','1e3:00.00','0-02:03','0-24:00:00'):
        try:cpu_seconds(token)
        except ValueError:pass
        else:raise AssertionError(token)
    assert parse_ps('123 4096 0:03.01',123)['cpu_seconds']==3.01
    for line in ('124 4096 0:03.00','123 bad 0:00.00','123 4096 nan','123 4096 0:00.00 extra'):
        try:parse_ps(line,123)
        except ValueError:pass
        else:raise AssertionError(line)
    ok=dict(returncode=0,watchdog_reason=None)
    for cause in ('cpu_limit','wall_limit','rss_limit','monitor_failure'):
        assert checked_classification(dict(ok,watchdog_reason=cause),dict(finalized=True,handler_restored=True,classification='solver_completed'))=='process_censored_or_failed'
    assert checked_classification(dict(ok,returncode=1),dict(finalized=True,handler_restored=True,classification='solver_completed'))=='process_censored_or_failed'
    assert checked_classification(ok,None)=='missing_report'
    assert checked_classification(ok,dict(finalized=False))=='unfinalized_or_unrestored_report'
    return dict(passed=True,parser_valid_examples=5,parser_invalid_examples=12,invalid_monitor_examples=4,budget_and_exit_censoring=True)

def run_child(name,scenario,n,limit,inject,wall):
    out=ROOT/'confirmation'/name;out.mkdir(parents=True)
    cfg=dict(scenario=scenario,n=n,time_limit=limit,seed=2026111801,output=str(out.resolve()))
    atomic_json(out/'config.json',cfg)
    started=time.monotonic();peak=0;reason=None;injection=None;monitor_error=None
    samples=[];actions=[];cpu_limit=3. if scenario=='cpu_hard' else 10.
    with (out/'stdout.log').open('w') as stream:
        proc=subprocess.Popen([sys.executable,str(ROOT/'worker.py'),str(out/'config.json')],stdout=stream,stderr=subprocess.STDOUT)
        try:
            while proc.poll() is None:
                if time.monotonic()-started>wall:reason='wall_limit'
                if reason is None:
                    try:
                        query_at=time.monotonic()
                        result=subprocess.run(['ps','-o','pid=,rss=,time=','-p',str(proc.pid)],capture_output=True,text=True,timeout=1)
                        if result.stdout.strip():
                            if result.returncode:raise ValueError('ps error with data')
                            sample=parse_ps(result.stdout.strip(),proc.pid)
                            sample.update(query_started=query_at,observed_at=time.monotonic(),raw=result.stdout.strip())
                            samples.append(sample);peak=max(peak,sample['rss_bytes'])
                            if sample['cpu_seconds']>=cpu_limit:reason='cpu_limit'
                            elif sample['rss_bytes']>1073741824:reason='rss_limit'
                        elif proc.poll() is None:raise ValueError('Missing active-process monitor data')
                    except Exception as exc:
                        monitor_error=f'{type(exc).__name__}: {exc}';reason='monitor_failure'
                # Recheck after a potentially stalled ps query.
                if reason is None and time.monotonic()-started>wall:reason='wall_limit'
                marker='persist_ready.json' if scenario=='late_persistence' else 'ready.json'
                if reason is None and inject and injection is None and (out/marker).exists():
                    ready=read(out/marker)
                    if time.monotonic()-ready['at']['monotonic']>=.02:
                        injection=dict(pid=proc.pid,signum=int(signal.SIGXCPU),sent_at_monotonic=time.monotonic(),ready=ready)
                        try:proc.send_signal(signal.SIGXCPU);injection['sent']=True
                        except ProcessLookupError:injection['sent']=False
                if reason:
                    actions.append(dict(pid=proc.pid,signum=int(signal.SIGTERM),at=time.monotonic(),reason=reason))
                    proc.terminate()
                    try:proc.wait(timeout=.5)
                    except subprocess.TimeoutExpired:
                        actions.append(dict(pid=proc.pid,signum=int(signal.SIGKILL),at=time.monotonic(),reason=reason))
                        proc.kill();proc.wait()
                    break
                time.sleep(.01)
        finally:
            # Never leave an owned child alive if the controller raises.
            if proc.poll() is None:proc.kill();proc.wait()
        code=proc.wait()
    process=dict(pid=proc.pid,parent_pid=os.getpid(),started_monotonic=started,returncode=code,watchdog_reason=reason,
        monitor_error=monitor_error,peak_rss_bytes=peak,wall_seconds=time.monotonic()-started,
        controlled_injection=injection,expected_wall_limit=wall,expected_cpu_limit=cpu_limit,
        monitor_samples=samples,termination_actions=actions)
    report=read(out/'result.json') if (out/'result.json').exists() else None
    process['classification']=checked_classification(process,report)
    atomic_json(out/'process.json',process)
    row=dict(name=name,scenario=scenario,folder=out.relative_to(ROOT).as_posix(),process=process,
        has_incumbent=report.get('has_incumbent') if report else None,solver_status=report.get('solver_status') if report else None)
    print(json.dumps(dict(name=name,returncode=code,classification=process['classification'],watchdog_reason=reason,solver_status=row['solver_status'],has_incumbent=row['has_incumbent'])),flush=True)
    return row

def prior_check():
    for name,digest in read(OLD/'manifest.json')['files'].items():assert sha(OLD/name)==digest,name
    for name in ('worker.py','result_guard.py'):assert sha(ROOT/name)==sha(OLD/name),name

def freeze():
    assert not (ROOT/'frozen.json').exists(),'Preserve freeze'
    prior_check();c=read(OLD/'calibration_result.json');v1=read(OLD/'confirmation_result.json');assert c['passed']
    prior_wall=c['controller_wall_seconds']+v1['controller_wall_seconds']
    assert c['optimization_calls']==2 and v1['confirmation_optimizer_calls']==5
    paths=[ROOT/n for n in ('PLAN.md','worker.py','result_guard.py','control.py','audit.py','PREFLIGHT.md','unit_result.json','unit_result_initial.json')]
    paths += [OLD/'manifest.json',OLD/'frozen.json',OLD/'calibration_result.json',OLD/'confirmation_result.json',OLD/'V1_OUTCOME.json']
    f=dict(files={str(p.resolve()):sha(p) for p in paths},selected_fixture=c['selected_with_incumbent'],
        confirmation_scenarios=['timeout_none','timeout_incumbent','legacy_injected','deferred_injected','optimal','soft_cpu','hard_cpu','wall_guard','late_persistence'],
        max_confirmation_optimizer_calls=5,prior_optimizer_calls=7,max_cumulative_optimizer_calls=12,real_research_calls=0,
        prior_children=11,max_cumulative_children=20,prior_controller_wall_seconds=prior_wall,
        confirmation_controller_wall_cap=min(85.,120.-prior_wall),cumulative_controller_wall_cap=120.,
        wall_seconds_each=8.,rss_bytes=1073741824,cpu_seconds_normal=10.,cpu_seconds_hard_fixture=3.)
    atomic_json(ROOT/'frozen.json',f)
    print(json.dumps(dict(frozen=True,files=len(f['files']),sha256=sha(ROOT/'frozen.json'))))

def confirm():
    assert not (ROOT/'confirmation').exists() and not (ROOT/'confirmation_result.json').exists(),'Preserve partial/full execution; no retries'
    f=read(ROOT/'frozen.json');prior_check()
    for name,digest in f['files'].items():assert sha(Path(name))==digest,name
    units();t=time.monotonic();chosen=f['selected_fixture'];n=chosen['n'];limit=chosen['time_limit'];rows=[]
    specs=[('timeout_none','normal',200,0.,False,8.),('timeout_incumbent','normal',n,limit,False,8.),
        ('legacy_injected','legacy_signal',n,limit,True,8.),('deferred_injected','deferred_signal',n,limit,True,8.),
        ('optimal','normal',6,1.,False,8.),('soft_cpu','cpu_soft',0,0.,False,8.),
        ('hard_cpu','cpu_hard',0,0.,False,8.),('wall_guard','wall_kill',0,0.,False,.15),
        ('late_persistence','late_persistence',6,0.,True,8.)]
    for name,scenario,nn,ll,inject,wall in specs:
        if time.monotonic()-t+10>f['confirmation_controller_wall_cap']:break
        rows.append(run_child(name,scenario,nn,ll,inject,wall))
        atomic_json(ROOT/'confirmation_progress.json',dict(rows=rows))
    elapsed=time.monotonic()-t
    atomic_json(ROOT/'confirmation_result.json',dict(rows=rows,controller_wall_seconds=elapsed,
        cumulative_controller_wall_seconds=f['prior_controller_wall_seconds']+elapsed,
        confirmation_optimizer_calls=sum(r['scenario'] not in ('cpu_soft','cpu_hard','wall_kill','late_persistence') for r in rows),
        prior_optimizer_calls=7,all_scenarios_attempted=len(rows)==len(specs),real_research_calls=0,frozen_sha256=sha(ROOT/'frozen.json')))
    paths=list((ROOT/'confirmation').rglob('*'))+[ROOT/'confirmation_result.json']
    atomic_json(ROOT/'output_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in paths if p.is_file()}))

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('units','freeze','confirm'):raise SystemExit('Usage: control.py units|freeze|confirm')
    if sys.argv[1]=='units':
        assert not (ROOT/'unit_result.json').exists(),'Preserve unit result'
        value=units();atomic_json(ROOT/'unit_result.json',value);print(json.dumps(value))
    else:{'freeze':freeze,'confirm':confirm}[sys.argv[1]]()
