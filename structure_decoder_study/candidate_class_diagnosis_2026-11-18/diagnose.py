"""Classify already saved candidates; never decode, enlarge search or reselect."""
from __future__ import annotations
import os,time
START_CPU,START_WALL=time.process_time(),time.monotonic()
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[k]="1"
import hashlib,json,resource,signal,sys
from pathlib import Path
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
HEAD=STUDY/"headroom_cached_order_2026-11-17"
OLD=STUDY/"natural_noise_reproduction_2026-11-17"
ATOL,RTOL=1e-8,1e-12
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    tmp=p.with_name(p.name+".tmp");tmp.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");tmp.replace(p)
def peak():
    v=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(v if sys.platform=="darwin" else v*1024)
class BudgetStop(Exception):pass
def budget():
    if time.process_time()-START_CPU>=600:raise BudgetStop("CPU limit")
    if time.monotonic()-START_WALL>=900:raise BudgetStop("Wall limit")
    if peak()>1073741824:raise BudgetStop("RSS limit")
def codes(bits):
    bits=np.asarray(bits)
    assert bits.ndim==2 and bits.shape[0]<=16 and np.isin(bits,[0,1]).all()
    return (1<<np.arange(bits.shape[0],dtype=np.uint16))@bits.astype(np.uint16)
def tolerance(a,b):return ATOL+RTOL*max(abs(a),abs(b))
def selected_position(delta):
    j=int(np.argmax(delta))
    return j+1 if float(delta[j])>0. else 0

def summarize(labels,scores,improvements,selected,truth):
    labels=np.asarray(labels);scores=np.asarray(scores);improvements=np.asarray(improvements)
    assert labels.shape==scores.shape==improvements.shape and scores.ndim==1
    assert np.isfinite(scores).all() and np.isfinite(improvements).all()
    records=[]
    for label in np.unique(labels):
        ix=np.flatnonzero(labels==label)
        raw=int(ix[np.argmin(scores[ix])]);source=int(ix[np.argmax(improvements[ix])])
        records.append(dict(logical_class=int(label),count=len(ix),minimum_raw_score=float(scores[raw]),
            first_exact_raw_minimum_position=raw,source_best_position=source,
            source_best_delta=float(improvements[source]),source_best_raw_score=float(scores[source]),
            exact_raw_minimum_count=int(np.count_nonzero(scores[ix]==scores[raw])),
            exact_source_best_count=int(np.count_nonzero(improvements[ix]==improvements[source]))))
    own=next((r for r in records if r["logical_class"]==truth),None)
    other=[r for r in records if r["logical_class"]!=truth]
    competitor=min(other,key=lambda r:(r["minimum_raw_score"],r["logical_class"])) if other else None
    correct=int(labels[selected])==truth
    gap=(own["minimum_raw_score"]-competitor["minimum_raw_score"]) if own and competitor else None
    sensitive=bool(gap is not None and abs(gap)<=tolerance(own["minimum_raw_score"],competitor["minimum_raw_score"]))
    if gap is not None and not sensitive:assert (gap<0)==correct,"Source winner contradicts robust raw-class margin"
    raw_min=float(scores.min());source_max=float(improvements.max())
    result=dict(list_members=len(labels),represented_classes=len(records),true_logical_class=int(truth),
        selected_position=int(selected),selected_logical_class=int(labels[selected]),selected_score=float(scores[selected]),
        true_class_present=own is not None,true_class_count=own["count"] if own else 0,
        true_class_minimum_score=own["minimum_raw_score"] if own else None,
        best_competing_class=competitor["logical_class"] if competitor else None,
        best_competing_score=competitor["minimum_raw_score"] if competitor else None,
        true_minus_best_competing_gap=gap,
        undefined_margin_reason="correct_class_absent" if own is None else "no_competing_class" if competitor is None else None,
        true_competitor_numerically_sensitive=sensitive,
        raw_minimum_classes=[r["logical_class"] for r in records if abs(r["minimum_raw_score"]-raw_min)<=tolerance(r["minimum_raw_score"],raw_min)],
        source_maximum_delta=source_max,source_exact_best_count=int(np.count_nonzero(improvements==source_max)),
        selected_matches_truth=correct,
        diagnosis="source_success" if correct else "correct_class_present_but_not_selected" if own else "correct_class_absent_from_saved_list")
    return result,records

def adapters():
    h=np.array([[1,1,0,1,1],[0,1,1,0,0],[1,0,1,1,1]],dtype=np.int64)
    l=np.array([[0,0,0,1,1],[0,0,1,1,1]],dtype=np.int64)
    e0=np.array([1,0,0,0,0],dtype=np.uint8);piv=np.array([0,1]);free=np.array([2,3,4])
    rf=np.array([[1,1,1],[1,0,0]],dtype=np.uint8)
    algebra=(l@e0%2)[:,None]^((l[:,piv]@rf+l[:,free])%2)
    x=np.repeat(e0[:,None],3,axis=1);x[piv,:]^=rf;x[free,np.arange(3)]=1
    assert np.array_equal(h@x%2,np.repeat((h@e0%2)[:,None],3,axis=1))
    assert np.array_equal(l@x%2,algebra)
    labels=np.r_[codes((l@e0%2)[:,None]),codes(algebra)]
    assert labels.tolist()==[0,2,3,3]
    scores=np.array([3.,4.,1.,1.]);improve=np.array([0.,-1.,2.,2.]);selected=selected_position(improve[1:])
    assert selected==2
    for truth,expected in [(3,"source_success"),(0,"correct_class_present_but_not_selected"),(1,"correct_class_absent_from_saved_list")]:
        row,groups=summarize(labels,scores,improve,selected,truth)
        assert row["diagnosis"]==expected and sum(r["count"] for r in groups)==4
        if truth==1:assert row["true_class_minimum_score"] is row["true_minus_best_competing_gap"] is None
    # A strict-positive source decision is preserved even if raw roundoff ranks differently.
    assert selected_position(np.array([0.,-1e-15]))==0
    row,_=summarize(np.array([0,1]),np.array([1.,1.-1e-13]),np.array([0.,-1e-15]),0,1)
    assert row["diagnosis"]=="correct_class_present_but_not_selected" and row["true_competitor_numerically_sensitive"]
    row,_=summarize(np.array([0,0]),np.array([1.,1.]),np.array([0.,0.]),0,0)
    assert row["selected_matches_truth"] and row["best_competing_score"] is row["true_minus_best_competing_gap"] is None
    assert row["undefined_margin_reason"]=="no_competing_class"
    all_codes=np.arange(4096,dtype=np.uint16)
    bits=((all_codes[None,:]>>np.arange(12,dtype=np.uint16)[:,None])&1).astype(np.uint8)
    assert np.array_equal(codes(bits),all_codes)
    return dict(passed=True,dependent_row_algebra=True,duplicate_class_grouping=True,absent_scores_null=True,
        source_positive_and_zero_ties=True,all4096_logical_codes_roundtrip=True)

def main():
    assert not (ROOT/"analysis_result.json").exists(),"Preserve previous run"
    resource.setrlimit(resource.RLIMIT_CPU,(600,605))
    def stop(_s,_f):raise BudgetStop("CPU limit")
    signal.signal(signal.SIGXCPU,stop)
    frozen=read(ROOT/"frozen.json");rows=[];status="validation_failed";message=""
    try:
        for name,expected in frozen["files"].items():assert sha(Path(name))==expected,name
        save(ROOT/"algebra_adapters.json",adapters())
        l=sp.load_npz(OLD/"entry/L.npz").astype(np.int64).tocsr()
        priors=np.load(OLD/"entry/priors.npy");weight=np.log(1/priors)
        assert l.shape==(12,12240) and np.isfinite(weight).all()
        for case in frozen["cases"]:
            budget();cid=case["case_id"]
            with (ROOT/"journal.jsonl").open("a") as f:f.write(json.dumps(dict(event="start",case_id=cid))+"\n")
            cached=np.load(case["cached_npz"]);gate=np.load(HEAD/"gates"/f"{cid:04d}.npz")
            saved=np.load(HEAD/"search"/f"{cid:04d}.npz")
            pivot=gate["pivot_cols"];e0=saved["baseline"];free=saved["free"];rf=saved["rf"];delta=saved["delta"]
            assert len(free)==10446 and rf.shape==(1794,10446) and delta.shape==(10446,)
            assert not e0[free].any() and np.isin(rf,[0,1]).all(),"Affine class formula requires zero free bits/binary rf"
            assert np.array_equal(e0,cached["correction"]) and np.isin(cached["actual"],[0,1]).all()
            baseline_bits=np.asarray(l@e0%2).ravel()
            offsets=(l[:,pivot]@rf.astype(np.int64)+l[:,free].toarray())%2
            candidate_bits=baseline_bits[:,None]^offsets
            labels=np.r_[codes(baseline_bits[:,None]),codes(candidate_bits)]
            scores=np.r_[float(weight@e0),saved["direct_scores"]]
            improvements=np.r_[0.,delta];position=selected_position(delta)
            out=e0.copy()
            if position:out[pivot]^=rf[:,position-1];out[int(free[position-1])]=1
            assert np.array_equal(out,saved["correction_full"]),"Source policy/selected correction changed"
            assert int(codes((l@out%2)[:,None])[0])==int(labels[position])
            truth=int(codes(cached["actual"][:,None])[0])
            row,groups=summarize(labels,scores,improvements,position,truth)
            baseline_failed=not np.array_equal(baseline_bits,cached["actual"])
            row.update(case_id=cid,baseline_failure=bool(baseline_failed),role=case["role"],
                nonbaseline_candidates=10446,absolute_L_row_order=True,class_counts_are_posterior_masses=False)
            if case["role"]=="success_control" or row["selected_matches_truth"]:assert row["true_class_present"]
            save(ROOT/"cases"/f"{cid:04d}.json",dict(summary=row,classes=groups))
            np.savez_compressed(ROOT/"cases"/f"{cid:04d}.npz",absolute_class_codes=labels,scores=scores,source_improvements=improvements)
            rows.append(row)
            with (ROOT/"journal.jsonl").open("a") as f:f.write(json.dumps(dict(event="complete",case_id=cid))+"\n")
            print(json.dumps(dict(case_id=cid,completed=len(rows))),flush=True)
            budget()
        status="completed";message="All24 unchanged saved lists classified; no repair or new search"
    except Exception as exc:
        if isinstance(exc,BudgetStop):status="resource_stopped"
        message=f"{type(exc).__name__}: {exc}"
    result=dict(status=status,message=message,cases_completed=len(rows),rows=rows,
        list_members=sum(r["list_members"] for r in rows),nonbaseline_candidates=sum(r["nonbaseline_candidates"] for r in rows),
        child_cpu_seconds=time.process_time()-START_CPU,child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak(),
        frozen_sha256=sha(ROOT/"frozen.json"),new_decoder_calls=0,new_physical_samples=0,new_search_candidates=0,new_fits=0)
    save(ROOT/"analysis_result.json",result)
    print(json.dumps({k:v for k,v in result.items() if k!="rows"}),flush=True)
    if status!="completed":raise SystemExit(1)

if __name__=="__main__":main()
