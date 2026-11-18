"""No solver/helper imports: exact sparse parity and represented-cost checks."""
from __future__ import annotations
import os,time
START_CPU,START_WALL=time.process_time(),time.monotonic()
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[name]="1"
import hashlib,json,math,resource,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
import scipy.sparse as sp
ROOT=Path(__file__).resolve().parent;STUDY=ROOT.parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def cost_fraction(w,x):
    result=Fraction(0)
    for j,bit in enumerate(x):
        if bit:result+=Fraction.from_float(float(w[j]))
    return result
def main():
    resource.setrlimit(resource.RLIMIT_CPU,(30,35))
    assert not (ROOT/"audit_result.json").exists(),"Preserve audit"
    f=read(ROOT/"frozen.json")
    for name,digest in f["files"].items():assert sha(Path(name))==digest,name
    for name,digest in read(ROOT/"output_manifest.json")["files"].items():assert sha(ROOT/name)==digest,name
    result=read(ROOT/"process_result.json")
    assert result["frozen_sha256"]==sha(ROOT/"frozen.json")
    assert 1<=len(result["rows"])<=2 and [r["case_id"] for r in result["rows"]]==[131,228][:len(result["rows"])]
    h=sp.load_npz(Path(f["H_path"])).astype(np.int64).tocsr();l=sp.load_npz(Path(f["L_path"])).astype(np.int64).tocsr()
    w=np.load(ROOT/"weights.npy");assert np.array_equal(w,np.log(1/np.load(f["priors_path"])))
    a=sp.vstack([h,l],format="csr")
    journal=[json.loads(line) for line in (ROOT/"reference_invocations.jsonl").read_text().splitlines()] if (ROOT/"reference_invocations.jsonl").exists() else []
    starts=[r["case_id"] for r in journal if r["event"]=="start"]
    attempted=[r["case_id"] for r in result["rows"]]
    states={cid:0 for cid in attempted};event_order=[]
    for event in journal:
        cid=event["case_id"];assert cid in states
        event_order.append(attempted.index(cid))
        if event["event"]=="start":assert states[cid]==0;states[cid]=1
        elif event["event"]=="solver_returned":assert states[cid]==1;states[cid]=2
        else:raise AssertionError("Unknown invocation event")
    assert event_order==sorted(event_order)
    verified=[]
    for process_row in result["rows"]:
        cid=process_row["case_id"];case=next(c for c in f["cases"] if c["case_id"]==cid)
        inputs=np.load(ROOT/case["input_npz"]);original=np.load(case["original_cached_npz"]);old=np.load(case["old_search_npz"]);gate=np.load(case["old_gate_npz"])
        assert np.array_equal(inputs["syndrome"],original["syndrome"]) and np.array_equal(inputs["actual"],original["actual"])
        wrong=inputs["full_1fv_wrong"];known=inputs["known_correct"]
        assert np.array_equal(wrong,old["correction_full"])
        assert np.array_equal(h@wrong%2,inputs["syndrome"]) and not np.array_equal(l@wrong%2,inputs["actual"])
        target=np.r_[inputs["syndrome"],inputs["actual"]].astype(np.int64)
        assert np.isin(known,[0,1]).all() and np.array_equal(a@known%2,target)
        upper=(np.diff(a.indptr)-target)//2
        known_slack=(a@known-target)//2
        assert np.all(known_slack>=0) and np.all(known_slack<=upper)
        assert np.array_equal(a@known-2*known_slack,target)
        process=process_row["process"]
        if not process_row["completed_normally"]:
            assert process_row["classification"]=="unresolved_resource_or_infrastructure_stop"
            verified.append(dict(case_id=cid,classification=process_row["classification"],no_exclusion_claim=True));continue
        report=read(ROOT/"cases"/f"{cid:04d}.json")
        raw_metadata=read(ROOT/"cases"/f"{cid:04d}_raw_metadata.json")
        assert process["returncode"]==0 and process["watchdog_reason"] is None and process["monitor_error"] is None
        assert report["status"]=="completed" and report["case_id"]==cid and report["frozen_sha256"]==sha(ROOT/"frozen.json")
        assert report["solver_status"] in (0,1) and report["solver_status"]==raw_metadata["solver_status"]
        assert report["child_cpu_seconds"]<90 and report["child_wall_seconds"]<120 and report["peak_child_rss_bytes"]<=1073741824
        assert process["peak_observed_child_rss_bytes"]<=1073741824 and process["wall_seconds"]<120
        assert report["rigorous_lower_bound_available"] is False and report["oracle_logical_target_used"] is True
        assert report["new_reference_optimization_calls"]==1 and report["new_BP_OSD_LSD_calls"]==report["new_physical_shots"]==0
        assert sum(r["event"]=="start" and r["case_id"]==cid for r in journal)==1
        assert sum(r["event"]=="solver_returned" and r["case_id"]==cid for r in journal)==1
        if not report["incumbent_valid"]:
            assert report["solver_status"]==1 and raw_metadata["incumbent_returned"] is False
            assert not (ROOT/"cases"/f"{cid:04d}_raw.npz").exists()
            assert report["classification"]==process_row["classification"]=="unresolved_no_verified_better_witness"
            verified.append(dict(case_id=cid,classification=report["classification"],no_exclusion_claim=True));continue
        values=np.load(ROOT/"cases"/f"{cid:04d}_solver.npz")
        raw=values["raw_solution"];integers=values["integer_solution"];x=values["correction"]
        assert np.array_equal(raw,np.load(ROOT/"cases"/f"{cid:04d}_raw.npz")["raw_solution"])
        assert raw.shape==(14052,) and np.isfinite(raw).all()
        proximity=float(np.max(np.abs(raw-np.rint(raw))))
        assert proximity<=1e-7 and proximity==report["incumbent_integer_proximity"]
        assert np.array_equal(integers,np.rint(raw).astype(np.int64)) and np.array_equal(x,integers[:12240])
        assert np.isin(x,[0,1]).all() and np.array_equal(a@x%2,target)
        slack=integers[12240:]
        assert np.all(slack>=0) and np.all(slack<=upper) and np.array_equal(a@x-2*slack,target)
        new_cost=math.fsum(float(v) for v,bit in zip(w,x) if bit);wrong_cost=math.fsum(float(v) for v,bit in zip(w,wrong) if bit)
        difference=cost_fraction(w,wrong)-cost_fraction(w,x)
        tol=1e-8+1e-12*max(abs(new_cost),abs(wrong_cost))
        assert abs(new_cost-report["incumbent_score"])<=tol and new_cost==report["incumbent_score_fsum"]
        assert wrong_cost==report["wrong_score_fsum"] and abs(wrong_cost-case["wrong_score"])<=tol
        assert difference==Fraction(int(report["exact_float_weight_improvement"]["numerator"]),int(report["exact_float_weight_improvement"]["denominator"]))
        better=difference>Fraction.from_float(tol)
        expected="verified_outside_list_competitive_witness" if better else "unresolved_no_verified_better_witness"
        assert expected==report["classification"]==process_row["classification"]
        free_weight=int(x[old["free"]].sum());outside=free_weight>1
        if not outside:
            candidate=old["baseline"].copy();occupied=np.flatnonzero(x[old["free"]])
            if len(occupied):
                j=int(occupied[0]);candidate[gate["pivot_cols"]]^=old["rf"][:,j];candidate[int(old["free"][j])]=1
            outside=not np.array_equal(candidate,x)
        if better:
            assert outside and new_cost<case["best_saved_true_score"]-tol
        verified.append(dict(case_id=cid,classification=expected,new_score=new_cost,wrong_full_1fv_score=wrong_cost,
            improvement=float(difference),outside_saved_list=outside,nonzero_old_free_coordinates=free_weight,
            all_H_and_L_equations_valid=True,exact_represented_weight_cost_checked=True,no_exclusion_claim=True))
    prior={};d=STUDY/"candidate_class_diagnosis_2026-11-18"
    paths=list(read(d/"audit_result.json")["previous_result_manifests_verified"])+["candidate_class_diagnosis_2026-11-18/manifest.json"]
    for name in paths:
        p=STUDY/name
        for relative,digest in read(p)["files"].items():assert sha(p.parent/relative)==digest,(name,relative)
        prior[name]=sha(p)
    assert time.process_time()-START_CPU<30 and time.monotonic()-START_WALL<60
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;peak=int(peak if sys.platform=="darwin" else peak*1024)
    assert peak<=1073741824
    report=dict(passed=True,rows=verified,real_reference_calls_started=len(starts),entry_reference_calls=4,new_BP_OSD_LSD_calls=0,new_physical_shots=0,
        oracle_assisted_analysis=True,rigorous_exclusion_claims=0,previous_manifests_verified=prior,
        frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)),child_cpu_seconds=time.process_time()-START_CPU,
        child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak)
    save(ROOT/"audit_result.json",report)
    print(json.dumps({k:v for k,v in report.items() if k!="previous_manifests_verified"}),flush=True)

if __name__=="__main__":main()
