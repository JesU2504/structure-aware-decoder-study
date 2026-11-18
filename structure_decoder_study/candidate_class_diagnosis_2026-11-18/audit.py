"""Independent explicit-vector verification of the saved-list class diagnosis."""
from __future__ import annotations
import os,time
START_CPU,START_WALL=time.process_time(),time.monotonic()
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[k]="1"
import hashlib,json,resource,signal,sys
from pathlib import Path
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parent;STUDY=ROOT.parent
HEAD=STUDY/"headroom_cached_order_2026-11-17";OLD=STUDY/"natural_noise_reproduction_2026-11-17"
CHECKED_CASES=0
class BudgetStop(Exception):pass
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def peak():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform=="darwin" else value*1024)
def check_budget():
    if time.process_time()-START_CPU>=600:raise BudgetStop("Audit CPU limit")
    if time.monotonic()-START_WALL>=900:raise BudgetStop("Audit wall limit")
    if peak()>1073741824:raise BudgetStop("Audit RSS limit")
def close(a,b):return abs(a-b)<=1e-8+1e-12*max(abs(a),abs(b))
def encode(bits):
    # Independent byte packing, rather than primary powers-of-two dot product.
    bits=np.asarray(bits,dtype=np.uint8)
    assert bits.shape[0]==12 and np.isin(bits,[0,1]).all()
    packed=np.packbits(bits.T,axis=1,bitorder="little")
    return packed[:,0].astype(np.uint16)+(packed[:,1].astype(np.uint16)<<8)

def main():
    global CHECKED_CASES
    assert not (ROOT/"audit_result.json").exists(),"Preserve previous verification"
    resource.setrlimit(resource.RLIMIT_CPU,(600,605))
    def cpu_stop(_s,_f):raise BudgetStop("Audit CPU limit")
    signal.signal(signal.SIGXCPU,cpu_stop)
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    for name,digest in read(ROOT/"analysis_output_manifest.json")["files"].items():assert sha(ROOT/name)==digest,name
    process=read(ROOT/"analysis_process.json");analysis=read(ROOT/"analysis_result.json")
    assert process["passed"] and process["returncode"]==0 and process["watchdog_reason"] is None and process["monitor_error"] is None
    assert analysis["status"]=="completed" and analysis["cases_completed"]==24
    assert analysis["list_members"]==250728 and analysis["nonbaseline_candidates"]==250704
    assert analysis["frozen_sha256"]==sha(ROOT/"frozen.json")
    assert analysis["child_cpu_seconds"]<600 and process["wall_seconds"]<900
    assert max(analysis["peak_child_rss_bytes"],process["peak_observed_child_rss_bytes"])<=1073741824
    assert read(ROOT/"algebra_adapters.json")["passed"] and read(ROOT/"watchdog_adapters.json")["passed"]
    selected=read(HEAD/"selection.json");assert selected==frozen["cases"]
    ids=[c["case_id"] for c in selected]
    assert len(analysis["rows"])==24 and [r["case_id"] for r in analysis["rows"]]==ids
    journal=[json.loads(line) for line in (ROOT/"journal.jsonl").read_text().splitlines()]
    assert [(e["event"],e["case_id"]) for e in journal]==[(ev,cid) for cid in ids for ev in ("start","complete")]
    h=sp.load_npz(OLD/"entry/H.npz").astype(np.int64).tocsr()
    l=sp.load_npz(OLD/"entry/L.npz").astype(np.int64).tocsr()
    weight=np.log(1/np.load(OLD/"entry/priors.npy"))
    assert h.shape==(1800,12240) and l.shape==(12,12240)
    all_codes=np.arange(4096,dtype=np.uint16)
    bits=np.array([[(int(code)>>j)&1 for code in all_codes] for j in range(12)],dtype=np.uint8)
    assert np.array_equal(encode(bits),all_codes)
    previous_rows={r["case_id"]:r for r in read(HEAD/"result_audit.json")["rows"]}
    verified=[];diagnoses={};max_score_error=0.;raw_min_identity_differences=0
    for case,row in zip(selected,analysis["rows"]):
        check_budget();cid=case["case_id"]
        meta=read(Path(case["cached_metadata"]));assert meta["case_id"]==cid and meta["config"]["name"]=="osd20"
        original=np.load(case["cached_npz"]);gate=np.load(HEAD/"gates"/f"{cid:04d}.npz")
        saved=np.load(HEAD/"search"/f"{cid:04d}.npz");new=np.load(ROOT/"cases"/f"{cid:04d}.npz")
        reported=read(ROOT/"cases"/f"{cid:04d}.json");assert reported["summary"]==row and row["case_id"]==cid
        e0=saved["baseline"];piv=gate["pivot_cols"];free=saved["free"];rf=saved["rf"];delta=saved["delta"]
        assert len(free)==10446 and len(set(piv.tolist()))==1794 and len(set(free.tolist()))==10446
        assert not set(piv.tolist())&set(free.tolist()) and not e0[free].any()
        assert np.array_equal(e0,gate["solution"]) and np.array_equal(e0,original["correction"])
        assert np.array_equal(h@e0%2,original["syndrome"])
        labels=np.empty(10447,dtype=np.uint16);direct=np.empty(10447,dtype=np.float64)
        labels[0]=encode((l@e0%2)[:,None])[0];direct[0]=float(weight@e0)
        for start in range(0,10446,128):
            check_budget();end=min(start+128,10446)
            x=np.repeat(e0[:,None],end-start,axis=1)
            x[piv,:]=np.bitwise_xor(e0[piv,None],rf[:,start:end])
            x[free[start:end],np.arange(end-start)]=1
            assert np.all(h@x.astype(np.int64)%2==original["syndrome"][:,None])
            labels[start+1:end+1]=encode(l@x.astype(np.int64)%2)
            direct[start+1:end+1]=weight@x.astype(np.float64)
        assert np.array_equal(labels,new["absolute_class_codes"])
        canonical=np.r_[float(weight@e0),saved["direct_scores"]];improvements=np.r_[0.,delta]
        assert np.array_equal(canonical,new["scores"]) and np.array_equal(improvements,new["source_improvements"])
        assert np.isfinite(canonical).all() and np.allclose(canonical,direct,atol=1e-8,rtol=1e-12)
        err=float(np.max(np.abs(canonical-direct)));max_score_error=max(max_score_error,err)
        # Independent Python first-maximum policy, including the no-change rule.
        best=max(range(10446),key=lambda j:float(delta[j]))
        chosen=best+1 if float(delta[best])>0 else 0
        expected=e0.copy()
        if chosen:expected[piv]^=rf[:,chosen-1];expected[int(free[chosen-1])]=1
        assert np.array_equal(expected,saved["correction_full"])
        assert chosen==row["selected_position"] and int(labels[chosen])==row["selected_logical_class"]
        assert row["selected_score"]==float(canonical[chosen])
        truth=int(encode(original["actual"][:,None])[0]);assert truth==row["true_logical_class"]
        assert bool(labels[0]!=truth)==row["baseline_failure"] and row["role"]==case["role"]
        groups={}
        for pos,(label,score,imp) in enumerate(zip(labels,canonical,improvements)):
            code=int(label)
            if code not in groups:groups[code]=dict(positions=[],scores=[],improvements=[],direct=[])
            g=groups[code];g["positions"].append(pos);g["scores"].append(float(score));g["improvements"].append(float(imp));g["direct"].append(float(direct[pos]))
        class_records={r["logical_class"]:r for r in reported["classes"]}
        assert set(class_records)==set(groups) and row["represented_classes"]==len(groups)
        assert sum(r["count"] for r in class_records.values())==10447
        for code,g in groups.items():
            r=class_records[code];mini=min(range(len(g["positions"])),key=lambda i:g["scores"][i])
            maxi=max(range(len(g["positions"])),key=lambda i:g["improvements"][i])
            independent_min=min(range(len(g["positions"])),key=lambda i:g["direct"][i])
            assert r["count"]==len(g["positions"]) and r["minimum_raw_score"]==g["scores"][mini]
            assert r["first_exact_raw_minimum_position"]==g["positions"][mini]
            assert close(r["minimum_raw_score"],g["direct"][independent_min])
            raw_min_identity_differences+=g["positions"][mini]!=g["positions"][independent_min]
            assert r["source_best_position"]==g["positions"][maxi] and r["source_best_delta"]==g["improvements"][maxi]
            assert r["source_best_raw_score"]==g["scores"][maxi]
            assert r["exact_raw_minimum_count"]==sum(v==g["scores"][mini] for v in g["scores"])
            assert r["exact_source_best_count"]==sum(v==g["improvements"][maxi] for v in g["improvements"])
        present=truth in groups;correct=int(labels[chosen])==truth
        diagnosis="source_success" if correct else "correct_class_present_but_not_selected" if present else "correct_class_absent_from_saved_list"
        assert row["diagnosis"]==diagnosis and row["selected_matches_truth"]==correct
        assert row["true_class_present"]==present and row["true_class_count"]==(len(groups[truth]["positions"]) if present else 0)
        assert correct==(not previous_rows[cid]["outcomes"]["full"]["logical_failure"])
        if case["role"]=="success_control" or correct:assert present
        others=[code for code in groups if code!=truth]
        competitor=min(others,key=lambda code:(min(groups[code]["scores"]),code)) if others else None
        assert row["best_competing_class"]==competitor
        comp_min=min(groups[competitor]["scores"]) if competitor is not None else None
        assert row["best_competing_score"]==comp_min
        true_min=min(groups[truth]["scores"]) if present else None
        assert row["true_class_minimum_score"]==true_min
        gap=true_min-comp_min if true_min is not None and comp_min is not None else None
        assert row["true_minus_best_competing_gap"]==gap
        reason="correct_class_absent" if not present else "no_competing_class" if not others else None
        assert row["undefined_margin_reason"]==reason
        sensitive=bool(gap is not None and close(true_min,comp_min))
        assert row["true_competitor_numerically_sensitive"]==sensitive
        if gap is not None and not sensitive:assert (gap<0)==correct
        global_min=min(canonical);near=sorted(code for code,g in groups.items() if close(min(g["scores"]),global_min))
        assert row["raw_minimum_classes"]==near
        assert row["source_maximum_delta"]==float(max(improvements))
        assert row["source_exact_best_count"]==int(np.count_nonzero(improvements==max(improvements)))
        assert row["list_members"]==10447 and row["nonbaseline_candidates"]==10446
        assert row["class_counts_are_posterior_masses"] is False and row["absolute_L_row_order"] is True
        diagnoses[diagnosis]=diagnoses.get(diagnosis,0)+1
        verified.append(dict(case_id=cid,diagnosis=diagnosis,true_class_present=present,represented_classes=len(groups),
            true_minus_best_competing_gap=gap,max_direct_score_error=err))
        CHECKED_CASES=len(verified)
        print(json.dumps(dict(audited_case=cid,cases_completed=len(verified))),flush=True)
    previous={}
    names=list(read(HEAD/"result_audit.json")["previous_manifests_verified"])+["headroom_cached_order_2026-11-17/manifest.json"]
    for name in names:
        p=STUDY/name
        for relative,digest in read(p)["files"].items():assert sha(p.parent/relative)==digest,(name,relative)
        previous[name]=sha(p)
    check_budget()
    assert len(verified)==24 and sum(diagnoses.values())==24
    result=dict(status="completed",passed=True,cases_completed=len(verified),rows=verified,diagnoses=diagnoses,
        all_list_members_verified=len(verified)*10447,nonbaseline_candidates_verified=len(verified)*10446,source_winners_unchanged=True,
        all1800_H_rows_and12_L_rows_checked=True,logical_encoding_roundtrip4096=True,
        all_class_counts_and_minima_checked=True,max_direct_score_error=max_score_error,
        raw_minimum_representative_identity_differences_within_tolerance=raw_min_identity_differences,
        previous_result_manifests_verified=previous,new_decoder_calls=0,new_physical_samples=0,new_search_candidates=0,new_fits=0,
        child_cpu_seconds=time.process_time()-START_CPU,child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak(),
        frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)))
    save(ROOT/"audit_result.json",result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("rows","previous_result_manifests_verified")}))

if __name__=="__main__":
    try:main()
    except BudgetStop as exc:
        save(ROOT/"audit_result.json",dict(status="resource_stopped",passed=False,message=str(exc),cases_completed=CHECKED_CASES,
            child_cpu_seconds=time.process_time()-START_CPU,child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak()))
        raise SystemExit(1)
