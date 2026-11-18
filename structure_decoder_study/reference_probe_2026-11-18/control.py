"""Prepare and bound two fixed reference optimization attempts."""
from __future__ import annotations
import os
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[name]="1"
import ast,hashlib,json,platform,signal,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;STUDY=ROOT.parent
DIAG=STUDY/"candidate_class_diagnosis_2026-11-18"
HEAD=STUDY/"headroom_cached_order_2026-11-17";OLD=STUDY/"natural_noise_reproduction_2026-11-17"
import monitor
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def function_source(source,name):
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return "\n".join(source.splitlines()[node.lineno-1:node.end_lineno])

def prepare():
    import numpy as np
    import scipy.sparse as sp
    import scipy.optimize._milp as scipy_milp
    import probe
    assert not (ROOT/"frozen.json").exists(),"Preserve previous plan"
    entry=read(ROOT/"entry_result.json");process=read(ROOT/"entry_process.json")
    assert entry["passed"] and process["returncode"]==0 and process["watchdog_reason"] is None and process["monitor_error"] is None
    assert read(ROOT/"entry_validation_adapters.json")["passed"]
    assert read(ROOT/"entry_validation_adapters.json")["probe_sha256"]==sha(ROOT/"probe.py")
    assert sha(ROOT/"entry_probe_snapshot.py")==entry["probe_sha256"]
    assert sha(ROOT/"entry.py")==entry["entry_sha256"]
    tested=(ROOT/"entry_probe_snapshot.py").read_text();current=(ROOT/"probe.py").read_text()
    for name in ("build_model","model_witness","solve","validate_incumbent"):
        assert function_source(tested,name)==function_source(current,name),name
    for tree_name in ("OPTIONS","INT_TOL","ATOL"):
        def assignment(source):
            node=next(n for n in ast.parse(source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==tree_name or isinstance(t,ast.Tuple) and any(isinstance(e,ast.Name) and e.id==tree_name for e in t.elts) for t in n.targets))
            return ast.dump(node.value)
        assert assignment(tested)==assignment(current),tree_name
    for name,digest in read(DIAG/"manifest.json")["files"].items():assert sha(DIAG/name)==digest,name
    for name,digest in read(DIAG/"frozen.json")["files"].items():assert sha(Path(name))==digest,name
    (ROOT/"inputs").mkdir();(ROOT/"cases").mkdir()
    h_path=OLD/"entry/H.npz";l_path=OLD/"entry/L.npz"
    h=sp.load_npz(h_path).astype(np.int64);l=sp.load_npz(l_path).astype(np.int64)
    priors=np.load(OLD/"entry/priors.npy");weights=np.log(1/priors)
    np.save(ROOT/"weights.npy",weights)
    paths=[ROOT/name for name in ("ENTRY.md","PROTOCOL.md","probe.py","entry.py","entry_probe_snapshot.py","entry_result.json","entry_process.json","entry_validation_adapters.json","entry.log","monitor.py","control.py","audit.py","weights.npy","PREFLIGHT.md")]
    paths += [h_path,l_path,OLD/"entry/priors.npy",DIAG/"manifest.json",DIAG/"frozen.json",DIAG/"analysis_result.json",DIAG/"audit_result.json",HEAD/"selection.json",Path(entry["backend_core_path"]),Path(scipy_milp.__file__)]
    cases=[]
    for cid in (131,228):
        original=next(c for c in read(HEAD/"selection.json") if c["case_id"]==cid)
        cached=np.load(original["cached_npz"]);saved_path=HEAD/"search"/f"{cid:04d}.npz";gate_path=HEAD/"gates"/f"{cid:04d}.npz"
        saved=np.load(saved_path);gate=np.load(gate_path);diagnosis=read(DIAG/"cases"/f"{cid:04d}.json")
        truth=diagnosis["summary"]["true_logical_class"]
        own=next(r for r in diagnosis["classes"] if r["logical_class"]==truth)
        pos=own["first_exact_raw_minimum_position"]
        known=saved["baseline"].copy()
        if pos:known[gate["pivot_cols"]]^=saved["rf"][:,pos-1];known[int(saved["free"][pos-1])]=1
        wrong=saved["correction_full"].copy()
        model=probe.build_model(h,l,cached["syndrome"],cached["actual"],weights)
        probe.model_witness(model,known)
        assert np.array_equal(h@wrong.astype(np.int64)%2,cached["syndrome"])
        assert not np.array_equal(l@wrong.astype(np.int64)%2,cached["actual"])
        wrong_score=float(weights@wrong);known_score=float(weights@known)
        assert abs(known_score-own["minimum_raw_score"])<1e-8
        assert abs(wrong_score-diagnosis["summary"]["selected_score"])<1e-8
        target=ROOT/"inputs"/f"{cid:04d}.npz"
        np.savez_compressed(target,syndrome=cached["syndrome"],actual=cached["actual"],full_1fv_wrong=wrong,known_correct=known)
        cases.append(dict(case_id=cid,input_npz=target.relative_to(ROOT).as_posix(),wrong_score=wrong_score,best_saved_true_score=known_score,known_correct_position=pos,
            original_cached_npz=original["cached_npz"],old_search_npz=str(saved_path.resolve()),old_gate_npz=str(gate_path.resolve())))
        paths += [target,Path(original["cached_npz"]),Path(original["cached_metadata"]),saved_path,gate_path,DIAG/"cases"/f"{cid:04d}.json"]
    frozen=dict(files={str(p.resolve()):sha(p) for p in paths},cases=cases,H_path=str(h_path.resolve()),L_path=str(l_path.resolve()),priors_path=str((OLD/"entry/priors.npy").resolve()),
        solver_options=probe.OPTIONS,versions=entry["versions"],platform=platform.platform(),python=sys.version,
        limits=dict(child_cpu_seconds=90,child_wall_seconds=120,child_rss_bytes=1073741824,audit_cpu_seconds=30,audit_wall_seconds=60),
        integrality_tolerance=probe.INT_TOL,score_atol=probe.ATOL,score_rtol=probe.RTOL,
        actual_logical_target_is_oracle=True,rigorous_lower_bound_branch_enabled=False,reference_calls_entry=4,reference_calls_real_planned=2,
        shared_entry_functions_identical=True,new_BP_OSD_LSD_calls=0,new_physical_shots=0,new_model_fits=0)
    save(ROOT/"frozen.json",frozen)
    print(json.dumps(dict(frozen=True,files=len(frozen["files"]),cases=[131,228],frozen_sha256=sha(ROOT/"frozen.json"))))

def run():
    assert not (ROOT/"process_result.json").exists(),"Preserve previous attempt"
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    # Monitor was exercised by the prior study and the normal entry process.
    expected=dict(returncode=0,watchdog_reason=None,monitor_error=None)
    def passed(process,report):
        return process["returncode"]==0 and process["watchdog_reason"] is None and process["monitor_error"] is None and isinstance(report,dict) and report.get("status")=="completed"
    assert passed(expected,dict(status="completed")) and not passed(dict(expected,returncode=1),dict(status="completed"))
    assert not passed(dict(expected,watchdog_reason="wall_limit"),dict(status="completed")) and not passed(expected,None)
    rows=[]
    for case in frozen["cases"]:
        cid=case["case_id"]
        process=monitor.watch([sys.executable,str(ROOT/"probe.py"),str(cid)],120,1073741824,ROOT/"cases"/f"{cid:04d}.log",echo=True)
        report=read(ROOT/"cases"/f"{cid:04d}.json") if (ROOT/"cases"/f"{cid:04d}.json").exists() else None
        stop=read(ROOT/"cases"/f"{cid:04d}_stop.json") if (ROOT/"cases"/f"{cid:04d}_stop.json").exists() else None
        resource_cause=process["watchdog_reason"] in ("wall_limit","rss_limit") or process["returncode"] in (-signal.SIGXCPU,-signal.SIGKILL) or isinstance(stop,dict) and stop.get("status")=="resource_stopped"
        row=dict(case_id=cid,process=process,completed_normally=passed(process,report),resource_cause=bool(resource_cause),
            classification=report["classification"] if passed(process,report) else "unresolved_resource_or_infrastructure_stop")
        rows.append(row);save(ROOT/"process_result.json",dict(status="running",rows=rows,frozen_sha256=sha(ROOT/"frozen.json")))
        if not row["completed_normally"]:
            if not resource_cause:break
    save(ROOT/"process_result.json",dict(status="completed" if len(rows)==2 else "stopped",rows=rows,frozen_sha256=sha(ROOT/"frozen.json")))
    output=[ROOT/"process_result.json"]+list((ROOT/"cases").iterdir())
    if (ROOT/"reference_invocations.jsonl").exists():output.append(ROOT/"reference_invocations.jsonl")
    save(ROOT/"output_manifest.json",dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in output if p.is_file()}))
    print(json.dumps(dict(attempted=len(rows),normal_completions=sum(r["completed_normally"] for r in rows))),flush=True)

def audit():
    assert not (ROOT/"audit_process.json").exists(),"Preserve previous audit"
    p=monitor.watch([sys.executable,str(ROOT/"audit.py")],60,1073741824,ROOT/"audit.log",echo=True)
    r=read(ROOT/"audit_result.json") if (ROOT/"audit_result.json").exists() else None
    p["passed"]=bool(p["returncode"]==0 and p["watchdog_reason"] is None and p["monitor_error"] is None and isinstance(r,dict) and r.get("passed") is True)
    save(ROOT/"audit_process.json",p);print(json.dumps(p),flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","run","audit"):raise SystemExit("Usage: control.py prepare|run|audit")
    {"prepare":prepare,"run":run,"audit":audit}[sys.argv[1]]()
