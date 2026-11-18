"""Synthetic-only solver/CPU signal harness. No research-case file access."""
from __future__ import annotations
import os,time
START_CPU,START_WALL=time.process_time(),time.monotonic()
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[key]="1"
import json,math,resource,signal,sys,warnings
from pathlib import Path
from result_guard import SignalLedger,atomic_json,telemetry,classify

class LegacySignalStop(Exception):pass

def fixture(n,seed):
    import numpy as np
    import scipy.sparse as sp
    rng=np.random.default_rng(seed)
    pairs=np.transpose(np.nonzero(np.triu(rng.random((n,n))<.08,1)))
    rr=np.repeat(np.arange(len(pairs)),2);cc=pairs.ravel()
    a=sp.coo_array((np.ones(len(cc)),(rr,cc)),shape=(len(pairs),n)).tocsc()
    c=-(1.+.001*rng.random(n))
    return pairs,a,c

def main(config_path):
    cfg=json.loads(Path(config_path).read_text());out=Path(cfg["output"]);out.mkdir(parents=True,exist_ok=True)
    initial=telemetry();scenario=cfg["scenario"]
    cpu_limits=(1,3) if scenario in ("cpu_soft","cpu_hard") else (10,12)
    resource.setrlimit(resource.RLIMIT_CPU,cpu_limits)
    previous=signal.getsignal(signal.SIGXCPU)
    atomic_json(out/"startup.json",dict(before_limits=initial,after_limits=telemetry(),scenario=scenario,
        start_cpu=START_CPU,start_wall=START_WALL,initial_handler=str(previous)))
    if scenario=="wall_kill":
        atomic_json(out/"ready.json",dict(phase="sleep",at=telemetry()))
        time.sleep(2);raise AssertionError("External wall guard did not stop child")
    report=None;legacy_failure=False;ledger=SignalLedger()
    try:
        with ledger:
            if scenario in ("cpu_soft","cpu_hard"):
                ledger.phase="cpu_spin";last=0.
                while True:
                    value=sum(i*i for i in range(1000))
                    now=time.process_time()
                    if now-last>.1:
                        atomic_json(out/"progress.json",dict(at=telemetry(),signals=ledger.events));last=now
                    if ledger.events and scenario=="cpu_soft":break
                ledger.phase="persisting"
                report=dict(classification="soft_cpu_signal_observed",after_call=telemetry(),scenario=scenario,
                    has_incumbent=False,solver_status=None,native_optimizer_calls=0)
            else:
                import numpy as np
                from scipy.optimize import milp,Bounds,LinearConstraint
                n=cfg["n"];seed=cfg["seed"];pairs,a,c=fixture(n,seed)
                np.savez_compressed(out/"fixture.npz",edges=pairs,cost=c)
                if scenario=="legacy_signal":
                    def throwing(_s,_f):raise LegacySignalStop("Controlled legacy raising-handler loss")
                    signal.signal(signal.SIGXCPU,throwing)
                ledger.phase="solver_call"
                atomic_json(out/"ready.json",dict(phase="solver_call",at=telemetry()))
                before=telemetry();returned=None
                try:
                    if scenario=="late_persistence":
                        from types import SimpleNamespace
                        returned=SimpleNamespace(status=1,message="Known payload for persistence unit; no solver call",x=np.zeros(n))
                        caught=[];native_calls=0
                    else:
                        native_calls=1
                        with warnings.catch_warnings(record=True) as caught:
                            warnings.simplefilter("always")
                            returned=milp(c=c,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),
                                constraints=LinearConstraint(a,-np.inf,np.ones(a.shape[0])),
                                options=dict(time_limit=cfg["time_limit"],presolve=False,mip_rel_gap=0.,threads=1,random_seed=0,disp=False))
                    after=telemetry();ledger.phase="persisting_result"
                    raw=returned.x
                    if raw is not None:np.savez_compressed(out/"raw.npz",x=raw)
                    atomic_json(out/"raw_metadata.json",dict(solver_status=int(returned.status),has_incumbent=raw is not None,
                        before_call=before,after_call=after,handler_while_raw_saved=str(signal.getsignal(signal.SIGXCPU))))
                    if scenario=="late_persistence":
                        atomic_json(out/"persist_ready.json",dict(phase="guarded_persistence",at=telemetry()))
                        time.sleep(.10)
                    valid=None;score=None;proximity=None
                    if raw is not None:
                        raw=np.asarray(raw);assert raw.shape==(n,) and np.isfinite(raw).all()
                        proximity=float(np.max(abs(raw-np.rint(raw))))
                        assert proximity<=1e-7
                        x=np.rint(raw).astype(np.int64)
                        assert np.isin(x,[0,1]).all() and np.all(x[pairs[:,0]]+x[pairs[:,1]]<=1)
                        score=math.fsum(float(c[i]) for i in range(n) if x[i])
                        valid=True;np.savez_compressed(out/"validated.npz",x=x)
                    report=dict(scenario=scenario,solver_status=int(returned.status),solver_message=str(returned.message),
                        has_incumbent=raw is not None,incumbent_valid=valid,incumbent_score=score,integer_proximity=proximity,
                        before_call=before,after_call=after,start_cpu=START_CPU,native_optimizer_calls=native_calls,
                        scipy_warnings=[str(w.message) for w in caught],oracle_or_research_data_used=False)
                except Exception as exc:
                    ledger.phase="exception_persisting"
                    atomic_json(out/"exception.json",dict(kind=type(exc).__name__,message=str(exc),at=telemetry(),
                        signals=ledger.events,returned_object_assigned=returned is not None,before_call=before,scenario=scenario))
                    if scenario=="legacy_signal" and isinstance(exc,LegacySignalStop):legacy_failure=True
                    else:raise
            if report is not None:
                atomic_json(out/"provisional_result.json",dict(report,finalized=False))
    finally:
        # Context exit restored the prior handler. Its event list is now stable.
        restored=signal.getsignal(signal.SIGXCPU)==previous
        atomic_json(out/"handler_restoration.json",dict(restored=restored,previous=str(previous),current=str(signal.getsignal(signal.SIGXCPU)),
            at=telemetry(),stable_signals=list(ledger.events)))
    assert restored
    if legacy_failure:raise SystemExit(1)
    assert report is not None
    if scenario=="late_persistence":
        try:
            with SignalLedger():raise ValueError("Deliberate restoration unit")
        except ValueError:pass
        assert signal.getsignal(signal.SIGXCPU)==previous
        report["exception_restoration_unit_passed"]=True
    events=list(ledger.events)
    if report["solver_status"] is not None:report["classification"]=classify(report["solver_status"],report["has_incumbent"],events)
    report.update(signals=events,finalized=True,handler_restored=restored,finalized_at=telemetry())
    atomic_json(out/"result.json",report)

if __name__=="__main__":main(sys.argv[1])
