"""Audit the FAILED entry and its one saved toy artifact. No rerun or pass exception.

Uses only the frozen independent artifact validator, never runtime/model helpers.
The original success-audit main is deliberately not executed on a failed suite.
"""
import hashlib,json,math
from pathlib import Path
import audit as artifact_audit
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    target=ROOT/'failure_accounting.json';assert not target.exists(),'Preserve failure audit'
    frozen=read(ROOT/'frozen.json')
    for p,digest in frozen['files'].items():assert sha(p)==digest,p
    outputs=read(ROOT/'output_manifest.json')
    for p,digest in outputs['files'].items():assert sha(ROOT/p)==digest,p
    result=read(ROOT/'entry_result.json');plan=read(ROOT/'execution_plan.json')
    assert result['passed'] is False and result['stop_reason']=='unexpected_entry_outcome'
    assert result['experimental_workers']==result['worker_launch_attempts']==result['optimizer_api_attempts']==1
    assert result['malformed_native_journal_lines']==0 and result['controller_wall_seconds']<=120.
    assert len(result['rows'])==1 and result['rows'][0]['expected_control_outcome_observed'] is False
    cfg_path=ROOT/'configs'/plan['config_files'][0];cfg=read(cfg_path);folder=ROOT/'entry'/cfg['name']
    assert cfg['name']=='integral_slack_required'
    assert sorted(p.name for p in (ROOT/'entry').iterdir())==[cfg['name']]
    process=read(folder/'process.json');cleanup=read(folder/'cleanup_summary.json')
    identity=dict(cfg['identity'],config_sha256=sha(cfg_path))
    assert process['identity']==cleanup['identity']==identity and cleanup['reaped'] is True
    assert process['returncode']==0 and process['monitor_failure'] is None
    assert process['accounting']['phase']=='REAPED' and process['accounting']['action']=='retain_censored'
    expected=['monitor_invalid: Unknown Darwin process state/modifier']
    assert process['accounting']['censor_reasons']==expected and not process['accounting']['terminal_state_observed']
    assert not process['termination_actions'] and not cleanup['actions'] and cleanup['fallback_cleanup'] is False
    assert process['controlled_signal'] is None and process['controlled_fault'] is None and process['exit_permission'] is None
    trace=[json.loads(line) for line in (folder/'monitor.jsonl').read_text().splitlines()]
    assert len(trace)==process['observations'] and sha(folder/'monitor.jsonl')==process['monitor_trace_sha256']
    unknown=[];previous_cpu=0.;last=process['started_monotonic'];seen_bad=False
    for item in trace:
        e=item['event'];b=e['before'];a=e['after'];q=e.get('query')
        assert last<=b['at']<=a['at'];last=a['at']
        if q is not None:
            assert not seen_bad and b['returncode'] is None and q['returncode']==0 and not q['error']
            assert b['at']<=q['start']<=q['end']<=a['at']
            fields=q['stdout'].split();assert len(fields)==4 and int(fields[0])==process['pid']
            if fields[1]=='?E':
                assert fields[2:] == ['0','0:00.00'] and a['returncode'] is None
                assert item['decision']['censor_reasons']==expected and item['decision']['cpu_highwater']==previous_cpu
                unknown.append(e);seen_bad=True
            else:
                parsed=artifact_audit.ps(q['stdout'],process['pid'])
                assert parsed['state']!='Z' and parsed['rss']>0 and parsed['cpu']>=previous_cpu
                previous_cpu=parsed['cpu'];assert not item['decision']['censor_reasons']
        else:
            assert seen_bad and b['returncode']==a['returncode']==0 and item['decision']['censor_reasons']==expected
    assert len(unknown)==1 and previous_cpu>0 and process['accounting']['cpu_highwater']>=previous_cpu
    assert trace[-1]['event']['before']['at']>=unknown[0]['after']['at']
    assert trace[-1]['event']['before']['at']-unknown[0]['after']['at']<.5
    artifact_audit.audit_config(cfg,0,plan['case_names'][0],read(ROOT/'prepared_protocol.json'))
    final=artifact_audit.audit_final(folder,cfg,process)
    assert final['solver_status']==0 and final['incumbent_valid'] is True and final['incumbent_score']==4.
    assert final['finalized_at']['monotonic']<unknown[0]['query']['start'] and not final['signals']
    calls=[json.loads(line) for line in (folder/'native_journal.jsonl').read_text().splitlines()]
    assert [r['event'] for r in calls]==['optimizer_start','optimizer_return_persisted']
    assert calls[0]==read(folder/'optimizer_attempt.json') and all(r['identity']==identity for r in calls)
    assert calls[1]['raw_manifest_sha256']==sha(folder/'raw_manifest.json')
    report=dict(scope='failed_entry_accounting_and_one_saved_toy_artifact_only',failure_accounting_passed=True,
        native_entry_passed=False,acceptance_criteria_changed=False,unknown_state_accepted_as_terminal=False,
        failure='prospective Darwin state model rejected observed ?E during exit',observed_unknown_record=unknown[0],
        owned_child_reaped=True,raw_toy_artifact_independently_valid=True,toy_optimum=4.,
        toy_artifact_is_research_evidence=False,optimizer_api_attempts=1,optimizer_returns_persisted=1,
        experimental_workers=1,unattempted_controls=plan['case_names'][1:],unattempted_count=12,
        controller_wall_seconds=result['controller_wall_seconds'],historical_optimizer_api_attempts=18,
        cumulative_optimizer_api_attempts=19,new_research_cases=0,new_BP_OSD_LSD_calls=0,new_model_fits=0,new_physical_shots=0,
        frozen_inputs_verified=len(frozen['files']),output_files_verified=len(outputs['files']),
        frozen_sha256=sha(ROOT/'frozen.json'),frozen_independent_artifact_audit_sha256=sha(ROOT/'audit.py'),
        failure_audit_source_sha256=sha(Path(__file__)))
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('observed_unknown_record','unattempted_controls')},indent=2))
if __name__=='__main__':main()
