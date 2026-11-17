"""Independent raw-file, sample-replay, and checkpoint audit for Stage 1."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import scipy.sparse as sp
import stim

ROOT=Path(__file__).resolve().parent


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cfg=json.loads((ROOT/"frozen_config.json").read_text())
    assert sha(ROOT/"PROTOCOL.md")==cfg["protocol_sha256"]
    assert sha(ROOT/"corpus.json")==cfg["corpus_sha256"]
    assert sha(ROOT/"study.py")==cfg["implementation_sha256"]
    assert sha(ROOT/"analyze.py")==cfg["analysis_sha256"]
    amendment=json.loads((ROOT/"analysis_amendment.json").read_text())
    for path,expected in amendment["hashes"].items():
        assert sha(ROOT/path)==expected,path
    assert sha(ROOT/"source_manifest.json")==cfg["source_manifest_sha256"]
    source=json.loads((ROOT/"source_manifest.json").read_text())
    folder=ROOT/"sources"/"basilthebeagles-tmcbs-c0490fa"
    for path,expected in source["files"].items():
        assert sha(folder/path)==expected,path
    assert sha(ROOT/"sources"/"tmcbs-c0490fa.tar.gz")==source["archive_sha256"]
    records=json.loads((ROOT/"corpus.json").read_text())
    checks=[]
    for record in records:
        name=record["name"]
        assert sha(ROOT/"circuits"/f"{name}.stim")==record["circuit_sha256"]
        assert sha(ROOT/"circuits"/f"{name}.dem")==record["dem_sha256"]
        c=stim.Circuit((ROOT/"circuits"/f"{name}.stim").read_text())
        m=np.load(ROOT/"circuits"/f"{name}.npz")
        h=sp.csc_matrix((m["h_data"],m["h_indices"],m["h_indptr"]),shape=tuple(m["h_shape"]))
        l=sp.csc_matrix((m["l_data"],m["l_indices"],m["l_indptr"]),shape=tuple(m["l_shape"]))
        for session in range(cfg["sessions"]):
            path=ROOT/"results"/f"session_{session}"/f"{name}.npz"
            a=np.load(path)
            summary=json.loads(path.with_suffix(".json").read_text())
            assert len(a["latency_ns"])==cfg["shots"]
            assert np.all(a["latency_ns"]>0)
            assert not a["invalid_correction"].any()
            assert summary["config_sha256"]==sha(ROOT/"frozen_config.json")
            assert summary["implementation_sha256"]==cfg["implementation_sha256"]
            assert np.isclose(np.mean(a["latency_ns"]),summary["mean_ns"])
            assert np.isclose(np.quantile(a["latency_ns"],.95),summary["p95_ns"])
            assert int(a["logical_z_failure"].sum())==summary["logical_z_failures"]
            # Re-sample the original physical circuit from its persisted seed,
            # independently of the benchmark's conversion/measurement loop.
            detectors,observables=c.compile_detector_sampler(seed=summary["seed"]).sample(cfg["shots"],separate_observables=True)
            assert np.array_equal(detectors.sum(axis=1),a["syndrome_weight"])
            idx=a["checkpoint_indices"]
            assert np.array_equal(detectors[idx],a["checkpoint_detectors"])
            assert np.array_equal(observables[idx],a["checkpoint_observables"])
            correction=a["checkpoint_corrections"]
            assert np.array_equal((h@correction.T).T%2,detectors[idx])
            fail=np.any((l@correction.T).T%2!=observables[idx],axis=1)
            assert np.array_equal(fail,a["logical_z_failure"][idx])
            checks.append(dict(name=name,session=session,shots=cfg["shots"],checkpoints=len(idx),passed=True))
    report=dict(cases=len(records),case_sessions=len(checks),sampled_shots_replayed=sum(x["shots"] for x in checks),
                correction_checkpoints=sum(x["checkpoints"] for x in checks),source_files_checked=len(source["files"]),
                input_hashes=True,implementation_hashes=True,analysis_amendment_hashes=True,checks=checks)
    (ROOT/"results"/"audit.json").write_text(json.dumps(report,indent=2)+"\n")
    manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob("*")) if p.is_file()
              and not any(x in ("__pycache__",".pytest_cache") for x in p.relative_to(ROOT).parts)
              and p.name!="manifest.json" and not p.name.endswith(".tmp")}
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="checks"}))


if __name__=="__main__":main()
