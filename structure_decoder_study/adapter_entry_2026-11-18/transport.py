"""Shared raw-first native transport. Imports native libraries only when used."""
from __future__ import annotations
import ast,hashlib,json,math,os,re,time,warnings
from pathlib import Path
from result_guard import atomic_json,telemetry

def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def journal(path,value):
    with Path(path).open('a') as stream:
        stream.write(json.dumps(value,sort_keys=True,allow_nan=False)+'\n');stream.flush();os.fsync(stream.fileno())

def atomic_npz(path,**arrays):
    import numpy as np
    path=Path(path);temporary=path.with_name(path.name+'.tmp')
    with temporary.open('xb') as stream:
        np.savez_compressed(stream,**arrays);stream.flush();os.fsync(stream.fileno())
    temporary.replace(path)

def scalar(value):
    import numpy as np
    if value is None:return None
    if isinstance(value,(bool,np.bool_)):return dict(unexpected_scalar_type='bool',representation=repr(value))
    if isinstance(value,(int,np.integer)):return int(value)
    if isinstance(value,(float,np.floating)):
        return float(value) if math.isfinite(value) else dict(nonfinite=repr(float(value)))
    return dict(unexpected_scalar_type=type(value).__name__,representation=repr(value))

def check_environment(expected_path,out,identity):
    import importlib,platform,sys
    import numpy,scipy,scipy.optimize._milp as m
    import scipy.optimize._highspy._core as core
    expected=read(expected_path)
    wrapper=importlib.import_module(m._highs_wrapper.__module__)
    modules=dict(numpy_module=numpy,scipy_module=scipy,scipy_milp_wrapper=m,highs_core=core,direct_highs_wrapper=wrapper)
    actual=dict(identity=identity,python=sys.version,platform=platform.platform(),
        interpreter_resolved=str(Path(sys.executable).resolve()),
        imported_files={k:dict(path=str(Path(v.__file__).resolve()),sha256=sha(v.__file__)) for k,v in modules.items()},
        versions=dict(numpy=numpy.__version__,scipy=scipy.__version__),
        thread_environment={k:os.environ.get(k) for k in expected['intended_worker_thread_environment']})
    atomic_json(Path(out)/'environment_actual.json',actual)
    assert actual['python']==expected['python'] and actual['platform']==expected['platform']
    assert actual['interpreter_resolved']==expected['interpreter_resolved']
    assert sha(actual['interpreter_resolved'])==expected['interpreter_binary_sha256']
    assert actual['imported_files']==expected['imported_files']
    assert actual['thread_environment']==expected['intended_worker_thread_environment']
    assert actual['versions']=={k:expected['versions'][k] for k in ('numpy','scipy')}
    return actual

def persist_payload(out,identity,result,caught,before,after,native_calls,ledger):
    """Persist before warning/status/vector assertions; metadata handles nonfinite values."""
    out=Path(out);ledger.phase='persisting_result'
    raw=getattr(result,'x',None)
    if raw is not None:atomic_npz(out/'raw.npz',x=raw)
    meta=dict(identity=identity,before_call=before,after_call=after,native_optimizer_calls=native_calls,
        has_incumbent=raw is not None,solver_status=scalar(getattr(result,'status',None)),
        message=str(getattr(result,'message','')),warnings=[str(w.message) for w in caught],
        numerical_only={k:scalar(getattr(result,k,None)) for k in ('fun','mip_gap','mip_dual_bound','mip_node_count')},
        handler_while_raw_saved=telemetry()['sigxcpu_handler'])
    atomic_json(out/'raw_metadata.json',meta)
    files=['raw_metadata.json']+(['raw.npz'] if raw is not None else [])
    atomic_json(out/'raw_manifest.json',dict(identity=identity,files={n:sha(out/n) for n in files},persisted_at=telemetry()))
    return meta

def invoke(out,identity,call,ledger):
    ledger.phase='solver_call'
    attempt=dict(identity=identity,event='optimizer_start',at=telemetry())
    atomic_json(Path(out)/'optimizer_attempt.json',attempt)
    journal(Path(out)/'native_journal.jsonl',attempt)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        before=telemetry()
        atomic_json(Path(out)/'ready.json',dict(identity=identity,phase='solver_call',at=before))
        result=call()
    after=telemetry()
    metadata=persist_payload(out,identity,result,caught,before,after,1,ledger)
    journal(Path(out)/'native_journal.jsonl',dict(identity=identity,event='optimizer_return_persisted',at=telemetry(),
        raw_manifest_sha256=sha(Path(out)/'raw_manifest.json')))
    return result,metadata

def validate_warnings(messages,expected_forwarded):
    expected=set(expected_forwarded)
    assert len(messages)==1,'Expected one options-forwarding warning'
    match=re.fullmatch(r'Unrecognized options detected: (\{.*\})\. These will be passed to HiGHS verbatim\.',messages[0])
    assert match,'Unexpected warning text'
    observed=ast.literal_eval(match.group(1))
    assert isinstance(observed,set) and observed==expected,'Unexpected forwarded option set'

def mis_fixture(n=200,seed=2026111801):
    import numpy as np
    import scipy.sparse as sp
    rng=np.random.default_rng(seed)
    pairs=np.transpose(np.nonzero(np.triu(rng.random((n,n))<.08,1)))
    rr=np.repeat(np.arange(len(pairs)),2);cc=pairs.ravel()
    matrix=sp.coo_array((np.ones(len(cc)),(rr,cc)),shape=(len(pairs),n)).tocsc()
    cost=-(1.+.001*rng.random(n))
    return pairs,matrix,cost
