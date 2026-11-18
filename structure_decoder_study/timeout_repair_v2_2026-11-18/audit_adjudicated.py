"""Post-hoc supplemental audit of SAVED V2 outputs. No solver/decoder calls.

The original frozen audit FAILED; this file does not replace that outcome.
Only terminal zero-valued ps accounting samples receive the reviewed exception.
"""
from __future__ import annotations
import hashlib,itertools,json,math,signal
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'timeout_repair_2026-11-18'
ADJUDICATIONS=[]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def independent_cpu(token):
    # Independent implementation: do not import the controller parser.
    day_parts=token.split('-');assert len(day_parts) in (1,2)
    days=0
    if len(day_parts)==2:
        assert day_parts[0].isdigit();days=int(day_parts[0])
    parts=day_parts[-1].split(':');assert len(parts) in (2,3)
    assert all(p.isdigit() for p in parts[:-1])
    seconds_parts=parts[-1].split('.');assert len(seconds_parts) in (1,2)
    assert len(seconds_parts[0])==2 and all(p.isdigit() for p in seconds_parts)
    seconds=float(parts[-1]);assert 0<=seconds<60
    if len(parts)==2:
        assert len(day_parts)==1
        return int(parts[0])*60+seconds
    assert len(parts[1])==2 and 0<=int(parts[1])<60
    if len(day_parts)==2:assert 0<=int(parts[0])<24
    return days*86400+int(parts[0])*3600+int(parts[1])*60+seconds

def inspect_monitor(folder,process):
    assert read(folder/'process.json')==process
    assert process['pid']==read(folder/'startup.json')['after_limits']['pid']
    assert process['monitor_error'] is None and process['monitor_samples']
    assert process['wall_seconds']<=process['expected_wall_limit']+1.6
    previous=-1.;last_at=process['started_monotonic']
    for sample_index,sample in enumerate(process['monitor_samples']):
        fields=sample['raw'].split();assert len(fields)==3
        assert int(fields[0])==sample['pid']==process['pid']
        assert int(fields[1])*1024==sample['rss_bytes']<=1073741824
        assert fields[2]==sample['cpu_token']
        cpu=independent_cpu(fields[2]);assert abs(cpu-sample['cpu_seconds'])<1e-8
        assert sample['query_started']>=last_at
        if cpu<previous:
            assert sample_index==len(process['monitor_samples'])-1
            assert cpu==0 and sample['rss_bytes']==0 and previous>0
            assert process['watchdog_reason'] is None and not process['termination_actions']
            restoration=read(folder/'handler_restoration.json')
            assert restoration['restored'] is True
            if folder.name=='legacy_injected':
                assert process['returncode']==1
                assert read(folder/'exception.json')['kind']=='LegacySignalStop'
                assert not (folder/'result.json').exists()
                terminal=restoration['at']
            else:
                final=read(folder/'result.json')
                assert final['finalized'] is True and final['handler_restored'] is True
                assert process['returncode']==0
                terminal=final['finalized_at']
            assert sample['query_started']>=terminal['monotonic']
            assert 0<terminal['cpu_absolute']<process['expected_cpu_limit']
            maximum=max(s['cpu_seconds'] for s in process['monitor_samples'])
            assert 0<maximum<process['expected_cpu_limit']
            assert abs(maximum-terminal['cpu_absolute'])<.1
            ADJUDICATIONS.append(dict(name=folder.name,kind='final_zero_accounting_sample_after_terminal_marker',
                pid=process['pid'],sample=sample,terminal_marker_monotonic=terminal['monotonic'],
                retained_measured_cpu_maximum=maximum,final_child_cpu=terminal['cpu_absolute'],
                process_state_or_accounting_mechanism_established=False))
        else:
            previous=cpu
        assert sample['query_started']<=sample['observed_at']<=sample['query_started']+1.1
        last_at=sample['observed_at']
    assert process['peak_rss_bytes']==max(s['rss_bytes'] for s in process['monitor_samples'])
    for action in process['termination_actions']:
        assert action['pid']==process['pid'] and action['reason']==process['watchdog_reason']
        assert action['signum'] in (signal.SIGTERM,signal.SIGKILL)
        assert last_at<=action['at']<=process['started_monotonic']+process['wall_seconds']
    if process['watchdog_reason']:
        assert process['termination_actions'][0]['signum']==signal.SIGTERM
        assert process['classification']=='process_censored_or_failed'
    else:
        assert not process['termination_actions']
        assert all(s['cpu_seconds']<process['expected_cpu_limit'] for s in process['monitor_samples'])
def inspect_result(folder,process):
    assert process["returncode"]==0 and process["watchdog_reason"] is None and process["monitor_error"] is None
    r=read(folder/"result.json");h=read(folder/"handler_restoration.json");s=read(folder/"startup.json")
    assert r["finalized"] is True and r["handler_restored"] is True
    assert h["restored"] is True and h["previous"]==h["current"]==s["initial_handler"]
    assert h["stable_signals"]==r["signals"] and r["finalized_at"]["monotonic"]>=h["at"]["monotonic"]
    assert s["after_limits"]["rlimit_cpu"]==([1,3] if r["scenario"]=="cpu_soft" else [10,12])
    for state in [s["before_limits"],s["after_limits"],r["after_call"],r["finalized_at"]]:
        assert state["cpu_absolute"]>=0 and state["ru_utime"]>=0 and state["ru_stime"]>=0
        assert abs(state["cpu_absolute"]-state["ru_utime"]-state["ru_stime"])<.1
        assert state["peak_rss_bytes"]<=1073741824 and "sigxcpu_handler" in state
    expected="signal_observed_result_preserved" if r["signals"] else "solver_limit_with_incumbent" if r["solver_status"]==1 and r["has_incumbent"] else "solver_limit_no_incumbent" if r["solver_status"]==1 else "solver_completed"
    if r["scenario"]=="cpu_soft":expected="soft_cpu_signal_observed"
    assert expected==r["classification"]==process["classification"]
    if r["solver_status"] is not None:
        assert read(folder/"provisional_result.json")["finalized"] is False
        raw_meta=read(folder/"raw_metadata.json")
        assert raw_meta["has_incumbent"]==r["has_incumbent"] and raw_meta["solver_status"]==r["solver_status"]
        assert "function" in raw_meta["handler_while_raw_saved"]
        fixture=np.load(folder/"fixture.npz");edges=fixture["edges"];cost=fixture["cost"]
        if r["has_incumbent"]:
            raw=np.load(folder/"raw.npz")["x"];x=np.load(folder/"validated.npz")["x"]
            assert raw.shape==cost.shape and np.isfinite(raw).all()
            assert np.max(abs(raw-np.rint(raw)))<=1e-7 and np.array_equal(np.rint(raw).astype(np.int64),x)
            assert np.isin(x,[0,1]).all() and np.all(x[edges[:,0]]+x[edges[:,1]]<=1)
            total=math.fsum(float(v) for v,bit in zip(cost,x) if bit)
            assert total==r["incumbent_score"] and r["incumbent_valid"] is True
        else:
            assert not (folder/"raw.npz").exists() and not (folder/"validated.npz").exists()
        if r["scenario"]=="normal" and r["solver_status"]==0:
            assert len(cost)==6
            valid=[]
            for bits in itertools.product([0,1],repeat=6):
                if all(bits[int(i)]+bits[int(j)]<=1 for i,j in edges):valid.append(math.fsum(float(v) for v,bit in zip(cost,bits) if bit))
            assert abs(r["incumbent_score"]-min(valid))<1e-10
    return r

def main():
    assert not (ROOT/"audit_adjudication_result.json").exists(),"Preserve previous supplemental audit"
    for name,digest in read(ROOT/'audit_adjudication_frozen.json')['files'].items():assert sha(Path(name))==digest,name
    assert read(ROOT/'audit_initial_failure.json')['status']=='frozen_audit_failed'
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    for name,digest in read(ROOT/"output_manifest.json")["files"].items():assert sha(ROOT/name)==digest,name
    calibration=read(OLD/"calibration_result.json");v1=read(OLD/"confirmation_result.json");result=read(ROOT/"confirmation_result.json")
    assert calibration["passed"] and 2<=calibration["optimization_calls"]<=4
    prior_wall=calibration['controller_wall_seconds']+v1['controller_wall_seconds']
    assert frozen['prior_controller_wall_seconds']==prior_wall
    assert result['controller_wall_seconds']<=frozen['confirmation_controller_wall_cap']<=85
    assert result['cumulative_controller_wall_seconds']==prior_wall+result['controller_wall_seconds']<=120
    assert calibration['optimization_calls']+v1['confirmation_optimizer_calls']+result['confirmation_optimizer_calls']==12
    assert len(calibration['rows'])+len(v1['rows'])+len(result['rows'])==20
    assert read(ROOT/'unit_result.json')['passed']
    for name in ('worker.py','result_guard.py'):assert sha(ROOT/name)==sha(OLD/name)
    for name,digest in read(OLD/'manifest.json')['files'].items():assert sha(OLD/name)==digest,name
    assert read(OLD/'V1_OUTCOME.json')['audit_passed'] is False
    assert result["all_scenarios_attempted"] and result["frozen_sha256"]==sha(ROOT/"frozen.json")
    expected=["timeout_none","timeout_incumbent","legacy_injected","deferred_injected","optimal","soft_cpu","hard_cpu","wall_guard","late_persistence"]
    assert [r["name"] for r in result["rows"]]==expected
    assert result["confirmation_optimizer_calls"]==5 and result["real_research_calls"]==0
    for row in calibration["rows"]:inspect_result(OLD/row["folder"],row["process"])
    reports={};checks=[]
    selected=frozen["selected_fixture"]
    chosen=OLD/"calibration"/f"with_{selected['n']}"/"fixture.npz"
    reference=np.load(chosen)
    for row in result["rows"]:
        folder=ROOT/row["folder"];process=row["process"];name=row["name"]
        assert process["monitor_error"] is None and process["peak_rss_bytes"]<=1073741824
        inspect_monitor(folder,process)
        assert process['expected_cpu_limit']==(3. if name=='hard_cpu' else 10.)
        if name=="hard_cpu":
            assert process["returncode"] in (-signal.SIGTERM,-signal.SIGKILL) and process["watchdog_reason"]=='cpu_limit'
            crossing=process['monitor_samples'][-1]
            assert 3.<=crossing['cpu_seconds']<=3.5
            assert all(s['cpu_seconds']<3. for s in process['monitor_samples'][:-1])
            assert process['termination_actions'][0]['at']>=crossing['observed_at']
            assert process['termination_actions'][0]['at']-crossing['observed_at']<=.1
            assert process["classification"]=="process_censored_or_failed" and not (folder/"result.json").exists()
            assert read(folder/"startup.json")["after_limits"]["rlimit_cpu"]==[1,3]
            progress=read(folder/'progress.json')
            assert progress['signals'] and 2.8<=progress['at']['cpu_absolute']<=3.5
            assert progress['at']['pid']==process['pid'] and process['controlled_injection'] is None
        elif name=="wall_guard":
            assert process["watchdog_reason"]=="wall_limit" and process["returncode"]!=0
            assert process["classification"]=="process_censored_or_failed" and not (folder/"result.json").exists()
        elif name=="legacy_injected":
            assert process["returncode"]==1 and process["watchdog_reason"] is None
            assert process["classification"]=="process_censored_or_failed"
            assert not (folder/"raw.npz").exists() and not (folder/"result.json").exists()
            e=read(folder/"exception.json");assert e["kind"]=="LegacySignalStop" and e["returned_object_assigned"] is False
            assert read(folder/"handler_restoration.json")["restored"] is True
            injection=process["controlled_injection"];startup=read(folder/"startup.json")
            assert injection["sent"] is True and injection["pid"]==startup["after_limits"]["pid"]
            assert injection["signum"]==signal.SIGXCPU
            assert e["before_call"]["monotonic"]<=injection["sent_at_monotonic"]<=e["at"]["monotonic"]
        else:
            r=inspect_result(folder,process);reports[name]=r
            if name=="timeout_none":assert r["solver_status"]==1 and not r["has_incumbent"] and not r["signals"]
            if name=="timeout_incumbent":assert r["solver_status"]==1 and r["has_incumbent"] and not r["signals"]
            if name in ("deferred_injected","late_persistence"):
                injection=process["controlled_injection"];assert injection["sent"] is True
                startup=read(folder/"startup.json")
                assert injection["pid"]==startup["after_limits"]["pid"] and injection["signum"]==signal.SIGXCPU
                assert r["signals"] and r["classification"]=="signal_observed_result_preserved"
                assert all(e["signum"]==signal.SIGXCPU and e["handled_at"]["monotonic"]>=injection["sent_at_monotonic"] for e in r["signals"])
                assert r["has_incumbent"] and r["incumbent_valid"]
            if name=="deferred_injected":
                assert r["native_optimizer_calls"]==1
                assert r["before_call"]["monotonic"]<=injection["sent_at_monotonic"]<=r["after_call"]["monotonic"]
            if name=="late_persistence":
                assert r["native_optimizer_calls"]==0 and r["exception_restoration_unit_passed"] is True
                assert injection["ready"]["phase"]=="guarded_persistence"
                assert any(e["phase"]=="persisting_result" for e in r["signals"])
            if name=="soft_cpu":
                assert r["signals"] and r["classification"]=="soft_cpu_signal_observed" and r["native_optimizer_calls"]==0
                assert any(e["handled_at"]["rlimit_cpu"]==[1,3] and e["handled_at"]["cpu_absolute"]>=.9 for e in r["signals"])
                assert process["controlled_injection"] is None
        if name in ("timeout_incumbent","legacy_injected","deferred_injected"):
            fixture=np.load(folder/"fixture.npz")
            assert np.array_equal(fixture["edges"],reference["edges"]) and np.array_equal(fixture["cost"],reference["cost"])
        checks.append(dict(name=name,passed=True))
    assert reports["optimal"]["solver_status"]==0
    assert {a['name'] for a in ADJUDICATIONS}=={'legacy_injected','deferred_injected'}
    old=ROOT.parent/"reference_probe_2026-11-18"
    for name,digest in read(old/"manifest.json")["files"].items():assert sha(old/name)==digest,name
    report=dict(passed=True,status='supplemental_saved_output_audit_passed_original_audit_failed',
        original_frozen_audit_passed=False,post_hoc_adjudication=True,terminal_accounting_adjudications=ADJUDICATIONS,
        additional_optimizer_api_attempts=0,additional_children=0,
        checks=checks,calibration_optimizer_api_attempts=calibration["optimization_calls"],confirmation_optimizer_api_attempts=5,
        real_research_calls=0,physical_shots=0,controlled_legacy_loss_reproduced=True,controlled_result_loss_repaired=True,
        ordinary_timeouts_with_and_without_incumbents_validated=True,late_signal_and_restoration_validated=True,
        parent_CPU_and_wall_containment_validated=True,OS_hard_CPU_containment_validated=False,
        RSS_monitoring_enabled_but_no_crossing_test=True,signal_runs_not_promoted_to_ordinary_success=True,
        prior_V1_audit_failed_and_preserved=True,cumulative_optimizer_api_attempts=12,cumulative_children=20,
        cumulative_controller_wall_seconds=result['cumulative_controller_wall_seconds'],
        prior_V1_manifest_sha256=sha(OLD/'manifest.json'),
        historical_signal_origin_established=False,prior_reference_manifest_sha256=sha(old/"manifest.json"),
        frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)))
    save(ROOT/"audit_adjudication_result.json",report);print(json.dumps(report,indent=2))

if __name__=="__main__":main()
