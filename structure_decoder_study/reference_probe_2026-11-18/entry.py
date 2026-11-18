"""Exhaustive tiny-instance backend validation, before any real optimization."""
import os
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[name]="1"
import itertools,json,resource,time
from pathlib import Path
import importlib.metadata as metadata
import numpy as np
import scipy.sparse as sp
import scipy.optimize._highspy._core as hc
import probe
ROOT=Path(__file__).resolve().parent

def main():
    assert not (ROOT/"entry_result.json").exists(),"Preserve entry evidence"
    resource.setrlimit(resource.RLIMIT_CPU,(15,20))
    cases=[
        ("integral_slack_required",[[1,1],[1,1]],[[1,0]],[0,0],[1],[1.,3.]),
        ("dependent_cyclic",[[1,1,0,1,1],[0,1,1,0,0],[1,0,1,1,1]],[[0,0,0,1,1],[0,0,1,1,1]],[1,0,1],[1,0],[1.,2.,3.,4.,5.]),
        ("zero_syndrome",[[1,0,1,1],[0,1,1,0]],[[1,1,0,0]],[0,0],[0],[1.,2.,3.,4.]),
        ("inconsistent_duplicate_rows",[[1,1,0],[1,1,0]],[[0,0,1]],[0,1],[0],[1.,2.,3.])]
    rows=[];started=time.monotonic()
    for name,h,l,s,t,w in cases:
        h=np.asarray(h,dtype=np.int64);l=np.asarray(l,dtype=np.int64);s=np.asarray(s,dtype=np.int64);t=np.asarray(t,dtype=np.int64);w=np.asarray(w)
        valid=[]
        for bits in itertools.product([0,1],repeat=h.shape[1]):
            x=np.asarray(bits,dtype=np.uint8)
            if np.array_equal(h@x%2,s) and np.array_equal(l@x%2,t):valid.append((float(w@x),x))
        model=probe.build_model(h,l,s,t,w)
        options=dict(probe.OPTIONS,time_limit=2.,node_limit=1000,disp=False)
        result,warnings=probe.solve(model,options)
        if valid:
            expected=min(v[0] for v in valid)
            assert result.status==0 and abs(result.fun-expected)<1e-9
            checked=probe.validate_incumbent(model,result.x);assert checked is not None
            assert abs(float(w@checked[0])-expected)<1e-9
            for _,x in valid:probe.model_witness(model,x)
        else:
            expected=None;assert result.status==2
        rows.append(dict(name=name,enumerated_binary_vectors=2**h.shape[1],feasible_vectors=len(valid),exhaustive_minimum=expected,solver_status=int(result.status),passed=True,warnings=warnings))
    result=dict(passed=True,adapter_reference_optimization_calls=len(rows),real_case_reference_optimization_calls=0,rows=rows,
        versions=dict(scipy=metadata.version("scipy"),numpy=metadata.version("numpy"),bundled_highs=hc._Highs().version()),
        probe_sha256=probe.sha(ROOT/"probe.py"),entry_sha256=probe.sha(Path(__file__)),wall_seconds=time.monotonic()-started,
        backend_core_path=hc.__file__,backend_core_sha256=probe.sha(Path(hc.__file__)),
        parity_domains_all_integral=True,numerical_bounds_are_not_certificates=True)
    probe.save(ROOT/"entry_result.json",result);print(json.dumps(result,indent=2))

if __name__=="__main__":main()
