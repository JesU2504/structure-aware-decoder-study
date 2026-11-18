"""Entry-only isolated worker. No research-case mode or research input access."""
from __future__ import annotations
import os,time
START_CPU,START_WALL=time.process_time(),time.monotonic()
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
import hashlib,json,math,resource,signal,sys,traceback
from pathlib import Path
from result_guard import SignalLedger,atomic_json,telemetry
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(path):
    cfg=read(path);out=Path(cfg['output']);assert out.is_dir()
    identity=dict(cfg['identity'],config_sha256=sha(path));assert cfg['scope']=='synthetic_entry_only'
    initial=telemetry();resource.setrlimit(resource.RLIMIT_CPU,tuple(cfg['OS_cpu_limits']))
    previous=signal.getsignal(signal.SIGXCPU)
    atomic_json(out/'startup.json',dict(identity=identity,before_limits=initial,after_limits=telemetry(),
        start_cpu=START_CPU,start_wall=START_WALL,initial_handler=str(previous),
        native_modules_before_mode={k:k in sys.modules for k in ('numpy','scipy')}))
    ledger=SignalLedger();report=None
    try:
        with ledger:
            mode=cfg['mode'];name=cfg['name'];ledger.phase='entry_setup'
            if mode in ('cpu','wall','rss','terminal','fault'):
                # Keep these controls strictly stdlib-only, including their RSS baseline.
                if mode=='wall':
                    atomic_json(out/'ready.json',dict(identity=identity,phase='sleep',at=telemetry()))
                    time.sleep(2);raise AssertionError('Wall guard did not stop child')
                if mode=='rss':
                    atomic_json(out/'allocation_start.json',dict(identity=identity,at=telemetry(),committed_bytes=cfg['committed_bytes']))
                    payload=bytearray(cfg['committed_bytes'])
                    for index in range(0,len(payload),4096):payload[index]=7
                    atomic_json(out/'allocated.json',dict(identity=identity,at=telemetry(),committed_bytes=len(payload)))
                    while True:time.sleep(.1)
                if mode=='cpu':
                    last=0.;ledger.phase='cpu_spin'
                    while True:
                        total=sum(i*i for i in range(1000))
                        if time.process_time()-last>.1:
                            atomic_json(out/'progress.json',dict(identity=identity,at=telemetry(),signals=list(ledger.events)))
                            last=time.process_time()
                if mode=='fault':
                    atomic_json(out/'ready.json',dict(identity=identity,phase='live_fault_control',at=telemetry()))
                    while True:time.sleep(.02)
                if mode=='terminal':
                    start=time.process_time()
                    while time.process_time()-start<.1:total=sum(i*i for i in range(1000))
                    atomic_json(out/'ready.json',dict(identity=identity,phase='exit_permission_barrier',at=telemetry()))
                    permission=sys.stdin.readline()
                    assert permission=='EXIT\n','Owned permission barrier not released'
                    report=dict(payload_kind='terminal_control',solver_status=None,native_optimizer_calls=0,
                        raw_payload_complete=True,after_call=telemetry(),has_incumbent=False)
            else:
                from transport import atomic_npz,check_environment,invoke,mis_fixture,persist_payload,validate_warnings
                import numpy as np
                from scipy.optimize import Bounds,LinearConstraint,milp
                check_environment(ROOT/'environment.json',out,identity)
                if mode=='parity':
                    from model_helpers import build_model,model_witness,validate_incumbent
                    toy=cfg['fixture'];h=np.asarray(toy['H']);l=np.asarray(toy['L']);weights=np.asarray(toy['weights'])
                    model=build_model(h,l,np.asarray(toy['syndrome']),np.asarray(toy['logical_target']),weights)
                    atomic_npz(out/'fixture.npz',H=h,L=l,syndrome=np.asarray(toy['syndrome']),target=np.asarray(toy['logical_target']),weights=weights)
                    callback=lambda:milp(c=model['objective'],integrality=model['integrality'],bounds=Bounds(model['lower'],model['upper']),
                        constraints=LinearConstraint(model['matrix'].astype(np.float64),model['b'],model['b']),options=cfg['solver_options'])
                else:
                    pairs,matrix,cost=mis_fixture(cfg['n'],cfg['seed'])
                    atomic_npz(out/'fixture.npz',edges=pairs,cost=cost)
                    callback=lambda:milp(c=cost,integrality=np.ones(cfg['n']),bounds=Bounds(np.zeros(cfg['n']),np.ones(cfg['n'])),
                        constraints=LinearConstraint(matrix,-np.inf,np.ones(matrix.shape[0])),options=cfg['solver_options'])
                if mode=='mock':
                    from types import SimpleNamespace
                    before=telemetry();result=SimpleNamespace(status=1,message='Labeled mock; no native call',x=np.zeros(cfg['n']))
                    meta=persist_payload(out,identity,result,[],before,telemetry(),0,ledger)
                    atomic_json(out/'persist_ready.json',dict(identity=identity,phase='guarded_persistence',at=telemetry()))
                    time.sleep(.1)
                else:
                    result,meta=invoke(out,identity,callback,ledger)
                    atomic_json(out/'interpretation_started.json',dict(identity=identity,at=telemetry(),raw_manifest_sha256=sha(out/'raw_manifest.json')))
                    validate_warnings(meta['warnings'],cfg['expected_forwarded_options'])
                assert isinstance(result.status,(int,np.integer)) and not isinstance(result.status,(bool,np.bool_)),'Noninteger solver status'
                if mode=='parity':
                    assert result.status==cfg['expected_status']
                    checked=validate_incumbent(model,result.x)
                    if checked is not None:
                        x,residual,integers=checked;model_witness(model,x)
                        atomic_npz(out/'validated.npz',x=x,integer_solution=integers)
                        score=math.fsum(float(w) for w,bit in zip(weights,x) if bit)
                        assert abs(score-toy['minimum'])<1e-10
                    else:residual=None;score=None
                else:
                    assert result.status==1,'Expected timeout/mock status'
                    checked=result.x
                    if checked is not None:
                        raw=np.asarray(checked);assert raw.shape==(cfg['n'],) and np.isfinite(raw).all()
                        residual=float(np.max(abs(raw-np.rint(raw))));assert residual<=1e-7
                        x=np.rint(raw).astype(np.int64)
                        assert np.isin(x,[0,1]).all() and np.all(x[pairs[:,0]]+x[pairs[:,1]]<=1)
                        score=math.fsum(float(w) for w,bit in zip(cost,x) if bit)
                        atomic_npz(out/'validated.npz',x=x)
                    else:residual=None;score=None
                    assert (checked is not None)==cfg['expected_incumbent']
                report=dict(payload_kind=mode,solver_status=int(result.status),native_optimizer_calls=meta['native_optimizer_calls'],
                    raw_payload_complete=True,has_incumbent=result.x is not None,incumbent_valid=True if checked is not None else None,
                    incumbent_score=score,integer_proximity=residual,before_call=meta['before_call'],after_call=meta['after_call'],
                    warnings_validated=True,raw_manifest_sha256=sha(out/'raw_manifest.json'))
            ledger.phase='provisional_persistence'
            assert report is not None
            atomic_json(out/'provisional_result.json',dict(report,identity=identity,finalized=False))
    finally:
        restored=signal.getsignal(signal.SIGXCPU)==previous
        atomic_json(out/'handler_restoration.json',dict(identity=identity,restored=restored,previous=str(previous),
            current=str(signal.getsignal(signal.SIGXCPU)),at=telemetry(),stable_signals=list(ledger.events)))
    assert restored
    if cfg['mode']=='mock':
        try:
            with SignalLedger():raise ValueError('Controlled restoration check')
        except ValueError:pass
        assert signal.getsignal(signal.SIGXCPU)==previous
        report['exception_restoration_passed']=True
    atomic_json(out/'final.json',dict(report,identity=identity,finalized=True,handler_restored=True,
        signals=list(ledger.events),finalized_at=telemetry(),oracle_or_research_inputs_used=False,
        native_modules_after_mode={k:k in sys.modules for k in ('numpy','scipy')}))

if __name__=='__main__':
    try:main(sys.argv[1])
    except BaseException as exc:
        try:
            cfg=read(sys.argv[1]);atomic_json(Path(cfg['output'])/'exception.json',dict(identity=cfg['identity'],
                kind=type(exc).__name__,message=str(exc),at=telemetry(),traceback=traceback.format_exc()))
        finally:raise
