"""Check newer saved evidence, without decoder, optimizer or worker invocations.

This is a public-mirror verifier, not a re-signing of private-path experiment freezes.
"""
import hashlib,json,math,os
from pathlib import Path
import numpy as np
import scipy.sparse as sp
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'structure_decoder_study'
def read(path):return json.loads(Path(path).read_text())
def local(path):
    text=str(path).removeprefix('<WORKSPACE>/')
    assert not text.startswith('/') and '..' not in Path(text).parts
    return ROOT/text
def main():
    export=read(ROOT/'PUBLIC_EXPORT.json')
    for name,record in export['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==record['sha256'],name
    base=STUDY/'natural_noise_reproduction_2026-11-17'
    h=sp.load_npz(base/'entry/H.npz').astype(np.int64);l=sp.load_npz(base/'entry/L.npz').astype(np.int64)
    weights=np.log(1/np.load(base/'entry/priors.npy'))
    head=STUDY/'headroom_cached_order_2026-11-17';diag=STUDY/'candidate_class_diagnosis_2026-11-18'
    repaired=[];remaining=[];regressed=[];covered=0;cases=read(head/'selection.json')
    for case in cases:
        cid=case['case_id'];cached=np.load(local(case['cached_npz']));saved=np.load(head/'search'/f'{cid:04d}.npz')
        x=saved['correction_full'].astype(np.int64)
        assert np.array_equal(h@x%2,cached['syndrome'])
        assert np.array_equal(saved['correction_500'],x) and np.array_equal(saved['correction_1000'],x)
        logical=l@x%2;correct=bool(np.array_equal(logical,cached['actual']))
        if case['role']=='failure':(repaired if correct else remaining).append(cid)
        elif not correct:regressed.append(cid)
        diagnosis=read(diag/'cases'/f'{cid:04d}.json');summary=diagnosis['summary']
        packed=sum(int(bit)<<i for i,bit in enumerate(cached['actual']))
        selected=sum(int(bit)<<i for i,bit in enumerate(logical))
        assert summary['true_logical_class']==packed and summary['selected_logical_class']==selected
        assert summary['selected_matches_truth']==correct
        assert sum(c['count'] for c in diagnosis['classes'])==10447
        own=next(c for c in diagnosis['classes'] if c['logical_class']==packed)
        assert own['count']==summary['true_class_count']>0;covered+=1
        score=math.fsum(float(w) for w,bit in zip(weights,x) if bit)
        assert abs(score-summary['selected_score'])<1e-8
        position=own['first_exact_raw_minimum_position'];candidate=saved['baseline'].copy()
        if position:
            gate=np.load(head/'gates'/f'{cid:04d}.npz')
            candidate[gate['pivot_cols']]^=saved['rf'][:,position-1]
            candidate[int(saved['free'][position-1])]=1
        assert np.array_equal(h@candidate.astype(np.int64)%2,cached['syndrome'])
        assert np.array_equal(l@candidate.astype(np.int64)%2,cached['actual'])
        cost=math.fsum(float(w) for w,bit in zip(weights,candidate) if bit)
        assert abs(cost-own['minimum_raw_score'])<1e-8
    assert len(cases)==24 and len(repaired)==10 and sorted(remaining)==[131,228] and not regressed and covered==24
    reference=read(STUDY/'reference_probe_2026-11-18/final_checks.json')
    assert reference['real_optimizer_calls_started']==2 and reference['real_optimizer_calls_returned_to_python']==0
    failed=read(STUDY/'adapter_entry_2026-11-18/failure_accounting.json')
    assert failed['native_entry_passed'] is False and failed['unattempted_count']==12 and failed['optimizer_api_attempts']==1
    runner=STUDY/'runner_repair_2026-11-18';execution=read(runner/'execution.json');audit=read(runner/'audit_result.json')
    assert execution['passed'] and audit['passed'] and len(execution['rows'])==12
    assert execution['workers_started']==12 and audit['optimizer_calls']==audit['decoder_calls']==0
    for row in execution['rows']:
        result=read(runner/'runs'/row['name']/'result.json');final=result['kernel_final'];usage=final['usage']
        assert row['passed'] and final['pid']==result['pid'] and not result['ownership_errors']
        assert final['returncode']==os.waitstatus_to_exitcode(final['raw_status'])
        assert usage['total_cpu']==usage['user_cpu']+usage['system_cpu']
        assert usage['peak_rss_bytes']==usage['native_peak_rss']*(1 if usage['native_RSS_unit']=='bytes' else 1024)
        assert sum(e.get('returned_pid')==result['pid'] for e in result['kernel_events'])==1
    print(json.dumps(dict(passed=True,export_files=len(export['files']),headroom_cases_checked=24,
        failure_cases_repaired_by_known_1FV=10,remaining_selected_failures=[131,228],selected_control_regressions=0,
        correct_class_representatives_checked=24,reported_class_tables_checked=24,
        exhaustive_250728_member_audit_repeated=False,failed_entry_preserved=True,runner_controls_checked=12,
        new_decoder_calls=0,new_optimizer_calls=0,new_workers=0)))
if __name__=='__main__':main()
