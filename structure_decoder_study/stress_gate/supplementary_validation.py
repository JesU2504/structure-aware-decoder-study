"""CSS/logical algebra and source TICK-disjointness checks; no timing claim."""
from pathlib import Path
import json
import numpy as np
import stim
from stress import ROOT,code

def rank(a):
    a=a.astype(np.uint8).copy();r=0
    for j in range(a.shape[1]):
        hit=np.flatnonzero(a[r:,j])
        if not len(hit):continue
        k=r+int(hit[0]);a[[r,k]]=a[[k,r]]
        for i in range(a.shape[0]):
            if i!=r and a[i,j]:a[i]^=a[r]
        r+=1
        if r==len(a):break
    return r

def main():
    checks=[]
    for d in (3,5,7,9):
        c=code(d).css
        assert not np.any(c.hx@c.hz.T%2)
        assert not np.any(c.hx@c.lz.T%2) and not np.any(c.hz@c.lx.T%2)
        assert np.array_equal(c.lx@c.lz.T%2,np.eye(1,dtype=np.uint8))
        rx,rz=rank(c.hx),rank(c.hz);assert d*d-rx-rz==1
        checks.append(dict(distance=d,rank_x=rx,rank_z=rz,encoded_qubits=1,passed=True))
    gates={"CX","H","X","Y","Z","S","I","R","RX","MR","MRX","M","MX"}
    conflicts=[];files=list((ROOT/"circuits").glob("*.stim"))
    for path in files:
        seen=set()
        for i,inst in enumerate(stim.Circuit.from_file(str(path))):
            if inst.name=="TICK":seen.clear()
            elif inst.name in gates:
                for target in inst.targets_copy():
                    q=target.value
                    if q in seen:conflicts.append(dict(case=path.stem,instruction=i,qubit=q))
                    seen.add(q)
    result=dict(distance_code_checks=checks,circuit_files=len(files),nonnoise_gate_reuse_within_tick=conflicts,
                check_scope="CSS/logical algebra and source TICK disjointness; not a full physical timing model or distance proof")
    (ROOT/"results/supplementary_validation.json").write_text(json.dumps(result,indent=2)+"\n")
    assert not conflicts
    print(json.dumps(dict(distances_checked=len(checks),circuits_checked=len(files),tick_conflicts=len(conflicts))))

if __name__=="__main__":main()
