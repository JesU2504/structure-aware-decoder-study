"""Integrity closure of a FAILED entry; no solver or experimental worker."""
import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STUDY=ROOT.parent;CACHE={}
def read(p):return json.loads(p.read_text())
def sha(p):
    p=p.resolve()
    if p not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as f:
            while block:=f.read(1048576):h.update(block)
        CACHE[p]=h.hexdigest()
    return CACHE[p]
def verify(p):
    data=read(p)
    for name,digest in data['files'].items():assert sha(p.parent/name)==digest,(str(p),name)
    return len(data['files'])
def main():
    target=ROOT/'final_checks.json';assert not target.exists()
    started=time.monotonic();frozen=read(ROOT/'frozen.json')
    for path,digest in frozen['files'].items():assert sha(Path(path))==digest,path
    outputs=verify(ROOT/'output_manifest.json')
    reference=STUDY/'reference_probe_2026-11-18'
    prior=read(reference/'audit_result.json')['previous_manifests_verified']
    for name,digest in prior.items():
        p=STUDY/name;assert sha(p)==digest,name
        verify(p)
    assert len(prior)==23
    current={name:verify(STUDY/name/'manifest.json') for name in ('reference_probe_2026-11-18','timeout_repair_2026-11-18',
        'timeout_repair_v2_2026-11-18','reference_integration_protocol_2026-11-18')}
    failure=read(ROOT/'failure_accounting.json');result=read(ROOT/'entry_result.json')
    assert failure['failure_accounting_passed'] and not failure['native_entry_passed'] and result['passed'] is False
    assert failure['optimizer_api_attempts']==failure['optimizer_returns_persisted']==failure['experimental_workers']==1
    assert failure['unattempted_count']==12 and failure['cumulative_optimizer_api_attempts']==19
    assert not failure['acceptance_criteria_changed'] and not failure['unknown_state_accepted_as_terminal']
    assert not (ROOT/'audit_result.json').exists()
    for name,digest in read(ROOT/'offline_checks.json')['source_hashes'].items():assert sha(ROOT/name)==digest,name
    inventory=subprocess.run(['ps','-axo','pid=,command='],capture_output=True,text=True,timeout=2,check=True).stdout
    needle=str((ROOT/'worker.py').resolve())
    active=[s for s in inventory.splitlines() if needle in s]
    assert not active,active
    report=dict(integrity_checks_passed=True,native_entry_passed=False,date='2026-11-18',
        scope='failed_bounded_native_entry',frozen_files_verified=len(frozen['files']),raw_outputs_verified=outputs,
        earlier_result_manifests_verified=23,additional_prior_manifest_file_counts=current,unique_files_hashed=len(CACHE),
        actual_optimizer_api_attempts=1,optimizer_returns_persisted=1,workers_started=1,unattempted_controls=12,
        cumulative_optimizer_api_attempts=19,new_research_case_calls=0,new_BP_OSD_LSD_calls=0,new_model_fits=0,new_physical_shots=0,
        earlier_data_and_sources_unchanged=True,acceptance_criteria_changed=False,owned_child_reaped=True,
        no_matching_worker_processes=True,prior_research_cases_still_inconclusive=True,
        frozen_sha256=sha(ROOT/'frozen.json'),supervisor_postcheck_sha256=sha(ROOT/'POSTCHECK.md'),wall_seconds=time.monotonic()-started)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
