"""Verify public-export bytes and independently recompute recorded outcomes."""
from pathlib import Path
import hashlib,json
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/"structure_decoder_study"


def main():
    export=json.loads((ROOT/"PUBLIC_EXPORT.json").read_text())
    for name,record in export["files"].items():
        p=ROOT/name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==record["sha256"],name
    base=STUDY/"natural_noise_reproduction_2026-11-17"
    h=sp.load_npz(base/"entry/H.npz");l=sp.load_npz(base/"entry/L.npz")
    main_counts={x:dict(correct=0,logical_failure=0,invalid_correction=0) for x in ["osd20","lsd30","lsd100"]}
    calls=0
    for path in sorted((base/"calls").glob("*.json")):
        row=json.loads(path.read_text());data=np.load(path.with_suffix(".npz"))
        if row["phase"]=="adapter_toy":
            hm=np.array([[1,1,0],[0,1,1]],dtype=np.uint8);lm=np.array([[1,1,1]],dtype=np.uint8)
        else:hm,lm=h,l
        bad_s=np.count_nonzero(hm@data["correction"]%2!=data["syndrome"])
        bad_l=np.count_nonzero(lm@data["correction"]%2!=data["actual"])
        outcome="invalid_correction" if bad_s else "logical_failure" if bad_l else "correct"
        assert outcome==row["outcome"],str(path)
        if row["phase"]=="main":main_counts[row["config"]["name"]][outcome]+=1
        calls+=1
    assert calls==1627
    assert all(x==dict(correct=500,logical_failure=12,invalid_correction=0) for x in main_counts.values())
    diagnostic=STUDY/"ordering_diagnostic_2026-11-17"
    selection=json.loads((diagnostic/"frozen.json").read_text())["selection"]
    stable=native=0
    for case in selection:
        cached_path=str(case["cached_npz"]).replace("<WORKSPACE>/","")
        cached=np.load(ROOT/cached_path)
        output=np.load(diagnostic/"cases"/f"{case['case_id']:04d}.npz")
        for name in ("stable_solution","native_order_solution"):
            assert np.array_equal(h@output[name]%2,cached["syndrome"])
        stable+=int(np.array_equal(output["stable_solution"],cached["correction"]))
        native+=int(np.array_equal(output["native_order_solution"],cached["correction"]))
    assert stable==23 and native==24
    print(json.dumps(dict(passed=True,export_files=len(export["files"]),saved_calls_checked=calls,
                          main_counts=main_counts,ordering_matches=dict(stable=stable,native_sort_equivalent=native),
                          new_decoder_calls=0)))


if __name__=="__main__":main()
