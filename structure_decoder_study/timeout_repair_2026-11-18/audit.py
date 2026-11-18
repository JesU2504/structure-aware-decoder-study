"""Independent checks of synthetic timeout, signal, persistence and containment."""
from __future__ import annotations
import hashlib,itertools,json,math,signal
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
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
    assert not (ROOT/"audit_result.json").exists(),"Preserve previous audit"
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    for name,digest in read(ROOT/"output_manifest.json")["files"].items():assert sha(ROOT/name)==digest,name
    calibration=read(ROOT/"calibration_result.json");result=read(ROOT/"confirmation_result.json")
    assert calibration["passed"] and 2<=calibration["optimization_calls"]<=4
    assert calibration["controller_wall_seconds"]<=35 and result["controller_wall_seconds"]<=85
    assert calibration["controller_wall_seconds"]+result["controller_wall_seconds"]<=120
    assert result["all_scenarios_attempted"] and result["frozen_sha256"]==sha(ROOT/"frozen.json")
    expected=["timeout_none","timeout_incumbent","legacy_injected","deferred_injected","optimal","soft_cpu","hard_cpu","wall_guard","late_persistence"]
    assert [r["name"] for r in result["rows"]]==expected
    assert result["confirmation_optimizer_calls"]==5 and result["real_research_calls"]==0
    assert len(calibration["rows"])+len(result["rows"])<=13
    for row in calibration["rows"]:inspect_result(ROOT/row["folder"],row["process"])
    reports={};checks=[]
    selected=frozen["selected_fixture"]
    chosen=ROOT/"calibration"/f"with_{selected['n']}"/"fixture.npz"
    reference=np.load(chosen)
    for row in result["rows"]:
        folder=ROOT/row["folder"];process=row["process"];name=row["name"]
        assert process["monitor_error"] is None and process["peak_rss_bytes"]<=1073741824
        if name=="hard_cpu":
            assert process["returncode"]==-signal.SIGKILL and process["watchdog_reason"] is None
            assert process["classification"]=="process_censored_or_failed" and not (folder/"result.json").exists()
            assert read(folder/"startup.json")["after_limits"]["rlimit_cpu"]==[1,3]
            assert read(folder/"progress.json")["signals"]
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
    old=ROOT.parent/"reference_probe_2026-11-18"
    for name,digest in read(old/"manifest.json")["files"].items():assert sha(old/name)==digest,name
    report=dict(passed=True,checks=checks,calibration_optimizer_api_attempts=calibration["optimization_calls"],confirmation_optimizer_api_attempts=5,
        real_research_calls=0,physical_shots=0,controlled_legacy_loss_reproduced=True,controlled_result_loss_repaired=True,
        ordinary_timeouts_with_and_without_incumbents_validated=True,late_signal_and_restoration_validated=True,
        hard_CPU_and_wall_containment_validated=True,signal_runs_not_promoted_to_ordinary_success=True,
        historical_signal_origin_established=False,prior_reference_manifest_sha256=sha(old/"manifest.json"),
        frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)))
    save(ROOT/"audit_result.json",report);print(json.dumps(report,indent=2))

if __name__=="__main__":main()
