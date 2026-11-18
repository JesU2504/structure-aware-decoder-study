"""Fixed twelve stdlib-only runner checks. No solver or research launch mode."""
import hashlib,json,platform,signal,sys,time,uuid
from pathlib import Path
import runner
from runner import run,save,read,sha
ROOT=Path(__file__).resolve().parent
def configure():
    assert not (ROOT/'frozen.json').exists()
    nonce=str(uuid.uuid4());names=[('normal_exit','normal'),('nonzero_exit','nonzero'),('cpu_work','cpu_work'),
        ('final_CPU_over_budget','final_CPU'),('parent_wall','sleep'),('parent_CPU','spin'),('parent_RSS','rss'),
        ('TERM_to_KILL','ignore_TERM'),('setup_failure','sleep'),('exit_candidate_confirmed','barrier'),
        ('live_counter_reset','barrier'),('exit_candidate_timeout','barrier')]
    (ROOT/'configs').mkdir(exist_ok=True)
    files=[]
    for index,(name,mode) in enumerate(names):
        cfg=dict(name=name,mode=mode,nonce=nonce,cpu_limit=3.,wall_limit=4.,rss_limit=268435456,
            output=str((ROOT/'runs'/name).resolve()),OS_CPU_request=[5,6])
        if name=='final_CPU_over_budget':cfg['cpu_limit']=.05
        if name=='parent_CPU':cfg['cpu_limit']=.25
        if name=='parent_wall':cfg['wall_limit']=.15
        if name=='parent_RSS':cfg['rss_limit']=67108864
        if name=='TERM_to_KILL':cfg['wall_limit']=.3
        if name in ('exit_candidate_confirmed','exit_candidate_timeout'):cfg['fault']='exit_candidate'
        if name=='live_counter_reset':cfg['fault']='live_reset'
        file=f'{index:02d}_{name}.json';save(ROOT/'configs'/file,cfg);files.append(file)
    save(ROOT/'plan.json',dict(scope='stdlib_runner_only',configs=files,nonce=nonce,max_workers=12,
        controller_seconds=90.,admission_reserve=8.,calibration=0,retries=0,optimizer_calls=0,research_cases=0,
        real_os_ps_state_reproduction_required=False,final_CPU_control='kernel-only observations until exit, wall4 still enforced'))
    save(ROOT/'environment.json',dict(platform=platform.platform(),python=sys.version,executable=sys.executable,
        executable_resolved=str(Path(sys.executable).resolve()),binary_sha256=sha(Path(sys.executable).resolve()),
        SIGCHLD=int(signal.getsignal(signal.SIGCHLD))))
    print(json.dumps(dict(configured=12,new_optimizer_calls=0)))
def stop_valid(result,expected):
    a=result['signals'];final=result['kernel_final']
    if not final or not a or a[0]['signum']!=15 or any(not x.get('API_returned') for x in a):return False
    if expected==-15:return len(a)==1 and final['returncode']==-15 and a[0]['returncode_after_wait']==-15 and not a[0]['wait_timed_out']
    return (len(a)==2 and final['returncode']==-9 and a[0]['wait_timed_out'] and a[0]['returncode_after_wait'] is None
        and a[0]['wait_ended']-a[0]['wait_started']>=.49 and a[1]['requested_at']>=a[0]['wait_ended']
        and a[1]['signum']==9 and a[1]['returncode_after_wait']==-9 and not a[1]['wait_timed_out'])
def validate_plan():
    plan=read(ROOT/'plan.json')
    names=['normal_exit','nonzero_exit','cpu_work','final_CPU_over_budget','parent_wall','parent_CPU','parent_RSS',
        'TERM_to_KILL','setup_failure','exit_candidate_confirmed','live_counter_reset','exit_candidate_timeout']
    modes=['normal','nonzero','cpu_work','final_CPU','sleep','spin','rss','ignore_TERM','sleep','barrier','barrier','barrier']
    assert plan['max_workers']==12 and len(plan['configs'])==12 and plan['controller_seconds']==90. and plan['admission_reserve']==8.
    assert plan['scope']=='stdlib_runner_only' and plan['optimizer_calls']==plan['research_cases']==plan['calibration']==plan['retries']==0
    for file,name,mode in zip(plan['configs'],names,modes):
        cfg=read(ROOT/'configs'/file);runner.validate_config(cfg)
        assert cfg['name']==name and cfg['mode']==mode and cfg['nonce']==plan['nonce']
        assert cfg['output']==str((ROOT/'runs'/name).resolve()) and cfg['OS_CPU_request']==[5,6]
        assert cfg['cpu_limit']==(.05 if name=='final_CPU_over_budget' else .25 if name=='parent_CPU' else 3.)
        assert cfg['wall_limit']==(.15 if name=='parent_wall' else .3 if name=='TERM_to_KILL' else 4.)
        assert cfg['rss_limit']==(67108864 if name=='parent_RSS' else 268435456)
        assert cfg.get('fault')==('live_reset' if name=='live_counter_reset' else 'exit_candidate' if name in ('exit_candidate_confirmed','exit_candidate_timeout') else None)
    return plan
def validate_environment():
    e=read(ROOT/'environment.json')
    assert e['python']==sys.version and e['platform']==platform.platform() and e['SIGCHLD']==0
    assert e['executable_resolved']==str(Path(sys.executable).resolve()) and sha(e['executable_resolved'])==e['binary_sha256']
def expected(cfg,r):
    if r['ownership_errors'] or not r['kernel_final']:return False
    name=cfg['name'];rc=r['kernel_final']['returncode'];reasons=r['reasons']
    if name in ('normal_exit','cpu_work'):return rc==0 and not reasons and r['classification']=='ordinary_exit'
    if name=='nonzero_exit':return rc==7 and not reasons and r['classification']=='nonzero_or_signal_exit'
    if name=='final_CPU_over_budget':return rc==0 and reasons==['cpu_limit'] and not r['signals'] and not r['ps_queries']
    if name=='exit_candidate_confirmed':return rc==0 and not reasons and r['controlled_injection'] is not None and r['terminal_telemetry_unavailable']
    if name=='setup_failure':return reasons==['setup_or_runner_error'] and stop_valid(r,-15)
    if name=='live_counter_reset':return reasons==['monitor_invalid: Invalid live telemetry'] and stop_valid(r,-15)
    if name=='exit_candidate_timeout':return reasons==['exit_confirmation_timeout'] and stop_valid(r,-15)
    reason={'parent_wall':'wall_limit','parent_CPU':'cpu_limit','parent_RSS':'rss_limit','TERM_to_KILL':'wall_limit'}[name]
    return reasons==[reason] and stop_valid(r,-9 if name=='TERM_to_KILL' else -15)
def freeze():
    assert not (ROOT/'frozen.json').exists()
    review=read(ROOT/'PREFLIGHT.json')
    assert review['approved'] and review['scope']=='stdlib_runner_only' and read(ROOT/'offline_checks.json')['passed']
    validate_plan();validate_environment()
    offline=read(ROOT/'offline_checks.json')
    for name,digest in offline['source_hashes'].items():assert sha(ROOT/name)==digest,name
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp')]
    paths += [ROOT.parent/'adapter_entry_2026-11-18/manifest.json',ROOT.parent/'reference_integration_protocol_2026-11-18/manifest.json']
    env=read(ROOT/'environment.json');assert sha(env['executable_resolved'])==env['binary_sha256']
    paths.append(Path(env['executable_resolved']))
    save(ROOT/'frozen.json',dict(files={str(p.resolve()):sha(p) for p in paths},scope='stdlib_runner_only',max_workers=12,optimizer_calls=0))
    print(json.dumps(dict(frozen=True,sha256=sha(ROOT/'frozen.json'))))
def execute():
    started=time.monotonic();assert not (ROOT/'runs').exists(),'No resume/retry of a partial or complete run'
    frozen=read(ROOT/'frozen.json')
    for path,digest in frozen['files'].items():assert sha(path)==digest,path
    plan=validate_plan();validate_environment();rows=[];(ROOT/'runs').mkdir();stop=None
    for file in plan['configs']:
        if time.monotonic()-started+8>90:stop='admission_budget';break
        cfg=read(ROOT/'configs'/file)
        try:
            result=run(ROOT/'configs'/file);ok=bool(expected(cfg,result))
            row=dict(name=cfg['name'],passed=ok,pid=result['pid'],classification=result['classification'],
                spawned=True,returncode=result['kernel_final']['returncode'] if result['kernel_final'] else None,reasons=result['reasons'])
        except BaseException as exc:
            launch=dict(runner.LAST_LAUNCH) if runner.LAST_LAUNCH.get('nonce')==cfg['nonce'] and runner.LAST_LAUNCH.get('name')==cfg['name'] else {}
            row=dict(name=cfg['name'],passed=False,infrastructure_error=f'{type(exc).__name__}: {exc}',
                spawned=bool(launch.get('spawn_returned')),known_launch=launch)
        rows.append(row);save(ROOT/'progress.json',dict(rows=rows));print(json.dumps(row),flush=True)
        if not row['passed']:stop='unexpected_outcome';break
    elapsed=time.monotonic()-started;passed=len(rows)==12 and all(r['passed'] for r in rows) and elapsed<=90
    save(ROOT/'execution.json',dict(passed=passed,rows=rows,controller_seconds=elapsed,stop=stop,
        workers_started=sum(r['spawned'] for r in rows),launch_attempts=len(rows),optimizer_calls=0,decoder_calls=0,
        research_cases=0,physical_samples=0,frozen_sha256=sha(ROOT/'frozen.json')))
    paths=[p for p in (ROOT/'runs').rglob('*') if p.is_file()]+[ROOT/'execution.json',ROOT/'progress.json']
    save(ROOT/'output_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in paths}))
    print(json.dumps(dict(passed=passed,workers=len(rows),seconds=elapsed)),flush=True)
if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('configure','freeze','run'):raise SystemExit('configure|freeze|run')
    {'configure':configure,'freeze':freeze,'run':execute}[sys.argv[1]]()
