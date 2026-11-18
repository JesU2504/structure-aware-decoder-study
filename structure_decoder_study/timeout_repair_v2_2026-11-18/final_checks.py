"""Read-only integrity/accounting closure; no optimizer or scientific execution."""
from __future__ import annotations
import hashlib,json,subprocess,time
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
def verify(p,absolute=False):
    manifest=read(p)
    for name,digest in manifest['files'].items():
        target=Path(name) if absolute else p.parent/name
        assert sha(target)==digest,(p,name)
    return len(manifest['files'])
def main():
    target=ROOT/'final_checks.json';assert not target.exists(),'Preserve checks'
    started=time.monotonic()
    frozen_count=verify(ROOT/'frozen.json',True)
    supplemental_count=verify(ROOT/'audit_adjudication_frozen.json',True)
    output_count=verify(ROOT/'output_manifest.json')
    old=STUDY/'timeout_repair_2026-11-18'
    v1_count=verify(old/'manifest.json')
    reference=STUDY/'reference_probe_2026-11-18'
    reference_count=verify(reference/'manifest.json')
    prior=read(reference/'audit_result.json')['previous_manifests_verified']
    for name,digest in prior.items():
        manifest=STUDY/name;assert sha(manifest)==digest,name
        verify(manifest)
    assert len(prior)==23
    assert read(old/'V1_OUTCOME.json')['audit_passed'] is False
    assert read(ROOT/'audit_initial_failure.json')['status']=='frozen_audit_failed'
    assert not (ROOT/'audit_result.json').exists()
    audit=read(ROOT/'audit_adjudication_result.json')
    assert audit['passed'] and audit['original_frozen_audit_passed'] is False and audit['post_hoc_adjudication'] is True
    assert audit['cumulative_optimizer_api_attempts']==12 and audit['cumulative_children']==20
    assert audit['real_research_calls']==audit['physical_shots']==audit['additional_optimizer_api_attempts']==0
    assert audit['cumulative_controller_wall_seconds']<=120
    assert len(audit['checks'])==9 and all(c['passed'] for c in audit['checks'])
    for name in ('worker.py','result_guard.py'):assert sha(ROOT/name)==sha(old/name)
    # Filter the inventory before writing it; do not retain unrelated processes.
    inventory=subprocess.run(['ps','-axo','pid=,command='],capture_output=True,text=True,check=True,timeout=2).stdout
    needles=[str((ROOT/'worker.py').resolve()),str((old/'worker.py').resolve())]
    running=[line for line in inventory.splitlines() if any(n in line for n in needles)]
    assert not running,running
    report=dict(passed=True,date='2026-11-18',scope='integrity_and_accounting_closure_only',
        original_V1_audit_passed=False,original_V2_frozen_audit_passed=False,
        reviewed_post_hoc_supplemental_audit_passed=True,qualified_controlled_engineering_acceptance=True,
        V2_frozen_input_files=frozen_count,supplemental_frozen_input_files=supplemental_count,
        V2_raw_output_files=output_count,V1_manifest_files=v1_count,reference_manifest_files=reference_count,
        earlier_result_manifests_verified=len(prior),unique_files_hashed=len(CACHE),
        cumulative_synthetic_optimizer_api_attempts=12,cumulative_engineering_children=20,
        cumulative_controller_wall_seconds=audit['cumulative_controller_wall_seconds'],
        final_check_optimizer_api_attempts=0,new_research_case_calls=0,new_physical_shots=0,
        no_matching_test_worker_processes=True,all_sources_and_raw_results_unchanged=True,
        prior_research_cases_still_inconclusive=True,historical_signal_origin_established=False,
        final_check_wall_seconds=time.monotonic()-started,
        supervisor_postcheck_sha256=sha(ROOT/'POSTCHECK.md'))
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
