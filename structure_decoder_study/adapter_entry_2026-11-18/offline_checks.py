"""Meaningful preflight checks using exhaustive bits and labeled fake payloads.

No optimizer is called, no worker/ps process is launched, no research input read.
"""
import ast,hashlib,itertools,json,signal,sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from model_helpers import build_model,model_witness,validate_incumbent,INT_TOL
from result_guard import SignalLedger,telemetry
from transport import persist_payload,validate_warnings,sha,scalar
ROOT=Path(__file__).resolve().parent
def source_function(path,name):
    s=Path(path).read_text();n=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return '\n'.join(s.splitlines()[n.lineno-1:n.end_lineno])
def main():
    target=ROOT/'offline_checks.json';assert not target.exists(),'Preserve offline evidence'
    revision=sys.argv[1] if len(sys.argv)==2 else 'initial'
    assert revision.isalnum(),'Use an explicit alphanumeric offline revision'
    evidence=ROOT/('offline_evidence_'+revision);evidence.mkdir()
    spec=json.loads((ROOT/'prepared_protocol.json').read_text());toys=json.loads((ROOT/'entry_fixtures.json').read_text())['fixtures']
    checked=[]
    for name in spec['shared_adapter_source']['functions']:
        assert source_function(ROOT/'model_helpers.py',name)==source_function(spec['shared_adapter_source']['path'],name)
    assert INT_TOL==1e-7
    for toy in toys:
        model=build_model(np.asarray(toy['H']),np.asarray(toy['L']),np.asarray(toy['syndrome']),np.asarray(toy['logical_target']),np.asarray(toy['weights']))
        assert np.all(model['integrality']==1)
        feasible=0
        for bits in itertools.product((0,1),repeat=len(toy['weights'])):
            x=np.asarray(bits);a=np.vstack([toy['H'],toy['L']]);b=np.r_[toy['syndrome'],toy['logical_target']]
            if not np.array_equal(a@x%2,b):continue
            full=model_witness(model,x);returned=validate_incumbent(model,full.astype(float))
            assert np.array_equal(returned[0],x)
            bad=full.astype(float);bad[0]+=.01
            try:validate_incumbent(model,bad)
            except AssertionError:pass
            else:raise AssertionError('Bad fractional array accepted')
            feasible+=1
        assert feasible==toy['feasible_vectors'];checked.append(dict(toy=toy['name'],feasible_vectors=feasible,all_parity_domains_integral=True))
    previous=signal.getsignal(signal.SIGXCPU);folder=evidence/'payload';folder.mkdir()
    payload=SimpleNamespace(status=1,x=np.asarray([0.,1.]),message='Labeled fake payload; no solve',fun=float('nan'),mip_dual_bound=-float('inf'))
    with SignalLedger() as ledger:
        persist_payload(folder,dict(scope='offline_fake_payload'),payload,[],telemetry(),telemetry(),0,ledger)
        assert (folder/'raw.npz').exists() and (folder/'raw_manifest.json').exists()
        manifest=json.loads((folder/'raw_manifest.json').read_text())
        assert all(sha(folder/name)==digest for name,digest in manifest['files'].items())
        try:validate_warnings(['Unexpected warning after raw persistence'],['threads','random_seed'])
        except AssertionError:pass
        else:raise AssertionError('Unexpected warning accepted')
        assert (folder/'raw.npz').exists() and np.array_equal(np.load(folder/'raw.npz')['x'],payload.x)
    assert signal.getsignal(signal.SIGXCPU)==previous
    assert scalar(float('inf'))==dict(nonfinite='inf') and scalar(True)['unexpected_scalar_type']=='bool'
    for keys in (['threads','random_seed'],['threads','random_seed','mip_feasibility_tolerance']):
        message='Unrecognized options detected: '+repr(set(keys))+'. These will be passed to HiGHS verbatim.'
        validate_warnings([message],keys)
    try:validate_warnings([message],['threads','random_seed'])
    except AssertionError:pass
    else:raise AssertionError('Parity warning incorrectly accepted for MIS')
    # No OS process: exercise fallback cleanup without Accounting or a trace writer.
    import monitor
    class FakeOwned:
        pid=424242
        stdin=None
        returncode=None
        def poll(self):return self.returncode
        def send_signal(self,signum):self.signal=int(signum)
        def wait(self,timeout):self.returncode=-self.signal;return self.returncode
    for unwritable in (False,True):
        fake=FakeOwned();cleanup=dict(attempted=False,actions=[]);monitor.ACTIVE_OWNED.append(fake)
        destination=evidence/('cleanup_unwritable' if unwritable else 'cleanup');destination.mkdir()
        if unwritable:
            with patch.object(monitor,'atomic_json',side_effect=OSError('Controlled metadata failure')):
                monitor.finalize_owned(fake,cleanup,destination,dict(scope='offline_fake_process'))
        else:monitor.finalize_owned(fake,cleanup,destination,dict(scope='offline_fake_process'))
        assert fake.returncode==-signal.SIGTERM and cleanup['attempted'] and len(cleanup['actions'])==1
        assert fake not in monitor.ACTIVE_OWNED
    from control import stop_control_matches
    assert not stop_control_matches(dict(returncode=-9,termination_actions=[dict(signum=15,signal_API_returned=True,
        wait_returncode=-9,wait_timed_out=False)]))
    tree=ast.parse((ROOT/'monitor.py').read_text())
    watch=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='watch')
    block=next(n for n in watch.body if isinstance(n,ast.With))
    spawn_index=next(i for i,n in enumerate(block.body) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='Popen')
    assert isinstance(block.body[spawn_index+1],ast.Try) and block.body[spawn_index+1].finalbody
    report=dict(passed=True,scope='offline_helpers_and_mock_persistence',revision=revision,optimizer_api_attempts=0,experimental_workers=0,OS_queries=0,
        exact_original_model_helpers=True,integer_parity_checks=checked,invalid_fractional_arrays_rejected=True,
        raw_fake_payload_survives_unexpected_warning=True,per_mode_warning_sets_checked=True,handler_restored=True,
        nonfinite_scalars_labeled=True,boolean_status_not_silently_normalized=True,
        immediate_spawn_cleanup_guard_checked=True,fallback_reaps_fake_process_without_state_or_writable_metadata=True,
        lone_TERM_with_SIGKILL_exit_rejected=True,
        source_hashes={p.name:sha(p) for p in ROOT.glob('*.py') if p.name not in ('check_policy.py',)},
        native_integration_validated=False,research_cases_read_or_solved=0)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='source_hashes'},indent=2))
if __name__=='__main__':main()
