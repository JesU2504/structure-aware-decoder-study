"""Stress input, exact physical-sample replay, and correction checkpoint audit."""
from pathlib import Path
import hashlib,json,sys,importlib,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from stress import convert
import stim

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cfg=json.loads((ROOT/"run_config.json").read_text())
    for name,expected in cfg["hashes"].items():assert sha(ROOT/name)==expected,name
    lock=json.loads((ROOT/"pre_timing_lock.json").read_text())
    for name,expected in lock["files"].items():assert sha(ROOT/name)==expected,name
    confirmation_lock=json.loads((ROOT/"confirmation_lock.json").read_text())
    for name,expected in confirmation_lock["files"].items():assert sha(ROOT/name)==expected,name
    for module_name in ("ldpc.bplsd_decoder._bplsd_decoder","ldpc.bp_decoder._bp_decoder"):
        module=importlib.import_module(module_name);path=Path(module.__file__)
        assert sha(path)==confirmation_lock["backend_binary_sha256"][path.name]
    for package,version in confirmation_lock["packages"].items():assert importlib.metadata.version(package)==version
    assert sha(ROOT.parent/"study.py")==confirmation_lock["shared_study_sha256"]
    records=json.loads((ROOT/"corpus.json").read_text());checked=shots=checkpoints=0
    phases=["discovery"]
    if (ROOT/"results/confirmation_analysis.json").exists():phases.append("confirmation")
    if (ROOT/"results/boundary_summaries.json").exists():
        phases.append("boundary")
        bc=json.loads((ROOT/"boundary_config.json").read_text())
        for name,expected in bc["hashes"].items():assert sha(ROOT/name)==expected,name
    if (ROOT/"results/feature_box_summaries.json").exists():
        phases.append("feature_box")
        fc=json.loads((ROOT/"feature_box_config.json").read_text())
        for name,expected in fc["hashes"].items():assert sha(ROOT/name)==expected,name
    for phase in phases:
        phase_records=(json.loads((ROOT/"boundary_corpus.json").read_text()) if phase=="boundary" else
                       json.loads((ROOT/"feature_box_corpus.json").read_text()) if phase=="feature_box" else records)
        selected=({r["name"] for r in phase_records} if phase in ("discovery","boundary","feature_box") else
                  set(json.loads((ROOT/"confirmation_selection.json").read_text())["names"]))
        for record in phase_records:
            if record["name"] not in selected:continue
            name=record["name"]
            assert sha(ROOT/"circuits"/f"{name}.stim")==record["circuit_sha256"]
            assert sha(ROOT/"circuits"/f"{name}.dem")==record["dem_sha256"]
            c=stim.Circuit.from_file(str(ROOT/"circuits"/f"{name}.stim"))
            h,l,p,_=convert(c.detector_error_model())
            for session in range(3):
                path=ROOT/"results"/phase/f"session_{session}"/f"{name}.npz"
                a=np.load(path);s=json.loads(path.with_suffix(".json").read_text())
                assert s["config_sha256"]==sha(ROOT/"run_config.json")
                if phase=="feature_box":assert s["phase_config_sha256"]==sha(ROOT/"feature_box_config.json")
                assert len(a["wall_ns"])==s["shots"] and np.all(a["wall_ns"]>0) and np.all(a["cpu_ns"]>0)
                assert np.isclose(np.mean(a["wall_ns"]),s["mean_wall_ns"])
                assert np.isclose(np.quantile(a["wall_ns"],.95),s["p95_wall_ns"])
                det,obs=c.compile_detector_sampler(seed=s["seed"]).sample(s["planned_shots"],separate_observables=True)
                det=det[:s["shots"]];obs=obs[:s["shots"]]
                assert np.array_equal(det.sum(axis=1),a["syndrome_weight"])
                idx=a["checkpoint_indices"];correction=a["checkpoint_corrections"]
                assert np.array_equal(det[idx],a["checkpoint_detectors"])
                assert np.array_equal(obs[idx],a["checkpoint_observables"])
                assert np.array_equal((h@correction.T).T%2,det[idx])
                assert np.array_equal(np.any((l@correction.T).T%2!=obs[idx],axis=1),a["logical_z_failure"][idx])
                checked+=1;shots+=s["shots"];checkpoints+=len(idx)
    out=dict(case_sessions=checked,physical_shots_replayed=shots,correction_checkpoints=checkpoints,
             frozen_hashes=True,physical_replay=True,checkpoint_parity=True,passed=True,
             dependency_binaries_and_versions=True,
             confirmation_snapshot_recorded_after_launch=confirmation_lock["recorded_after_confirmation_launch"],
             external_peer_review=False)
    (ROOT/"results/audit.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out))

if __name__=="__main__":main()
