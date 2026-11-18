"""Independent audit of stdlib runner evidence. Imports none of its helpers."""
import hashlib,json,math,os,signal,sys
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ps(raw,pid):
    fields=raw.split();assert len(fields)==4 and fields[0].isdigit() and int(fields[0])==pid and fields[2].isdigit()
    stat=fields[1];assert stat and len(stat)<=16 and all(c in '+<>AELNSsVWX' for c in stat[1:])
    kind='live' if stat[0] in 'IRSTU' else 'candidate' if stat[0]=='Z' or stat=='?E' else 'invalid'
    assert kind!='invalid'
    t=fields[3].split(':');assert len(t) in (2,3) and all(x.isdigit() for x in t[:-1])
    sec=Decimal(t[-1]);assert sec.is_finite() and 0<=sec<60
    if len(t)==3:assert int(t[1])<60
    cpu=sec+60*int(t[-2])+(3600*int(t[0]) if len(t)==3 else 0)
    return dict(kind=kind,cpu=float(cpu),rss=int(fields[2])*1024,stat=stat)
def interim(r,cfg):
    cpu=0.;rss=0;pending=None;invalid=False;faults=0;CPU_cross=None;RSS_cross=None
    for q in r['ps_queries']:
        assert pending is None and not invalid and not q['error'] and q['returncode'] in (0,1)
        if q['raw'].strip():
            assert q['returncode']==0
            now=ps(q['raw'],r['pid']);injection=r['controlled_injection']
            if injection and q['start']==injection['mutated']['start']:
                faults+=1;true=ps(injection['truth']['raw'],r['pid'])
                for key in ('start','end','raw','returncode','kernel_events_before_query','kernel_events_after_query'):
                    assert q[key]==injection['mutated'][key]
                assert cpu>0 and true['kind']=='live' and true['cpu']>=.1 and true['rss']>0
                changed='R' if cfg['fault']=='live_reset' else '?E'
                expected=f'{r["pid"]} {changed} {true["rss"]//1024 if changed=="R" else 0} 0:00.00\n'
                assert q['raw']==expected and injection['truth']['raw']!=q['raw']
            if now['kind']=='live' and (now['rss']==0 or now['cpu']<cpu):
                invalid=True
            else:
                cpu=max(cpu,now['cpu']);rss=max(rss,now['rss'])
                if CPU_cross is None and cpu>=cfg['cpu_limit']:CPU_cross=q['end']
                if RSS_cross is None and rss>cfg['rss_limit']:RSS_cross=q['end']
                if now['kind']=='candidate':pending=q['end'];assert q['terminal_candidate']
        else:
            pending=q['end'];assert q['PID_absent_pending_confirmation']
    assert cpu==r['ps_cpu_highwater'] and rss==r['ps_RSS_highwater']
    assert (pending is not None)==r['terminal_telemetry_unavailable']
    if cfg.get('fault'):assert faults==1
    else:assert not faults and r['controlled_injection'] is None
    expected=set()
    if invalid:expected.add('monitor_invalid: Invalid live telemetry')
    if pending is not None:
        if cfg['name']=='exit_candidate_timeout':expected.add('exit_confirmation_timeout')
        else:assert r['kernel_final']['reaped_at']-pending<=.5
    u=r['kernel_final']['usage']
    if cpu>=cfg['cpu_limit'] or u['total_cpu']>=cfg['cpu_limit']:expected.add('cpu_limit')
    if rss>cfg['rss_limit'] or u['peak_rss_bytes']>cfg['rss_limit']:expected.add('rss_limit')
    if r['kernel_final']['reaped_at']-r['started']>=cfg['wall_limit']:expected.add('wall_limit')
    if r['setup_error']:expected.add('setup_or_runner_error')
    assert set(r['reasons'])==expected
    return dict(cpu_cross=CPU_cross,rss_cross=RSS_cross,pending_at=pending,invalid_live=invalid)
def main():
    target=ROOT/'audit_result.json';assert not target.exists()
    frozen=read(ROOT/'frozen.json')
    for path,digest in frozen['files'].items():assert sha(path)==digest,path
    for name,digest in read(ROOT/'output_manifest.json')['files'].items():assert sha(ROOT/name)==digest,name
    execution=read(ROOT/'execution.json');plan=read(ROOT/'plan.json')
    assert execution['passed'] and len(execution['rows'])==12 and execution['controller_seconds']<=90
    assert execution['workers_started']==execution['launch_attempts']==12
    names=['normal_exit','nonzero_exit','cpu_work','final_CPU_over_budget','parent_wall','parent_CPU','parent_RSS',
        'TERM_to_KILL','setup_failure','exit_candidate_confirmed','live_counter_reset','exit_candidate_timeout']
    modes=['normal','nonzero','cpu_work','final_CPU','sleep','spin','rss','ignore_TERM','sleep','barrier','barrier','barrier']
    assert plan['max_workers']==12 and plan['controller_seconds']==90 and plan['admission_reserve']==8
    assert [r['name'] for r in execution['rows']]==names
    checks=[]
    for index,(row,file) in enumerate(zip(execution['rows'],plan['configs'])):
        cfg=read(ROOT/'configs'/file);out=ROOT/'runs'/cfg['name'];r=read(out/'result.json');pid=r['pid']
        assert r['name']==cfg['name']==row['name'] and r['nonce']==cfg['nonce']==plan['nonce'] and row['passed']
        assert cfg['name']==names[index] and cfg['mode']==modes[index] and cfg['OS_CPU_request']==[5,6]
        assert cfg['cpu_limit']==(.05 if cfg['name']=='final_CPU_over_budget' else .25 if cfg['name']=='parent_CPU' else 3.)
        assert cfg['wall_limit']==(.15 if cfg['name']=='parent_wall' else .3 if cfg['name']=='TERM_to_KILL' else 4.)
        assert cfg['rss_limit']==(67108864 if cfg['name']=='parent_RSS' else 268435456)
        assert cfg['output']==str(out.resolve())
        assert not r['ownership_errors'] and r['kernel_final']['pid']==pid
        events=r['kernel_events'];finals=[];previous=0.
        for e in events:
            assert e['requested_pid']==pid and e['flags']==os.WNOHANG and e['started']>=previous and e['ended']>=e['started']
            previous=e['ended']
            if e.get('interrupted'):
                assert 'returned_pid' not in e and 'final' not in e;continue
            assert e['returned_pid'] in (0,pid)
            if e['returned_pid']==0:assert e['status_and_usage_ignored'] is True and 'raw_status' not in e and 'final' not in e
            else:
                assert os.WIFEXITED(e['raw_status']) or os.WIFSIGNALED(e['raw_status'])
                finals.append(e['final'])
        assert len(finals)==1 and events[-1]['returned_pid']==pid and finals[0]==r['kernel_final']
        f=finals[0];u=f['usage'];assert f['returncode']==os.waitstatus_to_exitcode(f['raw_status'])
        assert all(math.isfinite(u[k]) and u[k]>=0 for k in ('user_cpu','system_cpu','total_cpu','peak_rss_bytes'))
        assert u['total_cpu']==u['user_cpu']+u['system_cpu']
        assert u['native_RSS_unit']==('bytes' if sys.platform=='darwin' else 'KiB')
        assert u['peak_rss_bytes']==u['native_peak_rss']*(1 if sys.platform=='darwin' else 1024)
        for q in r['ps_queries']:
            assert q['start']<=q['end']<=r['ended'] and q['start']<f['reaped_at']
            assert 0<q['kernel_events_before_query']<=len(events)
            assert events[q['kernel_events_before_query']-1]['returned_pid']==0
        for a in r['signals']:
            assert a['pid']==pid and a['requested_at']<f['reaped_at'] and a['API_returned']
            assert a['wait_started']<=a['wait_ended'] and a['wait_ended']-a['wait_started']<=1.1
        reconstructed=interim(r,cfg)
        rc=f['returncode'];name=cfg['name'];reasons=r['reasons']
        if name in ('normal_exit','cpu_work','exit_candidate_confirmed'):assert rc==0 and not reasons and r['classification']=='ordinary_exit'
        if name=='nonzero_exit':assert rc==7 and r['classification']=='nonzero_or_signal_exit' and not reasons
        if name=='cpu_work':assert u['total_cpu']>=.1
        if name=='final_CPU_over_budget':
            assert rc==0 and reasons==['cpu_limit'] and u['total_cpu']>=.05 and not r['signals'] and not r['ps_queries']
            assert r['observation_gap']['control_only'] and r['classification']=='censored'
        if name in ('parent_wall','parent_CPU','parent_RSS','TERM_to_KILL','setup_failure','live_counter_reset','exit_candidate_timeout'):
            assert r['classification']=='censored' and r['signals'] and r['signals'][0]['signum']==signal.SIGTERM
            if name=='TERM_to_KILL':
                assert rc==-9 and len(r['signals'])==2 and r['signals'][0]['wait_timed_out'] and r['signals'][1]['signum']==9
                assert r['signals'][0]['returncode_after_wait'] is None and r['signals'][0]['wait_ended']-r['signals'][0]['wait_started']>=.49
                assert r['signals'][1]['requested_at']>=r['signals'][0]['wait_ended'] and r['signals'][1]['returncode_after_wait']==-9
                assert read(out/'ready.json')['TERM_handler']==signal.SIG_IGN
                assert read(out/'ready.json')['at']['monotonic']<=r['signals'][0]['requested_at']
            else:assert rc==-15 and len(r['signals'])==1 and r['signals'][0]['returncode_after_wait']==-15 and not r['signals'][0]['wait_timed_out']
        if name=='parent_CPU':
            assert reasons==['cpu_limit'] and reconstructed['cpu_cross'] is not None
            assert r['signals'][0]['requested_at']>=reconstructed['cpu_cross']
        if name in ('parent_wall','TERM_to_KILL'):assert reasons==['wall_limit'] and r['signals'][0]['requested_at']-r['started']>=cfg['wall_limit']
        if name=='parent_RSS':
            assert reasons==['rss_limit'] and reconstructed['rss_cross'] is not None
            assert read(out/'allocation_start.json')['at']['peak_RSS']<67108864
            assert reconstructed['rss_cross']>=read(out/'allocation_start.json')['at']['monotonic']
            assert r['signals'][0]['requested_at']>=reconstructed['rss_cross']
        if name=='setup_failure':assert reasons==['setup_or_runner_error'] and 'Controlled post-spawn' in r['setup_error']
        if cfg.get('fault'):
            i=r['controlled_injection'];assert i and i['truth']['raw']!=i['mutated']['raw']
            fields=i['truth']['raw'].split();assert int(fields[0])==pid and fields[1][0] in 'IRSTU'
            ready=read(out/'ready.json');assert i['truth']['start']>=ready['at']['monotonic']
            if name=='live_counter_reset':assert reasons==['monitor_invalid: Invalid live telemetry']
            if name=='exit_candidate_timeout':assert reasons==['exit_confirmation_timeout'] and r['signals'][0]['requested_at']>=i['at']+.49
            if name=='exit_candidate_timeout':assert r['signals'][0]['requested_at']>=reconstructed['pending_at']+.5
            if name=='exit_candidate_confirmed':assert r['terminal_telemetry_unavailable'] and i['permission_sent_at']>=i['at'] and rc==0
        if (out/'child_start.json').exists():
            child=read(out/'child_start.json');assert child['identity']==dict(name=name,nonce=cfg['nonce'],pid=pid)
            assert child['OS_CPU_request']==[5,6] and not child['native_packages_present']
        assert r['native_optimizers_called']==r['quantum_decoders_called']==0
        checks.append(dict(name=name,passed=True,returncode=rc,classification=r['classification'],
            kernel_CPU=u['total_cpu'],kernel_peak_RSS=u['peak_rss_bytes'],interim_ps_CPU=r['ps_cpu_highwater'],
            terminal_telemetry_unavailable=r['terminal_telemetry_unavailable']))
    report=dict(passed=True,scope='stdlib_runner_only',checks=checks,workers=12,optimizer_calls=0,decoder_calls=0,
        research_cases=0,physical_samples=0,kernel_owned_reaping_and_usage_validated=True,
        source_specific_accounting_preserved=True,invalid_live_data_remains_censored=True,
        controlled_exit_candidates_kernel_confirmed=True,natural_questionmarkE_reproduction_claim=False,
        native_optimizer_integration_validated=False,instantaneous_resource_containment_proved=False,
        controller_seconds=execution['controller_seconds'],frozen_sha256=sha(ROOT/'frozen.json'))
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
