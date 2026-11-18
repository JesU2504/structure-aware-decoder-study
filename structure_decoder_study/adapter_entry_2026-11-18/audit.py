"""Independent saved-output audit. Imports no model/solver/monitor helpers."""
from __future__ import annotations
import ast,hashlib,itertools,json,math,signal
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
    assert not p.exists(),'Preserve audit'
    q=p.with_name(p.name+'.tmp');q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n');q.replace(p)
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def clock(token):
    pieces=token.split('-');assert len(pieces) in (1,2)
    days=int(pieces[0]) if len(pieces)==2 else 0
    if len(pieces)==2:assert pieces[0].isdigit()
    parts=pieces[-1].split(':');assert len(parts) in (2,3)
    assert all(x.isdigit() for x in parts[:-1])
    sec=Decimal(parts[-1]);assert sec.is_finite() and 0<=sec<60
    if len(parts)==2:
        assert len(pieces)==1
        return float(Decimal(int(parts[0])*60)+sec)
    hour,minute=int(parts[0]),int(parts[1]);assert minute<60
    if len(pieces)==2:assert hour<24
    return float(Decimal(days*86400+hour*3600+minute*60)+sec)
def ps(raw,pid):
    fields=raw.split();assert len(fields)==4
    assert fields[0].isdigit() and int(fields[0])==pid
    stat=fields[1];assert stat[0] in ('I','R','S','T','U','Z')
    assert all(c in '+<>AELNSsVWX' for c in stat[1:])
    assert fields[2].isdigit()
    return dict(stat=stat,state=stat[0],cpu=clock(fields[3]),rss=int(fields[2])*1024)

def verify_parity_raw(fixture,values):
    h=np.asarray(fixture['H'],dtype=np.int64);l=np.asarray(fixture['L'],dtype=np.int64)
    a=np.vstack((h,l));b=np.r_[fixture['syndrome'],fixture['logical_target']].astype(np.int64)
    w=np.asarray(fixture['weights'],dtype=np.float64);n=len(w)
    values=np.asarray(values);assert values.shape==(n+len(b),) and np.isfinite(values).all()
    assert np.max(abs(values-np.rint(values)))<=1e-7
    ints=np.rint(values).astype(np.int64);x,z=ints[:n],ints[n:]
    assert np.isin(x,[0,1]).all() and np.all(z>=0) and np.all(z<=(a.sum(axis=1)-b)//2)
    assert np.array_equal(a@x-2*z,b)
    assert np.array_equal(h@x%2,fixture['syndrome']) and np.array_equal(l@x%2,fixture['logical_target'])
    exact=sum((Fraction.from_float(float(v)) for v,bit in zip(w,x) if bit),Fraction())
    return x,ints,math.fsum(float(v) for v,bit in zip(w,x) if bit),exact

def audit_monitor(folder,cfg,process):
    trace=rows(folder/'monitor.jsonl');assert len(trace)==process['observations']
    assert sha(folder/'monitor.jsonl')==process['monitor_trace_sha256']
    pid=process['pid'];last=process['started_monotonic'];cpu_max=0.;rss_max=0;reaped=False;terminal=False;fault_seen=False
    signal_at=process['controlled_signal']['at'] if process['controlled_signal'] else None
    positive_live=[];z_records=[];fault_records=[]
    for item in trace:
        e=item['event'];b=e['before'];after=e['after'];q=e.get('query')
        assert last<=b['at']<=after['at'] and after['at']>last
        if reaped:raise AssertionError('Observation after owned reaping')
        if b['returncode'] is not None:assert q is None and after['returncode']==b['returncode']
        if q is not None:
            assert b['returncode'] is None and not terminal
            assert b['at']<=q['start']<=q['end']<=after['at'] and q['end']-q['start']<=1.01
            assert not q['error']
            fault=e.get('controlled_fault')
            if fault:
                assert cfg['mode']=='fault' and not fault_seen
                assert fault==process['controlled_fault'] and q==fault['corrupted_query']
                true=ps(fault['true_query']['stdout'],pid)
                assert true['state']!='Z' and true['rss']>0 and 'NOT_A_NUMBER' in q['stdout']
                assert q['stdout'].split()==[str(pid),true['stat'],'NOT_A_NUMBER',fault['true_query']['stdout'].split()[3]]
                assert item['decision']['censor_reasons']==['monitor_invalid: Invalid RSS']
                fault_seen=True;fault_records.append(fault)
            elif q['stdout'].strip():
                assert q['returncode']==0
                current=ps(q['stdout'],pid)
                if current['state']=='Z':
                    terminal=True;z_records.append(dict(query=q,before=b,after=after))
                else:
                    assert current['rss']>0 and current['cpu']>=cpu_max
                    if current['cpu']>0:positive_live.append(dict(query=q,cpu=current['cpu']))
                cpu_max=max(cpu_max,current['cpu']);rss_max=max(rss_max,current['rss'])
            else:
                assert q['returncode'] in (0,1)
                terminal=True # Pending absence must be confirmed by owned reaping below.
        elif b['returncode'] is None:
            assert terminal and e.get('bounded_reaping_wait')
        if after['returncode'] is not None:
            assert after['returncode']==process['returncode'];reaped=True
        if signal_at is not None and terminal:assert signal_at<=q['end'] if q is not None else signal_at<=b['at']
        last=after['at']
    assert reaped and process['accounting']['phase']=='REAPED' and process['monitor_failure'] is None
    assert process['accounting']['returncode']==process['returncode']
    for snapshot in process['checked_child_snapshots']:
        path=folder/snapshot['file'];assert sha(path)==snapshot['file_sha256']
        content=read(path);assert content['identity']==process['identity']
        at=content[snapshot['key']];assert at==snapshot['telemetry'] and at['pid']==pid
        assert process['started_monotonic']<=at['monotonic']<=last
        assert at['cpu_absolute']>=0 and abs(at['cpu_absolute']-at['ru_utime']-at['ru_stime'])<.1
        cpu_max=max(cpu_max,at['cpu_absolute']);rss_max=max(rss_max,at['peak_rss_bytes'])
    assert cpu_max==process['accounting']['cpu_highwater'] and rss_max==process['accounting']['rss_highwater']
    independent=[]
    if fault_seen:independent.append('monitor_invalid: Invalid RSS')
    if cpu_max>=cfg['limits']['cpu']:independent.append('cpu_limit')
    if rss_max>cfg['limits']['rss']:independent.append('rss_limit')
    if last-process['started_monotonic']>=cfg['limits']['wall']:independent.append('wall_limit')
    assert set(process['accounting']['censor_reasons'])==set(independent)
    actions=process['termination_actions']
    for action in actions:
        assert action['pid']==pid and action['signum'] in (signal.SIGTERM,signal.SIGKILL)
        assert action['before']['returncode'] is None and action['before']['at']<=action['requested_at']<=action['wait_started']<=action['wait_finished']
        assert action['wait_finished']-action['wait_started']<1.1
        assert action['reasons'] and set(action['reasons']).issubset(set(independent))
        assert action['signal_API_returned'] is True and 'wait_error' not in action
    if actions:
        assert actions[0]['signum']==signal.SIGTERM
        if len(actions)==1:
            assert process['returncode']==actions[0]['wait_returncode']==-signal.SIGTERM and not actions[0]['wait_timed_out']
        else:
            assert len(actions)==2 and actions[0]['wait_timed_out'] and actions[0]['wait_returncode'] is None
            assert actions[0]['wait_finished']-actions[0]['wait_started']>=.49
            assert actions[1]['signum']==signal.SIGKILL and actions[1]['requested_at']>=actions[0]['wait_finished']
            assert process['returncode']==actions[1]['wait_returncode']==-signal.SIGKILL and not actions[1]['wait_timed_out']
    if cfg['mode'] in ('cpu','wall','rss','fault'):
        assert process['returncode'] in (-signal.SIGTERM,-signal.SIGKILL) and process['termination_actions']
        assert not (folder/'final.json').exists()
    else:assert process['returncode']==0 and not process['termination_actions'] and not independent
    if cfg['mode']=='cpu':
        event=next(item['event'] for item in trace if item['event'].get('query') and item['event']['query']['stdout'].strip()
            and ps(item['event']['query']['stdout'],pid)['cpu']>=3.)
        crossing=ps(event['query']['stdout'],pid)['cpu'];assert 3.<=crossing<=3.5
        progress=read(folder/'progress.json');assert progress['identity']==process['identity'] and progress['signals']
        for e in progress['signals']:
            assert e['signum']==signal.SIGXCPU and e['phase']=='cpu_spin'
            assert e['handled_at']['pid']==pid and e['handled_at']['rlimit_cpu']==[1,3] and e['handled_at']['cpu_absolute']>=.9
        assert process['controlled_signal'] is None and actions[0]['requested_at']>=event['query']['end']
    if cfg['mode']=='rss':
        pre=read(folder/'allocation_start.json')
        assert pre['at']['peak_rss_bytes']<67108864 and pre['committed_bytes']==100663296
        assert rss_max>67108864
        event=next(item['event'] for item in trace if item['event'].get('query') and item['event']['query']['stdout'].strip()
            and ps(item['event']['query']['stdout'],pid)['rss']>67108864)
        assert event['query']['end']>=pre['at']['monotonic']
    if cfg['mode']=='terminal':
        permission=process['exit_permission'];assert permission and permission['before']['returncode'] is None
        assert permission['before']['at']<=permission['at']<=permission['released_at']
        assert permission['single_query']['start']-permission['released_at']>=.05
        assert len(z_records)==1 and z_records[0]['query']==permission['single_query'] and positive_live
        assert positive_live[-1]['query']['end']<=permission['released_at']
        ready=read(folder/'ready.json');assert ready['identity']==process['identity'] and ready['phase']=='exit_permission_barrier'
        live=ps(permission['positive_live_record']['stdout'],pid)
        assert live['state']!='Z' and live['cpu']>=.1 and permission['positive_live_record']['start']>=ready['at']['monotonic']
        assert sum(item['event'].get('query') is not None and item['event']['query']['start']>=permission['released_at'] for item in trace)==1
    if cfg['mode']=='fault':assert len(fault_records)==1
    response=None
    if actions:
        trigger=next(item['event']['after']['at'] for item in trace if item['decision']['censor_reasons'])
        response=dict(first_trigger_observed_at=trigger,first_signal_requested_at=actions[0]['requested_at'],
            response_seconds=actions[0]['requested_at']-trigger,measured_CPU_overshoot=max(0.,cpu_max-cfg['limits']['cpu']),
            observed_RSS_overshoot=max(0,rss_max-cfg['limits']['rss']),confirmed_wall_overshoot=max(0.,last-process['started_monotonic']-cfg['limits']['wall']))
        assert response['response_seconds']>=0
    return dict(cpu_highwater=cpu_max,rss_highwater=rss_max,observed_Z_records=len(z_records),termination_response=response,
        terminal_zero_inferred_without_state=False,unobserved_CPU_after_last_sample_not_claimed_measured=True)

def audit_final(folder,cfg,process):
    if cfg['mode'] in ('cpu','wall','rss','fault'):return None
    final=read(folder/'final.json');restore=read(folder/'handler_restoration.json');start=read(folder/'startup.json')
    identity=process['identity']
    assert final['identity']==restore['identity']==start['identity']==identity
    assert final['finalized'] is True and final['handler_restored'] is True and final['raw_payload_complete'] is True
    assert restore['restored'] is True and restore['previous']==restore['current']==start['initial_handler']
    assert final['signals']==restore['stable_signals'] and final['finalized_at']['monotonic']>=restore['at']['monotonic']
    assert read(folder/'provisional_result.json')['finalized'] is False
    assert final['oracle_or_research_inputs_used'] is False
    assert start['after_limits']['rlimit_cpu']==cfg['OS_cpu_limits']
    if cfg['mode']=='terminal':
        assert final['native_optimizer_calls']==0 and not any(final['native_modules_after_mode'].values()) and not final['signals']
        return final
    manifest=read(folder/'raw_manifest.json');meta=read(folder/'raw_metadata.json')
    assert manifest['identity']==meta['identity']==identity and final['raw_manifest_sha256']==sha(folder/'raw_manifest.json')
    for name,digest in manifest['files'].items():assert sha(folder/name)==digest
    assert 'function' in meta['handler_while_raw_saved']
    assert manifest['persisted_at']['monotonic']<=restore['at']['monotonic']
    assert meta['solver_status']==final['solver_status'] and meta['has_incumbent']==final['has_incumbent']
    actual=read(folder/'environment_actual.json');environment=read(ROOT/'environment.json')
    assert actual['imported_files']==environment['imported_files'] and actual['thread_environment']==environment['intended_worker_thread_environment']
    if cfg['mode']!='mock':
        started=read(folder/'interpretation_started.json')
        assert started['identity']==identity and started['raw_manifest_sha256']==sha(folder/'raw_manifest.json')
        assert manifest['persisted_at']['monotonic']<=started['at']['monotonic']
        assert len(meta['warnings'])==1
        message=meta['warnings'][0];prefix='Unrecognized options detected: ';suffix='. These will be passed to HiGHS verbatim.'
        assert message.startswith(prefix) and message.endswith(suffix)
        assert ast.literal_eval(message[len(prefix):-len(suffix)])==set(cfg['expected_forwarded_options'])
    else:assert meta['warnings']==[]
    if cfg['mode']=='parity':
        toy=cfg['fixture'];feasible=[]
        for bits in itertools.product((0,1),repeat=len(toy['weights'])):
            if all(sum(a*b for a,b in zip(row,bits))%2==target for row,target in zip(toy['H']+toy['L'],toy['syndrome']+toy['logical_target'])):
                feasible.append(math.fsum(float(w) for w,bit in zip(toy['weights'],bits) if bit))
        assert len(feasible)==toy['feasible_vectors'] and final['solver_status']==(0 if feasible else 2)
        if feasible:
            x,ints,score,exact=verify_parity_raw(toy,np.load(folder/'raw.npz')['x'])
            assert np.array_equal(x,np.load(folder/'validated.npz')['x']) and np.array_equal(ints,np.load(folder/'validated.npz')['integer_solution'])
            assert score==min(feasible)==toy['minimum']==final['incumbent_score']
        else:assert not final['has_incumbent'] and not (folder/'raw.npz').exists()
    else:
        fixture=np.load(folder/'fixture.npz');edges=fixture['edges'];cost=fixture['cost']
        rng=np.random.default_rng(cfg['seed']);expected=np.transpose(np.nonzero(np.triu(rng.random((cfg['n'],cfg['n']))<.08,1)))
        assert np.array_equal(edges,expected) and np.array_equal(cost,-(1.+.001*rng.random(cfg['n'])))
        assert final['solver_status']==1 and final['has_incumbent']==cfg['expected_incumbent']
        if final['has_incumbent']:
            raw=np.load(folder/'raw.npz')['x'];x=np.load(folder/'validated.npz')['x']
            assert raw.shape==cost.shape and np.isfinite(raw).all() and np.max(abs(raw-np.rint(raw)))<=1e-7
            assert np.array_equal(np.rint(raw).astype(np.int64),x) and np.isin(x,(0,1)).all()
            assert np.all(x[edges[:,0]]+x[edges[:,1]]<=1)
            assert math.fsum(float(w) for w,bit in zip(cost,x) if bit)==final['incumbent_score']
        else:assert not (folder/'raw.npz').exists()
    if cfg['inject_signal']:
        injected=process['controlled_signal'];assert injected['pid']==process['pid'] and injected['signum']==signal.SIGXCPU
        assert injected['signal_API_returned'] is True and injected['before']['returncode'] is None
        assert injected['marker']['identity']==identity and injected['at']>=injected['marker']['at']['monotonic']+.02
        assert final['signals'] and all(e['signum']==signal.SIGXCPU and e['handled_at']['pid']==process['pid']
            and injected['at']<=e['handled_at']['monotonic']<=restore['at']['monotonic']
            and e['handled_at']['rlimit_cpu']==cfg['OS_cpu_limits'] and 'function' in e['handled_at']['sigxcpu_handler'] for e in final['signals'])
        if cfg['mode']=='mock':
            assert final['native_optimizer_calls']==0 and final['exception_restoration_passed'] is True
            assert injected['marker']['phase']=='guarded_persistence'
            assert any(e['phase']=='persisting_result' for e in final['signals'])
        else:
            assert injected['marker']['phase']=='solver_call'
            assert meta['before_call']['monotonic']<=injected['at']<=meta['after_call']['monotonic']
    else:assert not final['signals'] and process['controlled_signal'] is None
    return final

def audit_config(cfg,index,name,spec):
    fixtures={r['name']:r for r in read(ROOT/'entry_fixtures.json')['fixtures']}
    modes={n:'parity' for n in fixtures}
    modes.update(timeout_none='MIS',timeout_incumbent='MIS',signal_during_call='MIS',signal_during_persistence='mock',
        parent_CPU='cpu',parent_wall='wall',parent_RSS='rss',observed_terminal_Z='terminal',malformed_active_monitor='fault')
    mode=modes[name];assert cfg['mode']==mode and cfg['name']==cfg['identity']['name']==name and cfg['identity']['index']==index
    assert cfg['scope']=='synthetic_entry_only' and cfg['output']==str((ROOT/'entry'/name).resolve())
    assert cfg['identity']['prepared_protocol_sha256']==sha(ROOT/'prepared_protocol.json')
    for source,digest in cfg['identity']['sources'].items():assert sha(ROOT/source)==digest
    expected_limits=dict(cpu=10.,wall=8.,rss=1073741824);os_limits=[10,12]
    if name=='parent_CPU':expected_limits['cpu']=3.;os_limits=[1,3]
    if name=='parent_wall':expected_limits['wall']=.15
    if name=='parent_RSS':expected_limits['rss']=67108864
    assert cfg['limits']==expected_limits and cfg['OS_cpu_limits']==os_limits
    assert cfg['inject_signal']==(name in ('signal_during_call','signal_during_persistence'))
    if mode=='parity':
        assert cfg['fixture']==fixtures[name] and cfg['expected_status']==fixtures[name]['expected_solver_status']
        assert cfg['solver_options']==spec['entry']['parity_options']
        assert set(cfg['expected_forwarded_options'])=={'threads','random_seed','mip_feasibility_tolerance'}
    if mode in ('MIS','mock'):
        assert cfg['n']==(6 if mode=='mock' else 200) and cfg['seed']==2026111801
        assert cfg['expected_incumbent']==(name!='timeout_none')
        assert cfg['solver_options']==dict(spec['entry']['MIS']['options'],time_limit=0. if name=='timeout_none' else .15)
        assert set(cfg['expected_forwarded_options'])=={'threads','random_seed'}
    if mode=='rss':assert cfg['committed_bytes']==100663296

def main():
    assert not (ROOT/'audit_result.json').exists(),'Preserve audit'
    frozen=read(ROOT/'frozen.json')
    for path,digest in frozen['files'].items():assert sha(path)==digest,path
    for path,digest in read(ROOT/'output_manifest.json')['files'].items():assert sha(ROOT/path)==digest,path
    plan=read(ROOT/'execution_plan.json');result=read(ROOT/'entry_result.json');spec=read(ROOT/'prepared_protocol.json')
    assert sha(ROOT/'prepared_protocol.json')==sha(ROOT.parent/'reference_integration_protocol_2026-11-18/protocol.json')
    assert result['frozen_sha256']==sha(ROOT/'frozen.json')
    assert result['passed'] and result['controller_wall_seconds']<=120.
    assert len(result['rows'])==13 and [r['name'] for r in result['rows']]==plan['case_names']
    checked=[];attempts=0;returns=0
    for index,(row,filename) in enumerate(zip(result['rows'],plan['config_files'])):
        cfg=read(ROOT/'configs'/filename);folder=ROOT/'entry'/cfg['name'];process=read(folder/'process.json')
        audit_config(cfg,index,plan['case_names'][index],spec)
        identity=dict(cfg['identity'],config_sha256=sha(ROOT/'configs'/filename))
        assert process['identity']==identity and read(folder/'launch.json')['identity']==identity
        cleanup=read(folder/'cleanup_summary.json');assert cleanup['identity']==identity and cleanup['reaped'] is True
        assert cleanup['fallback_cleanup'] is False and cleanup['actions']==process['termination_actions']
        assert read(folder/'spawn_attempt.json')['identity']==identity and cleanup['pid']==process['pid']
        start=read(folder/'startup.json');assert start['identity']==identity and start['after_limits']['pid']==process['pid']
        assert start['after_limits']['rlimit_cpu']==cfg['OS_cpu_limits']
        if cfg['mode'] in ('cpu','wall','rss','terminal','fault'):assert not any(start['native_modules_before_mode'].values())
        monitor=audit_monitor(folder,cfg,process);final=audit_final(folder,cfg,process)
        calls=rows(folder/'native_journal.jsonl') if (folder/'native_journal.jsonl').exists() else []
        count=sum(c['event']=='optimizer_start' for c in calls);returned=sum(c['event']=='optimizer_return_persisted' for c in calls)
        assert count==returned==(1 if cfg['mode'] in ('parity','MIS') else 0)
        assert all(c['identity']==identity for c in calls)
        if calls:
            assert read(folder/'optimizer_attempt.json')==calls[0]
            assert [c['event'] for c in calls]==['optimizer_start','optimizer_return_persisted']
            assert calls[1]['raw_manifest_sha256']==sha(folder/'raw_manifest.json')
            assert calls[1]['at']['monotonic']>=read(folder/'raw_manifest.json')['persisted_at']['monotonic']
        else:assert not (folder/'optimizer_attempt.json').exists()
        attempts+=count;returns+=returned
        checked.append(dict(name=cfg['name'],passed=True,optimizer_attempts=count,process_returncode=process['returncode'],
            process_censor_reasons=process['accounting']['censor_reasons'],monitor=monitor))
    assert attempts==returns==result['optimizer_api_attempts']==7 and result['experimental_workers']==13
    assert result['worker_launch_attempts']==13 and result['malformed_native_journal_lines']==0
    assert result['real_research_calls']==result['physical_shots']==0
    prep=ROOT.parent/'reference_integration_protocol_2026-11-18'
    for name,digest in read(prep/'manifest.json')['files'].items():assert sha(prep/name)==digest,name
    report=dict(passed=True,scope='synthetic_native_entry_only',checks=checked,optimizer_api_attempts=attempts,
        optimizer_returns_persisted=returns,experimental_workers=13,controller_wall_seconds=result['controller_wall_seconds'],
        historical_optimizer_api_attempts=18,cumulative_optimizer_api_attempts=25,real_research_calls=0,physical_shots=0,
        real_case_launch_supported=False,ordinary_timeouts_and_signal_persistence_validated=True,
        process_state_and_owned_reaping_validated=True,parent_CPU_wall_RSS_controls_validated=True,
        OS_hard_CPU_enforcement_proved=False,abrupt_parent_death_containment_validated=False,
        model_and_incumbents_independently_checked=True,scientific_improvement_claim=False,
        frozen_sha256=sha(ROOT/'frozen.json'),audit_source_sha256=sha(Path(__file__)))
    save(ROOT/'audit_result.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
