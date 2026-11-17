"""Independent file/replay/checkpoint audit of the paired component control."""
from pathlib import Path
import hashlib,json
import numpy as np
import scipy.sparse as sp
import stim

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results"/"component_control"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cfg=json.loads((OUT/"config.json").read_text())
    assert sha(ROOT/"component_control.py")==cfg["implementation_sha256"]
    assert sha(ROOT/"COMPONENT_CONTROL_PROTOCOL.md")==cfg["protocol_sha256"]
    assert sha(ROOT/"frozen_config.json")==cfg["primary_config_sha256"]
    config_hash=sha(OUT/"config.json")
    records=[r for r in json.loads((ROOT/"corpus.json").read_text())
             if r["case"]["blocks"]==4 and r["case"]["family"] in ("fanout","repeated")]
    checked=0;checkpoints=0;outcomes=0
    for record in records:
        name=record["name"]
        c=stim.Circuit((ROOT/"circuits"/f"{name}.stim").read_text())
        m=np.load(ROOT/"circuits"/f"{name}.npz")
        h=sp.csc_matrix((m["h_data"],m["h_indices"],m["h_indptr"]),shape=tuple(m["h_shape"]))
        l=sp.csc_matrix((m["l_data"],m["l_indices"],m["l_indptr"]),shape=tuple(m["l_shape"]))
        for session in range(3):
            path=OUT/f"session_{session}"/f"{name}.npz"
            a=np.load(path)
            s=json.loads(path.with_suffix(".json").read_text())
            assert s["config_sha256"]==config_hash
            assert a["latency_ns"].shape==(2,1000)
            assert np.all(a["latency_ns"]>0)
            for mode,prefix in ((0,"joint"),(1,"split")):
                assert np.isclose(a["latency_ns"][mode].mean(),s[f"{prefix}_mean_ns"])
                assert int(a["logical_z_failure"][mode].sum())==s[f"{prefix}_failures"]
            d,o=c.compile_detector_sampler(seed=s["seed"]).sample(1000,separate_observables=True)
            idx=a["checkpoint_indices"]
            assert np.array_equal(d[idx],a["checkpoint_syndromes"])
            assert np.array_equal(o[idx],a["checkpoint_observables"])
            for mode in (0,1):
                correction=a["checkpoint_corrections"][mode]
                assert np.array_equal((h@correction.T).T%2,d[idx])
                failure=np.any((l@correction.T).T%2!=o[idx],axis=1)
                assert np.array_equal(failure,a["logical_z_failure"][mode,idx])
            checked+=1;checkpoints+=2*len(idx);outcomes+=int(np.sum(a["logical_z_failure"][0]!=a["logical_z_failure"][1]))
    result=dict(case_sessions=checked,paired_physical_shots=checked*1000,decode_forms=2,
                checkpoint_corrections=checkpoints,whole_logical_z_failure_outcome_disagreements=outcomes,
                hashes=True,physical_replay=True,checkpoint_parity=True,passed=True)
    (OUT/"audit.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))

if __name__=="__main__":main()
