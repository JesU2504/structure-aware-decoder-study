"""Final integrity/count closure only; no experimental worker or solver."""
import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STUDY=ROOT.parent;CACHE={}
def read(p):return json.loads(p.read_text())
def sha(p):
    p=p.resolve()
    if p not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as f:
            while chunk:=f.read(1048576):h.update(chunk)
        CACHE[p]=h.hexdigest()
    return CACHE[p]
def verify(p):
    d=read(p)
    for name,digest in d['files'].items():assert sha(p.parent/name)==digest,(str(p),name)
    return len(d['files'])
def main():
    target=ROOT/'final_checks.json';assert not target.exists();started=time.monotonic()
    frozen=read(ROOT/'frozen.json')
    for p,digest in frozen['files'].items():assert sha(Path(p))==digest,p
    outputs=verify(ROOT/'output_manifest.json')
    reference=STUDY/'reference_probe_2026-11-18'
    prior=read(reference/'audit_result.json')['previous_manifests_verified']
    for name,digest in prior.items():
        p=STUDY/name;assert sha(p)==digest,name;verify(p)
    earlier={name:verify(STUDY/name/'manifest.json') for name in ('reference_probe_2026-11-18','timeout_repair_2026-11-18',
        'timeout_repair_v2_2026-11-18','reference_integration_protocol_2026-11-18','adapter_entry_2026-11-18')}
    execution=read(ROOT/'execution.json');audit=read(ROOT/'audit_result.json');offline=read(ROOT/'offline_checks.json')
    assert execution['passed'] and audit['passed'] and offline['passed'] and offline['count']==32
    assert execution['workers_started']==12 and len(audit['checks'])==12 and all(c['passed'] for c in audit['checks'])
    assert audit['optimizer_calls']==audit['decoder_calls']==audit['research_cases']==audit['physical_samples']==0
    for name,digest in offline['source_hashes'].items():assert sha(ROOT/name)==digest,name
    inventory=subprocess.run(['ps','-axo','pid=,command='],capture_output=True,text=True,check=True,timeout=2).stdout
    assert not [s for s in inventory.splitlines() if str(ROOT/'fixture.py') in s]
    report=dict(passed=True,scope='bounded_stdlib_runner_core',offline_checks=32,actual_workers=12,
        optimizer_calls=0,decoder_calls=0,research_cases=0,physical_samples=0,cumulative_optimizer_attempts_unchanged=19,
        frozen_input_files=len(frozen['files']),output_files=outputs,earlier_result_manifests_verified=len(prior),
        additional_prior_manifests_verified=earlier,all_prior_sources_and_data_unchanged=True,
        no_matching_fixture_processes=True,native_optimizer_integration_validated=False,
        frozen_sha256=sha(ROOT/'frozen.json'),supervisor_review_sha256=sha(ROOT/'POSTCHECK.md'),
        unique_files_hashed=len(CACHE),wall_seconds=time.monotonic()-started)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
