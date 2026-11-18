"""Configure/freeze/run only the thirteen prospective synthetic entry controls."""
from __future__ import annotations
import ast,hashlib,json,sys,time,traceback,uuid
from pathlib import Path
sys.dont_write_bytecode=True
from result_guard import atomic_json
ROOT=Path(__file__).resolve().parent
PREP=ROOT.parent/'reference_integration_protocol_2026-11-18'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def function_source(path,name):
    source=Path(path).read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return '\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])

def configure():
    assert not (ROOT/'frozen.json').exists(),'Frozen: no configuration changes'
    spec=read(ROOT/'prepared_protocol.json');fixtures=read(ROOT/'entry_fixtures.json')['fixtures']
    assert spec['entry']['max_children']==13 and spec['entry']['max_optimizer_attempts']==7
    run_id=str(uuid.uuid4());configs=[]
    (ROOT/'configs').mkdir(exist_ok=True)
    modes={n:'parity' for n in [r['name'] for r in fixtures]}
    modes.update(timeout_none='MIS',timeout_incumbent='MIS',signal_during_call='MIS',signal_during_persistence='mock',
        parent_CPU='cpu',parent_wall='wall',parent_RSS='rss',observed_terminal_Z='terminal',malformed_active_monitor='fault')
    source_identity={n:sha(ROOT/n) for n in ('worker.py','transport.py','model_helpers.py','result_guard.py','accounting_policy.py')}
    for index,name in enumerate(spec['entry']['order']):
        mode=modes[name];limits=dict(cpu=10.,wall=8.,rss=1073741824);OS_limits=[10,12]
        if mode=='cpu':limits['cpu']=3.;OS_limits=[1,3]
        if mode=='wall':limits['wall']=.15
        if mode=='rss':limits['rss']=67108864
        cfg=dict(scope='synthetic_entry_only',name=name,mode=mode,limits=limits,OS_cpu_limits=OS_limits,
            output=str((ROOT/'entry'/name).resolve()),identity=dict(run_id=run_id,name=name,index=index,
                prepared_protocol_sha256=sha(ROOT/'prepared_protocol.json'),sources=source_identity),
            inject_signal=name in ('signal_during_call','signal_during_persistence'))
        if mode=='parity':
            toy=next(r for r in fixtures if r['name']==name)
            cfg.update(fixture=toy,solver_options=spec['entry']['parity_options'],expected_status=toy['expected_solver_status'],
                expected_forwarded_options=['threads','random_seed','mip_feasibility_tolerance'])
        elif mode in ('MIS','mock'):
            cfg.update(n=6 if mode=='mock' else 200,seed=2026111801,expected_incumbent=name!='timeout_none',
                solver_options=dict(spec['entry']['MIS']['options'],time_limit=0. if name=='timeout_none' else .15),
                expected_forwarded_options=['threads','random_seed'])
        elif mode=='rss':cfg['committed_bytes']=100663296
        path=ROOT/'configs'/f'{index:02d}_{name}.json';atomic_json(path,cfg);configs.append(path.name)
    atomic_json(ROOT/'execution_plan.json',dict(scope='synthetic_native_entry_only',real_research_launch_supported=False,
        run_id=run_id,config_files=configs,case_names=spec['entry']['order'],max_children=13,max_optimizer_attempts=7,
        controller_wall_acceptance_ceiling=120.,remaining_before_child=11.,retries=0,calibration_calls=0))
    print(json.dumps(dict(configured=True,children=13,optimizer_attempts_planned=7,optimizer_attempts_started=0)))

def expected(cfg,process,final):
    state=process['accounting'];name=cfg['name'];mode=cfg['mode']
    if state['phase']!='REAPED' or process['monitor_failure'] is not None:return False
    reasons=state['censor_reasons']
    if mode in ('cpu','wall','rss','fault'):
        if final is not None or not stop_control_matches(process):return False
        if mode=='fault':return len(reasons)==1 and reasons[0].startswith('monitor_invalid: Invalid RSS') and process['controlled_fault'] is not None
        wanted={'cpu':'cpu_limit','wall':'wall_limit','rss':'rss_limit'}[mode]
        return reasons==[wanted]
    if reasons or process['returncode']!=0 or not isinstance(final,dict):return False
    if not final.get('finalized') or not final.get('handler_restored') or not final.get('raw_payload_complete'):return False
    if mode=='terminal':
        permission=process['exit_permission']
        if not permission:return False
        fields=permission['single_query']['stdout'].split()
        return len(fields)==4 and fields[1][0]=='Z' and state['cpu_highwater']>0 and not final['signals']
    status=cfg['expected_status'] if mode=='parity' else 1
    if final['solver_status']!=status:return False
    want=cfg['fixture']['minimum'] is not None if mode=='parity' else cfg['expected_incumbent']
    if final['has_incumbent']!=want:return False
    if want and final['incumbent_valid'] is not True:return False
    if cfg['inject_signal']:
        return bool(final['signals']) and process['controlled_signal'] is not None
    return not final['signals']

def stop_control_matches(process):
    actions=process['termination_actions'];rc=process['returncode']
    if not actions or actions[0]['signum']!=15:return False
    if any('wait_error' in a or not a.get('signal_API_returned') for a in actions):return False
    if rc==-15:return len(actions)==1 and actions[0]['wait_returncode']==-15 and not actions[0]['wait_timed_out']
    return (rc==-9 and len(actions)==2 and actions[1]['signum']==9 and actions[0]['wait_timed_out']
        and actions[0]['wait_returncode'] is None and actions[1]['requested_at']>=actions[0]['wait_finished']
        and actions[1]['wait_returncode']==-9 and not actions[1]['wait_timed_out'])

def validate_configs(spec,plan):
    toys={f['name']:f for f in read(ROOT/'entry_fixtures.json')['fixtures']}
    modes={name:'parity' for name in toys}
    modes.update(timeout_none='MIS',timeout_incumbent='MIS',signal_during_call='MIS',signal_during_persistence='mock',
        parent_CPU='cpu',parent_wall='wall',parent_RSS='rss',observed_terminal_Z='terminal',malformed_active_monitor='fault')
    for index,(name,filename) in enumerate(zip(spec['entry']['order'],plan['config_files'])):
        cfg=read(ROOT/'configs'/filename);mode=modes[name]
        assert cfg['name']==cfg['identity']['name']==name and cfg['mode']==mode
        assert cfg['identity']['index']==index and cfg['identity']['run_id']==plan['run_id'] and cfg['scope']=='synthetic_entry_only'
        normal=spec['entry']['normal_child'];limit=dict(cpu=normal['cpu_threshold'],wall=normal['wall_threshold'],rss=normal['rss_bytes'])
        oslimit=normal['requested_OS_cpu_limits']
        if mode=='cpu':limit['cpu']=3.;oslimit=[1,3]
        if mode=='wall':limit['wall']=.15
        if mode=='rss':limit['rss']=67108864
        assert cfg['limits']==limit and cfg['OS_cpu_limits']==oslimit
        assert cfg['output']==str((ROOT/'entry'/name).resolve())
        assert cfg['inject_signal']==(name in ('signal_during_call','signal_during_persistence'))
        if mode=='parity':
            assert cfg['fixture']==toys[name] and cfg['expected_status']==toys[name]['expected_solver_status']
            assert cfg['solver_options']==spec['entry']['parity_options']
            assert set(cfg['expected_forwarded_options'])==set(spec['shared_adapter_source']['expected_forwarded_options_by_mode']['parity'])
        elif mode in ('MIS','mock'):
            assert cfg['n']==(6 if mode=='mock' else 200) and cfg['seed']==spec['entry']['MIS']['seed']
            assert cfg['solver_options']==dict(spec['entry']['MIS']['options'],time_limit=0. if name=='timeout_none' else .15)
            assert cfg['expected_incumbent']==(name!='timeout_none')
            assert set(cfg['expected_forwarded_options'])==set(spec['shared_adapter_source']['expected_forwarded_options_by_mode']['MIS'])
        if mode=='rss':assert cfg['committed_bytes']==100663296

def freeze():
    assert not (ROOT/'frozen.json').exists(),'Preserve freeze'
    review=read(ROOT/'PREFLIGHT.json');assert review['approved'] and review['scope']=='synthetic_native_entry_only'
    spec=read(ROOT/'prepared_protocol.json');plan=read(ROOT/'execution_plan.json')
    assert sha(ROOT/'prepared_protocol.json')==sha(PREP/'protocol.json')
    assert plan['case_names']==spec['entry']['order'] and len(plan['config_files'])==13
    validate_configs(spec,plan)
    for name in ('accounting_policy.py','check_policy.py','environment.json','entry_fixtures.json'):
        assert sha(ROOT/name)==sha(PREP/name),name
    assert sha(ROOT/'result_guard.py')==spec['shared_signal_guard']['sha256']
    for name in spec['shared_adapter_source']['functions']:
        assert function_source(ROOT/'model_helpers.py',name)==function_source(spec['shared_adapter_source']['path'],name),name
    assert 'INT_TOL=1e-7' in (ROOT/'model_helpers.py').read_text()
    offline=read(ROOT/'offline_checks.json');assert offline['passed']
    for name,digest in offline['source_hashes'].items():assert sha(ROOT/name)==digest,name
    assert read(ROOT/'policy_checks.json')['passed']
    for config_file in plan['config_files']:
        cfg=read(ROOT/'configs'/config_file)
        for name,digest in cfg['identity']['sources'].items():assert sha(ROOT/name)==digest,name
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp')]
    paths += [PREP/'manifest.json',PREP/'frozen.json',ROOT.parent/'reference_probe_2026-11-18/manifest.json',
        ROOT.parent/'timeout_repair_v2_2026-11-18/manifest.json']
    for v in read(ROOT/'environment.json')['imported_files'].values():
        assert sha(v['path'])==v['sha256'];paths.append(Path(v['path']))
    env=read(ROOT/'environment.json');assert sha(env['interpreter_resolved'])==env['interpreter_binary_sha256']
    paths.append(Path(env['interpreter_resolved']))
    atomic_json(ROOT/'frozen.json',dict(scope='synthetic_native_entry_only',research_launch_authorized=False,
        files={str(p.resolve()):sha(p) for p in paths},max_children=13,max_optimizer_attempts=7,
        controller_wall_acceptance_ceiling=120.,remaining_before_child=11.,run_id=plan['run_id']))
    print(json.dumps(dict(frozen=True,files=len(read(ROOT/'frozen.json')['files']),sha256=sha(ROOT/'frozen.json'))))

def run():
    started=time.monotonic()
    assert not (ROOT/'entry').exists() and not (ROOT/'entry_result.json').exists(),'Preserve partial/full attempts; no resume or retries'
    frozen=read(ROOT/'frozen.json')
    for path,digest in frozen['files'].items():assert sha(path)==digest,path
    import monitor
    plan=read(ROOT/'execution_plan.json');rows=[];(ROOT/'entry').mkdir()
    atomic_json(ROOT/'run_started.json',dict(run_id=plan['run_id'],started_monotonic=started,frozen_sha256=sha(ROOT/'frozen.json')))
    stop=None
    for filename in plan['config_files']:
        if time.monotonic()-started+11.>120.:stop='insufficient_remaining_controller_budget';break
        cfg=read(ROOT/'configs'/filename)
        try:
            process,final=monitor.watch(ROOT/'configs'/filename)
            accepted=bool(expected(cfg,process,final))
            row=dict(name=cfg['name'],config_file=filename,expected_control_outcome_observed=accepted,
                spawn_returned=True,returncode=process['returncode'],censor_reasons=process['accounting']['censor_reasons'])
        except BaseException as exc:
            identity=dict(cfg['identity'],config_sha256=sha(ROOT/'configs'/filename))
            spawn=dict(monitor.LAST_SPAWN) if monitor.LAST_SPAWN.get('identity')==identity else dict(spawn_returned=False)
            row=dict(name=cfg['name'],config_file=filename,expected_control_outcome_observed=False,
                spawn_returned=bool(spawn.get('spawn_returned')),owned_spawn=spawn,returncode=None,
                censor_reasons=['watch_exception'],exception=f'{type(exc).__name__}: {exc}',traceback=traceback.format_exc())
            accepted=False
        rows.append(row);atomic_json(ROOT/'entry_progress.json',dict(rows=rows,controller_wall_seconds=time.monotonic()-started))
        print(json.dumps(row),flush=True)
        if not accepted:stop='unexpected_entry_outcome';break
    elapsed=time.monotonic()-started
    attempts=len(list((ROOT/'entry').rglob('optimizer_attempt.json')))
    malformed=0
    for journal in (ROOT/'entry').rglob('native_journal.jsonl'):
        for line in journal.read_text().splitlines():
            try:json.loads(line)
            except json.JSONDecodeError:malformed+=1
    passed=len(rows)==13 and all(r['expected_control_outcome_observed'] for r in rows) and attempts==7 and elapsed<=120. and not malformed
    atomic_json(ROOT/'entry_result.json',dict(passed=passed,rows=rows,stop_reason=stop,controller_wall_seconds=elapsed,
        optimizer_api_attempts=attempts,experimental_workers=sum(r['spawn_returned'] for r in rows),
        worker_launch_attempts=len(rows),malformed_native_journal_lines=malformed,real_research_calls=0,physical_shots=0,
        frozen_sha256=sha(ROOT/'frozen.json')))
    paths=[p for p in (ROOT/'entry').rglob('*') if p.is_file()]+[ROOT/'entry_result.json',ROOT/'run_started.json',ROOT/'entry_progress.json']
    atomic_json(ROOT/'output_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in paths}))
    print(json.dumps(dict(entry_passed=passed,attempts=attempts,workers=len(rows),controller_wall_seconds=elapsed)),flush=True)

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('configure','freeze','run'):raise SystemExit('Usage: control.py configure|freeze|run')
    {'configure':configure,'freeze':freeze,'run':run}[sys.argv[1]]()
