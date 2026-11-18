"""Exact original mathematical helpers; no solver transport or CLI."""
import numpy as np
import scipy.sparse as sp
INT_TOL=1e-7

def build_model(h,l,syndrome,truth,weights):
    h=sp.csr_array(h,dtype=np.int64);l=sp.csr_array(l,dtype=np.int64)
    n=h.shape[1];assert l.shape[1]==n
    a=sp.vstack([h,l],format="csr");a.sum_duplicates();a.eliminate_zeros()
    b=np.r_[syndrome,truth].astype(np.int64)
    assert np.isin(a.data,[1]).all() and np.isin(b,[0,1]).all()
    assert len(weights)==n and np.isfinite(weights).all() and np.all(weights>0)
    degree=np.diff(a.indptr);upper=(degree-b)//2
    assert np.all(upper>=0),"Impossible zero-row parity must be handled explicitly"
    matrix=sp.hstack([a,-2*sp.eye(a.shape[0],format="csr",dtype=np.int64)],format="csc")
    # EVERY parity slack is integral; continuous slack would erase parity.
    integrality=np.ones(n+a.shape[0],dtype=np.uint8)
    lower=np.zeros(n+a.shape[0]);upper_bounds=np.r_[np.ones(n),upper]
    objective=np.r_[weights,np.zeros(a.shape[0])]
    return dict(h=h,l=l,a=a,b=b,matrix=matrix,integrality=integrality,lower=lower,upper=upper_bounds,objective=objective,n=n)

def model_witness(model,x):
    x=np.asarray(x)
    assert x.shape==(model["n"],) and np.isin(x,[0,1]).all()
    diff=model["a"]@x.astype(np.int64)-model["b"]
    assert np.all(diff%2==0)
    full=np.r_[x.astype(np.int64),diff//2]
    assert np.all(full>=model["lower"]) and np.all(full<=model["upper"])
    assert np.array_equal(model["matrix"]@full,model["b"])
    return full

def validate_incumbent(model,values):
    if values is None:return None
    values=np.asarray(values,dtype=np.float64)
    assert values.shape==model["objective"].shape and np.isfinite(values).all()
    residual=float(np.max(np.abs(values-np.rint(values))))
    assert residual<=INT_TOL,"Incumbent is not within frozen integer proximity"
    integers=np.rint(values).astype(np.int64)
    assert np.all(integers>=model["lower"]) and np.all(integers<=model["upper"])
    assert np.array_equal(model["matrix"]@integers,model["b"]),"Rounded incumbent violates exact equations"
    x=integers[:model["n"]].astype(np.uint8)
    assert np.array_equal(model_witness(model,x),integers)
    return x,residual,integers
