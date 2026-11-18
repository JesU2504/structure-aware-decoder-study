"""Independent explicit-vector audit; no source helper or decoder calls."""
from __future__ import annotations
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[key]="1"
import ast
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
OLD=STUDY/"natural_noise_reproduction_2026-11-17"
ORDER=STUDY/"ordering_diagnostic_2026-11-17"
START_CPU,START_WALL=time.process_time(),time.monotonic()
ATOL,RTOL=1e-8,1e-12

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
    tmp=p.with_name(p.name+".tmp")
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n");tmp.replace(p)
def peak():
    raw=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(raw if sys.platform=="darwin" else raw*1024)
def budget():
    assert time.process_time()-START_CPU<600,"Audit CPU budget"
    assert time.monotonic()-START_WALL<900,"Audit wall budget"
    assert peak()<=1073741824,"Audit RSS budget"
def rank(a):
    a=a.tocsr();basis={}
    for row in range(a.shape[0]):
        word=0
        for j,v in zip(a.indices[a.indptr[row]:a.indptr[row+1]],a.data[a.indptr[row]:a.indptr[row+1]]):
            if int(v)%2:word^=1<<int(j)
        while word:
            p=word.bit_length()-1
            if p in basis:word^=basis[p]
            else:basis[p]=word;break
    return len(basis)

def main():
    assert not (ROOT/"result_audit.json").exists(),"Preserve previous audit"
    resource.setrlimit(resource.RLIMIT_CPU,(600,605))
    def stop(_s,_f):raise RuntimeError("Audit CPU limit")
    signal.signal(signal.SIGXCPU,stop)
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    worker=read(ROOT/"worker_result.json");controller=read(ROOT/"controller_result.json")
    assert worker["status"]==controller["status"]=="completed"
    assert controller["returncode"]==0 and controller["watchdog_reason"] is None and controller["monitor_error"] is None
    assert worker["gates_completed"]==worker["searches_completed"]==24
    assert controller["frozen_sha256"]==worker["frozen_sha256"]==sha(ROOT/"frozen.json")
    assert worker["child_cpu_seconds"]<600 and controller["wall_seconds"]<900
    assert max(worker["peak_child_rss_bytes"],controller["peak_observed_child_rss_bytes"])<=1073741824
    assert worker["new_native_decoder_calls"]==worker["new_physical_shots"]==0
    for name in ("algebra_adapters.json","watchdog_adapters.json","exit_classifier_adapters.json","global_gate.json"):
        assert read(ROOT/name)["passed"]
    journal=[json.loads(line) for line in (ROOT/"journal.jsonl").read_text().splitlines()]
    selection=read(ROOT/"selection.json");ids=[r["case_id"] for r in selection]
    assert ids==[r["case_id"] for r in frozen["cases"]]
    expected=[(event,cid) for cid in ids for event in ("gate_start","gate_complete")]
    expected += [("all_gates_passed",None)]+[(event,cid) for cid in ids for event in ("search_start","search_complete")]
    assert [(r["event"],r.get("case_id")) for r in journal]==expected
    primary=[json.loads(line) for line in (OLD/"invocations.jsonl").read_text().splitlines()]
    primary=[r for r in primary if r["event"]=="complete" and r["phase"]=="main" and r["config"]["name"]=="osd20"]
    fail=sorted(r["case_id"] for r in primary if r["outcome"]=="logical_failure")
    control=[]
    for block in range(2):
        control+=sorted(r["case_id"] for r in primary if r["case_id"]//256==block and r["outcome"]=="correct" and not r["bp_converged"])[:6]
    assert len(fail)==len(control)==12 and ids==sorted(fail+control)
    h=sp.load_npz(OLD/"entry/H.npz").astype(np.int64).tocsr()
    l=sp.load_npz(OLD/"entry/L.npz").astype(np.int64).tocsr()
    priors=np.load(OLD/"entry/priors.npy");weight=np.log(1/priors)
    assert h.shape==(1800,12240) and rank(h)==1794 and l.shape==(12,12240)
    assert np.isfinite(weight).all()
    rows=[];totals={k:dict(rescues=[],regressions=[],remaining_failures=[],correct_controls=[]) for k in ("500","1000","full")}
    for case,input_case in zip(selection,frozen["cases"]):
        budget();cid=case["case_id"]
        original=np.load(case["cached_npz"]);sanitized=np.load(input_case["input_npz"])
        assert set(sanitized.files)=={"llrs","syndrome","correction","order"}
        for name in ("llrs","syndrome","correction"):assert np.array_equal(sanitized[name],original[name])
        native_order=np.load(ORDER/"cases"/f"{cid:04d}.npz")["native_order"]
        assert np.array_equal(sanitized["order"],native_order)
        gate=np.load(ROOT/"gates"/f"{cid:04d}.npz");gate_report=read(ROOT/"gates"/f"{cid:04d}.json")
        data=np.load(ROOT/"search"/f"{cid:04d}.npz");report=read(ROOT/"search"/f"{cid:04d}.json")
        assert report["case_id"]==gate_report["case_id"]==cid and gate_report["baseline_equal"]
        order=gate["order"];pivot=gate["pivot_cols"];e0=gate["solution"]
        assert np.array_equal(order,native_order) and np.array_equal(np.sort(order),np.arange(12240))
        assert np.all(np.diff(original["llrs"][order])>=0)
        assert len(set(pivot.tolist()))==1794 and rank(h[:,pivot])==1794
        mask=np.ones(12240,dtype=bool);mask[pivot]=False;free=order[mask[order]]
        assert len(free)==10446 and np.array_equal(free,data["free"])
        assert np.array_equal(e0,original["correction"]) and np.array_equal(e0,data["baseline"]) and not e0[free].any()
        assert np.array_equal(h@e0%2,original["syndrome"])
        reduced=gate["reduced"]
        identity=((reduced[:,pivot>>6]>>(pivot&63).astype(np.uint64))&np.uint64(1)).astype(np.uint8)
        assert np.array_equal(identity,np.eye(1794,dtype=np.uint8))
        assert np.array_equal(order[gate["pivot_pos"]],pivot)
        assert int(gate["closed_at"])==int(gate["pivot_pos"][-1])
        rf_all=data["rf"];saved_direct=data["direct_scores"]
        assert rf_all.shape==(1794,10446) and np.isin(rf_all,[0,1]).all()
        assert saved_direct.shape==(10446,) and np.isfinite(saved_direct).all()
        delta=data["delta"];direct=np.empty(10446);base_score=float(weight@e0)
        assert delta.shape==(10446,) and np.isfinite(delta).all()
        max_error=0.;near_correct=near_incorrect=0
        saved_min=min(base_score,float(saved_direct.min()))
        actual=original["actual"] # Only this postselection audit uses truth.
        baseline_failed=bool(np.any(l@e0%2!=actual))
        assert baseline_failed==(cid in fail)
        if np.isclose(base_score,saved_min,atol=ATOL,rtol=RTOL):
            near_incorrect+=int(baseline_failed);near_correct+=int(not baseline_failed)
        for start in range(0,10446,128):
            budget();end=min(start+128,10446);f=free[start:end];rf=rf_all[:,start:end]
            expected_rf=((reduced[:,f>>6]>>(f&63).astype(np.uint64))&np.uint64(1)).astype(np.uint8)
            assert np.array_equal(rf,expected_rf)
            candidates=np.repeat(e0[:,None],end-start,axis=1)
            candidates[pivot,:]=np.bitwise_xor(e0[pivot,None],rf)
            candidates[f,np.arange(end-start)]=1
            assert np.isin(candidates,[0,1]).all()
            assert np.all(h@candidates.astype(np.int64)%2==original["syndrome"][:,None])
            scores=weight@candidates.astype(np.float64);direct[start:end]=scores
            err=np.abs((base_score-scores)-delta[start:end]);max_error=max(max_error,float(err.max()))
            assert np.allclose(delta[start:end],base_score-scores,atol=ATOL,rtol=RTOL)
            assert np.allclose(saved_direct[start:end],scores,atol=ATOL,rtol=RTOL)
            near=np.isclose(scores,saved_min,atol=ATOL,rtol=RTOL)
            if near.any():
                failed=np.any(l@candidates[:,near].astype(np.int64)%2!=actual[:,None],axis=0)
                near_incorrect+=int(failed.sum());near_correct+=int((~failed).sum())
        outcomes={}
        for key,k in (("500",500),("1000",1000),("full",10446)):
            # Python max returns the first maximum; do not call source picker.
            best=max(range(k),key=lambda j:float(delta[j]));out=e0.copy()
            chosen=None
            if float(delta[best])>0:
                chosen=int(free[best]);out[pivot]^=rf_all[:,best];out[chosen]=1
            assert np.array_equal(out,data["correction_"+key])
            assert np.array_equal(h@out%2,original["syndrome"])
            out_score=float(weight@out);minimum=min(base_score,float(direct[:k].min()))
            assert np.isclose(out_score,minimum,atol=ATOL,rtol=RTOL)
            source_key=str(k);record=report["outputs"][source_key]
            assert record["chosen_free_column"]==chosen and np.isclose(record["score"],out_score,atol=ATOL,rtol=RTOL)
            assert record["source_delta"]==(float(delta[best]) if chosen is not None else 0.)
            wrong=int(np.count_nonzero(l@out%2!=actual));failed=wrong>0
            transition=("remaining_failures" if failed else "rescues") if baseline_failed else ("regressions" if failed else "correct_controls")
            totals[key][transition].append(cid)
            outcomes[key]=dict(logical_failure=failed,wrong_logical_bits=wrong,transition=transition,chosen_free_column=chosen,score=out_score)
        score_sequence=[base_score]+[outcomes[k]["score"] for k in ("500","1000","full")]
        for before,after in zip(score_sequence,score_sequence[1:]):
            assert after<=before+ATOL+RTOL*abs(before),"Expanded search worsened surrogate score"
        assert np.isclose(report["baseline_score"],base_score,atol=ATOL,rtol=RTOL)
        assert report["free_candidates"]==10446 and report["max_delta_absolute_error"]<=max_error+1e-9
        best_delta=float(max(delta));ordered_delta=sorted(float(x) for x in delta)
        tol=ATOL+RTOL*max(abs(best_delta),abs(base_score))
        assert report["best_source_delta"]==best_delta
        assert report["second_best_margin"]==ordered_delta[-1]-ordered_delta[-2]
        assert report["candidates_near_best"]==int(np.count_nonzero(np.abs(delta-best_delta)<=tol))
        assert report["near_zero_best"]==(abs(best_delta)<=tol)
        rows.append(dict(case_id=cid,baseline_failure=baseline_failed,candidates_explicitly_checked=10446,
            max_delta_absolute_error=max_error,outcomes=outcomes,
            near_minimum_candidates_correct=near_correct,near_minimum_candidates_incorrect=near_incorrect,
            logical_class_sensitive_within_tolerance=near_correct>0 and near_incorrect>0))
        print(json.dumps(dict(audited_case=cid,cases_completed=len(rows),full_transition=outcomes["full"]["transition"])),flush=True)
    previous={}
    names=list(read(ORDER/"audit.json")["previous_manifests_verified"])+["ordering_diagnostic_2026-11-17/manifest.json"]
    for name in names:
        p=STUDY/name
        for relative,digest in read(p)["files"].items():assert sha(p.parent/relative)==digest,(name,relative)
        previous[name]=sha(p)
    tree=ast.parse((ROOT/"experiment.py").read_text())
    assert not any(isinstance(n,ast.Attribute) and n.attr=="decode" for n in ast.walk(tree))
    search_outputs={str(p.relative_to(ROOT)):sha(p) for folder in ("inputs","gates","search") for p in sorted((ROOT/folder).iterdir()) if p.is_file()}
    assert len(list((ROOT/"search").glob("*.npz")))==24
    assert len(list((ROOT/"gates").glob("*.npz")))==24
    budget()
    result=dict(passed=True,cases=24,failures=12,success_controls=12,all_baselines_exact=True,
        candidates_explicitly_checked=24*10446,all1800_rows_checked_for_every_candidate=True,
        full_vector_direct_scoring=True,source_selection_rules_verified=True,prefix_score_monotonicity_verified=True,new_native_decoder_calls=0,new_physical_shots=0,
        global_gate_respected=True,totals=totals,rows=rows,previous_manifests_verified=previous,
        audited_outputs_sha256=search_outputs,frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)),
        audit_cpu_seconds=time.process_time()-START_CPU,audit_wall_seconds=time.monotonic()-START_WALL,peak_audit_rss_bytes=peak(),
        scope="Selected development diagnostic; not population gain, independent validation, hidden native pivots or novelty")
    save(ROOT/"result_audit.json",result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("rows","previous_manifests_verified","audited_outputs_sha256")}))

if __name__=="__main__":main()
