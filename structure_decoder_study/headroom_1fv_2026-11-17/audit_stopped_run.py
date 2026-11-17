"""Independent audit of saved gate evidence; no reconstruction or decoding."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/"natural_noise_reproduction_2026-11-17"
STUDY=ROOT.parent


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def rank_gf2(matrix):
    a=sp.csr_matrix(matrix);basis={}
    for i in range(a.shape[0]):
        word=sum(1<<int(j) for j,v in zip(a.indices[a.indptr[i]:a.indptr[i+1]],a.data[a.indptr[i]:a.indptr[i+1]]) if int(v)%2)
        while word:
            k=word.bit_length()-1
            if k in basis:word^=basis[k]
            else:basis[k]=word;break
    return len(basis)


def main():
    frozen=read(ROOT/"frozen.json")
    for name,expected in frozen["files"].items():assert sha(Path(name))==expected,name
    assert frozen["version"]==2
    archive=ROOT/"pre_run_v1"
    for name,expected in read(archive/"archive_record.json")["files"].items():assert sha(archive/name)==expected,name
    first=read(archive/"frozen.json")
    assert frozen["supersedes_frozen_sha256"]==sha(archive/"frozen.json")
    assert first["files"][str(ROOT/"experiment.py")]==sha(archive/"experiment.py")
    assert sha(ROOT/"selection.json")==sha(archive/"selection.json")
    for name,expected in first["files"].items():
        if name!=str(ROOT/"experiment.py"):assert frozen["files"][name]==expected
    for key in ("exit_classifier_adapters.json","watchdog_adapters.json","algebra_adapters.json"):
        assert read(ROOT/key)["passed"]
    assert read(ROOT/"exit_classifier_adapters.json")["cases"]==10
    controller,worker=read(ROOT/"controller_result.json"),read(ROOT/"worker_result.json")
    assert controller["returncode"]==0 and controller["watchdog_reason"] is None and controller["monitor_error"] is None
    assert controller["status"]==worker["status"]=="baseline_mismatch"
    assert controller["frozen_sha256"]==worker["frozen_sha256"]==sha(ROOT/"frozen.json")
    assert worker["gates_completed"]==9 and worker["searches_completed"]==0
    assert worker["peak_child_rss_bytes"]<=frozen["limits"]["child_rss_bytes"]
    assert controller["peak_observed_child_rss_bytes"]<=frozen["limits"]["child_rss_bytes"]
    assert worker["child_cpu_seconds"]<600 and controller["wall_seconds"]<900
    assert not (ROOT/"global_gate.json").exists() and list((ROOT/"search").iterdir())==[]
    journal=[json.loads(x) for x in (ROOT/"journal.jsonl").read_text().splitlines()]
    assert not any(r["event"] in ("all_gates_passed","search_start","search_complete") for r in journal)
    gate_events=[r for r in journal if r["event"]=="gate_complete"]
    ids=[r["case_id"] for r in gate_events]
    assert ids==[0,1,2,3,4,5,23,24,51]
    assert [r["case_id"] for r in journal if r["event"]=="gate_start"]==ids
    selected=read(ROOT/"selection.json")
    assert len(selected)==24 and [c["case_id"] for c in selected[:9]]==ids
    events=[json.loads(x) for x in (OLD/"invocations.jsonl").read_text().splitlines()]
    primary=[r for r in events if r["event"]=="complete" and r["phase"]=="main" and r["config"]["name"]=="osd20"]
    failures=sorted(r["case_id"] for r in primary if r["outcome"]=="logical_failure")
    controls=[]
    for block in range(2):controls+=sorted(r["case_id"] for r in primary if r["case_id"]//256==block and r["outcome"]=="correct" and not r["bp_converged"])[:6]
    assert sorted(failures+controls)==[r["case_id"] for r in selected]
    h=sp.load_npz(OLD/"entry/H.npz").tocsc()
    l=sp.load_npz(OLD/"entry/L.npz").tocsc()
    priors=np.load(OLD/"entry/priors.npy")
    checked=[];discrepancy=None
    for event,case in zip(gate_events,selected):
        cid=case["case_id"];metadata=read(Path(case["cached_metadata"]))
        data=np.load(case["cached_npz"]);gate=np.load(ROOT/"gates"/f"{cid:04d}.npz")
        report=read(ROOT/"gates"/f"{cid:04d}.json")
        assert metadata["case_id"]==cid and metadata["config"]["name"]=="osd20" and not metadata["bp_converged"]
        native=data["correction"];solution=gate["solution"];llr=data["llrs"]
        assert hashlib.sha256(native.tobytes()).hexdigest()==metadata["correction_sha256"]
        assert llr.dtype==np.float64 and np.isfinite(llr).all()
        order,pivot=gate["order"],gate["pivot_cols"]
        independent_order=np.asarray(sorted(range(12240),key=lambda j:(float(llr[j]),j)))
        assert np.array_equal(order,independent_order)
        assert len(set(pivot.tolist()))==1794 and rank_gf2(h[:,pivot])==1794
        pivot_mask=np.zeros(12240,dtype=bool);pivot_mask[pivot]=True
        free=order[~pivot_mask[order]]
        assert len(free)==10446 and not solution[free].any()
        reduced=gate["reduced"]
        pivot_bits=((reduced[:,pivot>>6]>>(pivot&63).astype(np.uint64))&np.uint64(1)).astype(np.uint8)
        assert np.array_equal(pivot_bits,np.eye(1794,dtype=np.uint8))
        assert np.array_equal(h@native%2,data["syndrome"]) and np.array_equal(h@solution%2,data["syndrome"])
        changed=np.flatnonzero(native!=solution)
        assert report["baseline_difference"]==event["baseline_difference"]==len(changed)
        assert report["baseline_equal"]==bool(np.array_equal(native,solution))
        assert event["baseline_equal"]==report["baseline_equal"]
        _,inv,counts=np.unique(llr,return_inverse=True,return_counts=True)
        pcounts=np.bincount(inv[pivot_mask],minlength=len(counts))
        assert report["pivot_free_tie_groups"]==int(np.count_nonzero((pcounts>0)&(pcounts<counts)))
        assert abs(report["tie_fraction"]-float(counts[counts>1].sum()/12240))<1e-15
        checked.append(dict(case_id=cid,baseline_difference=len(changed),all1800_constraints_valid=True,pivot_rank=1794))
        if len(changed):
            columns=[]
            for j in changed:
                tied=np.flatnonzero(llr==llr[j])
                columns.append(dict(column=int(j),native_bit=int(native[j]),python_bit=int(solution[j]),
                    llr=float(llr[j]),llr_hex=float(llr[j]).hex(),prior=float(priors[j]),python_pivot=bool(pivot_mask[j]),
                    tie_size=len(tied),tied_pivots=int(pivot_mask[tied].sum()),
                    H_support=h.indices[h.indptr[j]:h.indptr[j+1]].tolist(),L_support=l.indices[l.indptr[j]:l.indptr[j+1]].tolist()))
            xor=native^solution
            discrepancy=dict(case_id=cid,columns=columns,difference_weight=len(changed),
                H_xor_weight=int(np.count_nonzero(h@xor%2)),L_xor_weight=int(np.count_nonzero(l@xor%2)),
                native_wrong_logical_bits=int(np.count_nonzero(l@native%2!=data["actual"])),
                python_wrong_logical_bits=int(np.count_nonzero(l@solution%2!=data["actual"])),
                native_score=float(np.log(1/priors)@native),python_score=float(np.log(1/priors)@solution),
                interpretation="Same syndrome, logical vector and prior-weighted score up to roundoff. Exact tied reliabilities span Python pivots/free columns. Compatible with tie-order ambiguity; native pivot ordering was not observed, so cause is not proven. No rescue occurred.")
    assert all(row["baseline_difference"]==0 for row in checked[:-1])
    assert discrepancy and discrepancy["case_id"]==51 and discrepancy["difference_weight"]==4
    assert discrepancy["H_xor_weight"]==discrepancy["L_xor_weight"]==0
    assert discrepancy["native_wrong_logical_bits"]==discrepancy["python_wrong_logical_bits"]==9
    assert len({r["llr_hex"] for r in discrepancy["columns"]})==1
    assert len({r["prior"] for r in discrepancy["columns"]})==1
    save(ROOT/"baseline_discrepancy.json",discrepancy)
    previous={}
    paths=list(read(OLD/"result_audit.json")["previous_manifests_verified"])+["natural_noise_reproduction_2026-11-17/manifest.json"]
    for name in paths:
        manifest=STUDY/name;files=read(manifest)["files"]
        for relative,expected in files.items():assert sha(manifest.parent/relative)==expected,(name,relative)
        previous[name]=len(files)
    tree=ast.parse((ROOT/"experiment.py").read_text())
    assert not any(isinstance(n,ast.Attribute) and n.attr=="decode" for n in ast.walk(tree))
    report=dict(audit_passed=True,experiment_status="baseline_mismatch",frozen_version=2,
        frozen_files_verified=len(frozen["files"]),v1_preserved_and_scientific_selection_unchanged=True,
        cases_planned=24,gates_completed=9,gates_exact_match=8,mismatch_case=51,cases_unattempted=15,
        real_case_searches=0,new_native_decoder_calls=0,new_physical_shots=0,
        global_gate_respected=True,controller_classification_correct=True,resource_censored=False,
        child_cpu_seconds=worker["child_cpu_seconds"],child_wall_seconds=worker["child_wall_seconds"],
        peak_child_rss_bytes=worker["peak_child_rss_bytes"],completed_gate_checks=checked,
        previous_manifests_verified=previous,frozen_sha256=sha(ROOT/"frozen.json"),audit_source_sha256=sha(Path(__file__)),
        conclusion="Repair-headroom comparison unresolved: baseline adapter mismatch stopped all real searches. Remaining cases did not fail; they were not attempted.")
    save(ROOT/"result_audit.json",report)
    print(json.dumps({k:v for k,v in report.items() if k not in ("completed_gate_checks","previous_manifests_verified")}))


if __name__=="__main__":main()
