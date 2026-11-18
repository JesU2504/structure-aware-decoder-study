"""Existing HiGHS optimizer, standard parity MIP, one-sided verified witnesses."""
from __future__ import annotations
import os,time
START_CPU,START_WALL=time.process_time(),time.monotonic()
for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[name]="1"
import hashlib,json,math,resource,signal,sys,warnings
from pathlib import Path
from fractions import Fraction
import numpy as np
import scipy.sparse as sp
from scipy.optimize import milp,Bounds,LinearConstraint
ROOT=Path(__file__).resolve().parent
OPTIONS=dict(time_limit=60.,node_limit=10000,presolve=True,mip_rel_gap=0.,threads=1,random_seed=0,mip_feasibility_tolerance=1e-8,disp=True)
INT_TOL=1e-7
ATOL,RTOL=1e-8,1e-12
class BudgetStop(Exception):pass
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)
def peak():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform=="darwin" else value*1024)

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

def solve(model,options):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result=milp(c=model["objective"],integrality=model["integrality"],
            bounds=Bounds(model["lower"],model["upper"]),
            constraints=LinearConstraint(model["matrix"].astype(np.float64),model["b"],model["b"]),options=dict(options))
    messages=[str(w.message) for w in caught]
    # SciPy documents forwarding these options to its bundled HiGHS.
    allowed={"threads","random_seed","mip_feasibility_tolerance"}
    for message in messages:
        assert message.startswith("Unrecognized options detected:") and all(repr(k) in message for k in allowed),message
    return result,messages

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

def scalar(v):
    if v is None:return None
    if isinstance(v,(int,np.integer)):return int(v)
    value=float(v);return value if math.isfinite(value) else None

def main(case_id):
    frozen=read(ROOT/"frozen.json");case=next(c for c in frozen["cases"] if c["case_id"]==case_id)
    resource.setrlimit(resource.RLIMIT_CPU,(90,95))
    def cpu_stop(_s,_f):raise BudgetStop("Child CPU resource limit")
    signal.signal(signal.SIGXCPU,cpu_stop)
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    inputs=np.load(ROOT/case["input_npz"])
    h=sp.load_npz(Path(frozen["H_path"]));l=sp.load_npz(Path(frozen["L_path"]))
    weights=np.load(ROOT/"weights.npy")
    model=build_model(h,l,inputs["syndrome"],inputs["actual"],weights)
    assert (model["n"],model["a"].shape[0],len(model["objective"]))==(12240,1812,14052)
    model_witness(model,inputs["known_correct"])
    wrong=inputs["full_1fv_wrong"]
    assert np.array_equal(h.astype(np.int64)@wrong.astype(np.int64)%2,inputs["syndrome"])
    assert not np.array_equal(l.astype(np.int64)@wrong.astype(np.int64)%2,inputs["actual"])
    source_wrong_score=float(weights@wrong)
    assert abs(source_wrong_score-case["wrong_score"])<=ATOL+RTOL*abs(source_wrong_score)
    options=frozen["solver_options"];assert options==OPTIONS
    with (ROOT/"reference_invocations.jsonl").open("a") as log:
        log.write(json.dumps(dict(event="start",case_id=case_id,kind="correct_class_constrained_reference_optimization"))+"\n")
    c0,w0=time.process_time(),time.monotonic()
    result,messages=solve(model,options)
    solve_cpu=time.process_time()-c0;solve_wall=time.monotonic()-w0
    with (ROOT/"reference_invocations.jsonl").open("a") as log:
        log.write(json.dumps(dict(event="solver_returned",case_id=case_id,status=int(result.status)))+"\n")
    raw_metadata=dict(solver_status=int(result.status),solver_message=str(result.message),
        solver_objective=scalar(getattr(result,"fun",None)),solver_dual_bound_numerical_only=scalar(getattr(result,"mip_dual_bound",None)),
        solver_gap_numerical_only=scalar(getattr(result,"mip_gap",None)),solver_node_count=scalar(getattr(result,"mip_node_count",None)),
        incumbent_returned=result.x is not None,solver_warnings=messages)
    save(ROOT/"cases"/f"{case_id:04d}_raw_metadata.json",raw_metadata)
    if result.x is not None:np.savez_compressed(ROOT/"cases"/f"{case_id:04d}_raw.npz",raw_solution=result.x)
    # No score cutoff was added: the original saved correct vector proves feasibility.
    assert result.status!=2,"Solver infeasibility contradicts the known full-model witness"
    assert result.status!=3,"Bounded nonnegative full model cannot be unbounded"
    assert result.status in (0,1),"Unexpected solver status is a backend error"
    if result.status==0:assert result.x is not None,"Solver optimal status without an incumbent"
    checked=validate_incumbent(model,result.x)
    report=dict(status="completed",case_id=case_id,solver_status=int(result.status),solver_message=str(result.message),
        solver_success_flag=bool(result.success),solver_objective=scalar(getattr(result,"fun",None)),
        solver_dual_bound_numerical_only=scalar(getattr(result,"mip_dual_bound",None)),solver_gap_numerical_only=scalar(getattr(result,"mip_gap",None)),
        solver_node_count=scalar(getattr(result,"mip_node_count",None)),solver_warnings=messages,
        known_correct_model_adapter=True,wrong_vector_rejected_by_logical_constraint=True,wrong_score=source_wrong_score,
        solver_cpu_seconds=solve_cpu,solver_wall_seconds=solve_wall,new_reference_optimization_calls=1,new_BP_OSD_LSD_calls=0,new_physical_shots=0,
        rigorous_lower_bound_available=False,oracle_logical_target_used=True,classification="unresolved_no_verified_better_witness",
        frozen_sha256=sha(ROOT/"frozen.json"))
    if checked is not None:
        x,int_residual,integers=checked
        score=float(weights@x);wrong_fsum=math.fsum(float(weights[j]) for j in np.flatnonzero(wrong))
        new_fsum=math.fsum(float(weights[j]) for j in np.flatnonzero(x))
        assert abs(score-new_fsum)<=ATOL+RTOL*abs(score)
        assert abs(source_wrong_score-wrong_fsum)<=ATOL+RTOL*abs(source_wrong_score)
        # A feasible rounded vector establishes its own cost independently of solver.fun.
        reported_cost_difference=abs(float(result.fun)-score) if result.fun is not None else None
        exact_new=sum((Fraction.from_float(float(weights[j])) for j in np.flatnonzero(x)),Fraction())
        exact_wrong=sum((Fraction.from_float(float(weights[j])) for j in np.flatnonzero(wrong)),Fraction())
        tol=ATOL+RTOL*max(abs(new_fsum),abs(wrong_fsum))
        better=exact_wrong-exact_new>Fraction.from_float(tol)
        np.savez_compressed(ROOT/"cases"/f"{case_id:04d}_solver.npz",raw_solution=result.x,integer_solution=integers,correction=x)
        report.update(incumbent_valid=True,incumbent_integer_proximity=int_residual,incumbent_score=score,
            incumbent_score_fsum=new_fsum,wrong_score_fsum=wrong_fsum,improvement_fsum=wrong_fsum-new_fsum,
            solver_objective_difference_descriptive=reported_cost_difference,
            exact_float_weight_improvement=dict(numerator=str((exact_wrong-exact_new).numerator),denominator=str((exact_wrong-exact_new).denominator)),
            score_tolerance=tol,classification="verified_outside_list_competitive_witness" if better else "unresolved_no_verified_better_witness")
    else:report["incumbent_valid"]=False
    report.update(child_cpu_seconds=time.process_time()-START_CPU,child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak())
    if report["child_cpu_seconds"]>=90 or report["child_wall_seconds"]>=120 or report["peak_child_rss_bytes"]>1073741824:raise BudgetStop("Child CPU/wall/RSS resource ceiling")
    save(ROOT/"cases"/f"{case_id:04d}.json",report)
    print(json.dumps(report),flush=True)

if __name__=="__main__":
    try:main(int(sys.argv[1]))
    except Exception as exc:
        cid=int(sys.argv[1]);save(ROOT/"cases"/f"{cid:04d}_stop.json",dict(status="resource_stopped" if isinstance(exc,BudgetStop) else "validation_stopped",message=f"{type(exc).__name__}: {exc}",case_id=cid,child_cpu_seconds=time.process_time()-START_CPU,child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak()))
        raise
