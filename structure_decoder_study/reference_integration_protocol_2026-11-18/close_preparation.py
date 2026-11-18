"""Freeze/check PREPARATION ONLY. No optimizer, runtime monitor or OS query."""
import ast,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
CACHE={}
def read(p):return json.loads(p.read_text())
def sha(p):
    p=p.resolve()
    if p not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as stream:
            while block:=stream.read(1048576):h.update(block)
        CACHE[p]=h.hexdigest()
    return CACHE[p]
def write(p,value):
    assert not p.exists(),'Preserve '+str(p)
    p.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def manifest(p):
    value=read(p)
    for name,digest in value['files'].items():assert sha(p.parent/name)==digest,(str(p),name)
    return len(value['files'])
def freeze():
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp')]
    assert not (ROOT/'frozen.json').exists()
    paths.append(STUDY/'STATUS_2026-11-18_REFERENCE_INTEGRATION_PROTOCOL.md')
    for name in ('reference_probe_2026-11-18','timeout_repair_2026-11-18','timeout_repair_v2_2026-11-18'):
        paths.append(STUDY/name/'manifest.json')
    spec=read(ROOT/'protocol.json');environment=read(ROOT/'environment.json')
    paths += [Path(p) for p in spec['reference_input_hashes']]
    paths += [Path(v['path']) for v in environment['imported_files'].values()]
    paths += [Path(environment['interpreter_resolved']),Path(spec['shared_adapter_source']['path']),Path(spec['shared_signal_guard']['path'])]
    write(ROOT/'frozen.json',dict(scope='reviewed_preparation_only',native_entry_launch_authorized=False,research_launch_authorized=False,
        files={str(p.resolve()):sha(p) for p in paths}))
    print(json.dumps(dict(preparation_frozen=True,files=len(read(ROOT/'frozen.json')['files']),sha256=sha(ROOT/'frozen.json'))))
def check():
    started=time.monotonic();frozen=read(ROOT/'frozen.json')
    for p,digest in frozen['files'].items():assert sha(Path(p))==digest,p
    spec=read(ROOT/'protocol.json');checks=read(ROOT/'policy_checks.json');env=read(ROOT/'environment.json')
    for name,digest in checks['source_hashes'].items():assert sha(ROOT/name)==digest,name
    for name,digest in spec['reference_input_hashes'].items():assert sha(Path(name))==digest,name
    for record in env['imported_files'].values():assert sha(Path(record['path']))==record['sha256']
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(),str(p))
    assert checks['passed'] and checks['count']==77 and len(checks['checks'])==77
    assert not checks['actual_native_adapter_integration_validated'] and not checks['platform_process_state_behavior_validated']
    assert checks['optimizer_api_attempts']==checks['experimental_workers']==checks['OS_queries']==checks['research_cases']==0
    assert not spec['native_entry_launch_authorized'] and not spec['research_launch_authorized'] and not spec['scientific_value_gate_resolved']
    assert len(spec['entry']['order'])==spec['entry']['max_children']==13 and spec['entry']['max_optimizer_attempts']==7
    assert spec['entry']['remaining_before_child']==11 and len(spec['optional_research_cases'])==2
    assert spec['shared_adapter_source']['functions']==['build_model','model_witness','validate_incumbent']
    assert spec['shared_adapter_source']['new_transport_must_save_raw_before_warning_or_status_interpretation']
    for case in spec['reference_cases']:
        assert (Path(spec['reference_inputs_root'])/case['input_npz']).exists()
    assert spec['solver_options']==read(STUDY/'reference_probe_2026-11-18/frozen.json')['solver_options']
    prior=read(STUDY/'reference_probe_2026-11-18/audit_result.json')['previous_manifests_verified']
    for name,digest in prior.items():
        p=STUDY/name;assert sha(p)==digest,name
        manifest(p)
    assert len(prior)==23
    current={name:manifest(STUDY/name/'manifest.json') for name in ('reference_probe_2026-11-18','timeout_repair_2026-11-18','timeout_repair_v2_2026-11-18')}
    report=dict(passed=True,date='2026-11-18',scope='preparation_and_integrity_only',
        reviewed_preparation_complete=True,deterministic_policy_checks=77,
        native_adapter_implemented=False,native_adapter_validated=False,research_launch_authorized=False,
        native_entry_launch_authorized=False,new_optimizer_attempts=0,new_experimental_workers=0,
        new_research_cases=0,new_BP_OSD_LSD_calls=0,new_model_fits=0,new_physical_shots=0,
        earlier_result_manifests_verified=23,current_prior_manifest_file_counts=current,
        unique_files_hashed=len(CACHE),all_prior_results_unchanged=True,prior_research_cases_still_inconclusive=True,
        scientific_options_unchanged=True,solver_transport_warning_gap_identified=True,
        frozen_sha256=sha(ROOT/'frozen.json'),AI_supervisor_review_sha256=sha(ROOT/'SUPERVISOR_REVIEW.md'),
        wall_seconds=time.monotonic()-started)
    write(ROOT/'final_checks.json',report)
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp')]
    entries={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    status=STUDY/'STATUS_2026-11-18_REFERENCE_INTEGRATION_PROTOCOL.md'
    entries['../'+status.name]=sha(status)
    write(ROOT/'manifest.json',dict(status='reviewed_preparation_complete_execution_not_performed',files=entries))
    print(json.dumps(report,indent=2))
    print(json.dumps(dict(whole_manifest_files=len(entries),manifest_sha256=sha(ROOT/'manifest.json'))))
if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('freeze','check'):raise SystemExit('Usage: close_preparation.py freeze|check')
    {'freeze':freeze,'check':check}[sys.argv[1]]()
