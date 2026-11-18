"""Capture a preparation spec/environment. No optimizer invocation or worker."""
from __future__ import annotations
import ast,hashlib,importlib,itertools,json,os,platform,sys
from pathlib import Path
import numpy as np
import scipy
import scipy.optimize._milp as milp_module
import scipy.optimize._highspy._core as core
ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
OLD=STUDY/'reference_probe_2026-11-18'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    p=ROOT/name;assert not p.exists(),'Preserve '+name
    p.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def main():
    baseline=read(OLD/'frozen.json');entry=read(OLD/'entry_result.json')
    tree=ast.parse((OLD/'entry.py').read_text())
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cases' for t in n.targets))
    toys=ast.literal_eval(node.value);fixtures=[]
    for name,h,l,s,t,w in toys:
        feasible=[]
        for bits in itertools.product((0,1),repeat=len(w)):
            parity=lambda rows:[sum(a*b for a,b in zip(row,bits))%2 for row in rows]
            if parity(h)==s and parity(l)==t:feasible.append(sum(a*b for a,b in zip(w,bits)))
        previous=next(r for r in entry['rows'] if r['name']==name)
        minimum=min(feasible) if feasible else None
        assert minimum==previous['exhaustive_minimum'] and len(feasible)==previous['feasible_vectors']
        fixtures.append(dict(name=name,H=h,L=l,syndrome=s,logical_target=t,weights=w,
            enumerated_vectors=2**len(w),feasible_vectors=len(feasible),minimum=minimum,
            expected_solver_status=0 if feasible else 2))
    write('entry_fixtures.json',dict(source=str(OLD/'entry.py'),source_sha256=sha(OLD/'entry.py'),fixtures=fixtures))
    identity_paths={key:Path(module.__file__).resolve() for key,module in [('numpy_module',np),('scipy_module',scipy),('scipy_milp_wrapper',milp_module),('highs_core',core)]}
    direct_wrapper=importlib.import_module(milp_module._highs_wrapper.__module__)
    identity_paths['direct_highs_wrapper']=Path(direct_wrapper.__file__).resolve()
    assert sha(identity_paths['highs_core'])==entry['backend_core_sha256'],'Backend changed from prior entry'
    env=dict(interpreter=sys.executable,interpreter_resolved=str(Path(sys.executable).resolve()),python=sys.version,
        platform=platform.platform(),versions=dict(numpy=np.__version__,scipy=scipy.__version__,bundled_highs=entry['versions']['bundled_highs']),
        bundled_highs_version_provenance='prior version query, unchanged native core SHA256 verified',
        imported_files={k:dict(path=str(p),sha256=sha(p)) for k,p in identity_paths.items()},
        interpreter_binary_sha256=sha(Path(sys.executable).resolve()),
        observed_thread_environment={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')},
        intended_worker_thread_environment={k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')},
        actual_native_adapter_validated=False,optimizer_invocations=0)
    write('environment.json',env)
    entries=[f['name'] for f in fixtures]+['timeout_none','timeout_incumbent','signal_during_call',
        'signal_during_persistence','parent_CPU','parent_wall','parent_RSS','observed_terminal_Z','malformed_active_monitor']
    spec=dict(status='preparation_only_awaiting_review',native_entry_launch_authorized=False,research_launch_authorized=False,
        new_optimizer_attempts=0,new_experimental_workers=0,
        implementation_missing=['fresh_controller','integrated_worker','independent_runtime_and_witness_audit'],
        optional_research_cases=[131,228],case_order_fixed=True,scientific_value_gate_resolved=False,
        score='same represented float64 log(1/p)',comparison='current saved full-1FV wrong winner',
        score_tolerance=dict(atol=1e-8,rtol=1e-12,comparison='exact represented coefficient difference > atol+rtol*max(abs(scores))'),
        model=dict(fault_bits=12240,parity_rows=1812,integral_variables=14052,all_parity_slacks_integral=True,true_logical_target_is_oracle=True),
        solver_options=baseline['solver_options'],
        research_limits=dict(parent_absolute_cpu_threshold=90.,parent_wall_threshold=120.,rss_threshold_bytes=1073741824,
            requested_OS_cpu_limits=[90,95],controller_admission_threshold=260.,remaining_before_child=130.),
        monitor=dict(command=['ps','-o','pid=,stat=,rss=,time=','-p','OWNED_PID'],poll_interval_seconds=.01,
            query_timeout_seconds=1.,terminal_reaping_grace_seconds=.5,SIGTERM_wait_seconds=.5,SIGKILL_reap_wait_seconds=.5,
            thresholds_are_instantaneous_guarantees=False,normal_query_after_reaped=False,terminal_state='Z',
            live_CPU_decrease_is_sticky_error=True,terminal_zero_does_not_reset_highwater=True),
        entry=dict(order=entries,max_children=13,max_optimizer_attempts=7,controller_admission_threshold=120.,remaining_before_child=11.,
            normal_child=dict(cpu_threshold=10.,wall_threshold=8.,rss_bytes=1073741824,requested_OS_cpu_limits=[10,12]),
            parity_options=dict(baseline['solver_options'],time_limit=2.,node_limit=1000,disp=False),
            MIS=dict(n=200,density=.08,seed=2026111801,time_without_incumbent=0.,time_with_incumbent=.15,
                options=dict(presolve=False,mip_rel_gap=0.,threads=1,random_seed=0,disp=False)),
            dedicated_overrides=dict(parent_CPU=dict(cpu_threshold=3.,requested_OS_cpu_limits=[1,3]),
                parent_wall=dict(wall_threshold=.15),parent_RSS=dict(rss_bytes=67108864,committed_bytes=100663296)),
            Z_fixture=dict(cpu_burn=.1,positive_live_sample_required=True,permission_barrier=True,exit_query_delay=.05,queries_after_exit_permission=1),
            retries=0,calibration_calls=0,unexpected_failure_aborts_remaining=True),
        accounting=dict(historical_reference_attempts=6,historical_timeout_repair_attempts=12,historical_total=18,
            future_entry_max=7,future_optional_real_max=2,future_total_max=9,future_worker_max=15),
        background_progress_check_minutes=20,background_does_not_extend_budgets=True,
        scientific_interpretation=dict(primary='independently verified competitive witness from finalized ordinary return',
            secondary='separately tagged artifact-only verified witness from signalled/censored process',
            no_witness='inconclusive',rigorous_negative_exclusion_enabled=False,decoder_improvement_claim=False),
        prior_reference_frozen_sha256=sha(OLD/'frozen.json'),prior_reference_manifest_sha256=sha(OLD/'manifest.json'),
        prior_timeout_repair_manifest_sha256=sha(STUDY/'timeout_repair_v2_2026-11-18/manifest.json'),
        reference_inputs_root=str(OLD.resolve()),H_path=baseline['H_path'],L_path=baseline['L_path'],
        priors_path=baseline['priors_path'],weights_path=str((OLD/'weights.npy').resolve()),
        reference_cases=baseline['cases'],reference_input_hashes={p:d for p,d in baseline['files'].items()
            if p.endswith(('.npz','.npy')) or 'core.cpython' in p},
        shared_adapter_source= dict(path=str(OLD/'probe.py'),sha256=sha(OLD/'probe.py'),
            functions=['build_model','model_witness','validate_incumbent'],
            old_solve_is_not_reusable_transport=True,
            new_transport_must_save_raw_before_warning_or_status_interpretation=True,
            expected_forwarded_options_by_mode=dict(parity=['threads','random_seed','mip_feasibility_tolerance'],MIS=['threads','random_seed'])),
        shared_signal_guard=dict(path=str(STUDY/'timeout_repair_v2_2026-11-18/result_guard.py'),
            sha256=sha(STUDY/'timeout_repair_v2_2026-11-18/result_guard.py')))
    assert len(entries)==13 and sum((4,3))==7
    write('protocol.json',spec)
    print(json.dumps(dict(preparation_spec_written=True,entry_fixtures=len(fixtures),future_entry_children=len(entries),
        future_entry_optimizer_attempts=7,optimizer_attempts_now=0,experimental_workers_now=0,
        scipy_imported_path=str(identity_paths['scipy_module']),research_launch_authorized=False)))
if __name__=='__main__':main()
