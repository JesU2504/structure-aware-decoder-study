"""Deterministic policy contract examples; zero solvers, workers or OS queries."""
import hashlib,json
from pathlib import Path
from accounting_policy import Accounting,cpu_seconds,parse_record,classify_execution
ROOT=Path(__file__).resolve().parent

def observation(t,cpu='.43',rss='100',stat='R',rc=None,pid=42,query_rc=0,raw=None):
    # TIME is an actual ps-style token; caller supplies seconds after '0:00'.
    token='0:00'+cpu if cpu.startswith('.') else cpu
    if raw is None:raw=f'{pid} {stat} {rss} {token}'
    return dict(before=dict(at=t,returncode=None),query=dict(start=t+.001,end=t+.002,
        stdout=raw,returncode=query_rc),after=dict(at=t+.003,returncode=rc))
def reap(t,rc=0):
    return dict(before=dict(at=t,returncode=rc),query=None,after=dict(at=t+.001,returncode=rc))
def good_report(**changes):
    return dict(identity_valid=True,finalized=True,handler_restored=True,stable_signal_ledger=True,
        finalized_after_restoration=True,raw_payload_complete=True,solver_status=1,signals=[],**changes)

def main():
    target=ROOT/'policy_checks.json';assert not target.exists(),'Preserve checks'
    names=[]
    def checked(name,condition):
        assert condition,name
        names.append(name)
    for token,value in [('0:00.00',0.),('1:02.34',62.34),('1:02:03.45',3723.45),('0-02:03:04',7384.),('2-01:02:03',176523.)]:
        checked('valid_cpu_'+token,abs(cpu_seconds(token)-value)<1e-8)
    for token in ('nan','-1:00.00','0:60.00','1:60:00','0-02:03','0-24:00:00'):
        try:cpu_seconds(token)
        except ValueError:checked('reject_cpu_'+token,True)
        else:raise AssertionError(token)
    a=Accounting(42);a.advance(observation(.1,cpu='.00'))
    checked('initial_live_zero_cpu_with_positive_RSS_allowed',not a.censor_reasons)
    a=Accounting(42);a.advance(observation(.1));a.advance(observation(.2,cpu='.00',rss='0',stat='Z',rc=0))
    checked('terminal_Z_zero_retains_positive_CPU',a.cpu_highwater==.43 and a.phase=='REAPED' and not a.censor_reasons)
    a=Accounting(42);a.advance(observation(.1));a.advance(observation(.2,cpu='.00',rss='0',stat='R',rc=0))
    checked('live_zero_then_reap_does_not_excuse_bad_sample',bool(a.censor_reasons) and a.phase=='REAPED')
    a=Accounting(42);a.advance(observation(.1));a.advance(observation(.2,cpu='.20',rc=0))
    checked('positive_live_CPU_decrease_censored_even_when_reaped',bool(a.censor_reasons))
    a=Accounting(42);a.advance(observation(.1,cpu='.00',stat='Z'));r=a.advance(observation(.2))
    checked('Z_to_live_or_query_during_reaping_rejected',bool(a.censor_reasons) and not r['injections_allowed'])
    a=Accounting(42);a.advance(observation(.1,cpu='1:30.00',stat='Z',rss='0',rc=0))
    checked('terminal_positive_CPU_threshold_censored','cpu_limit' in a.censor_reasons)
    a=Accounting(42);r=a.advance(observation(.1,cpu='1:30.00',stat='Z',rss='0'))
    checked('censored_Z_requests_reaping_without_live_signals',r['action']=='reap_censored' and not r['injections_allowed'])
    a=Accounting(42);a.advance(observation(.1,raw='',query_rc=1,rc=0))
    checked('PID_gone_with_owned_reap_is_terminal',a.phase=='REAPED' and not a.censor_reasons)
    a=Accounting(42);r=a.advance(observation(.1,raw='',query_rc=1))
    checked('unconfirmed_absence_requires_bounded_reap',r['action']=='wait_reap' and not r['injections_allowed'])
    a.advance(reap(.2));checked('pending_absence_confirmed_within_grace',a.phase=='REAPED' and not a.censor_reasons)
    a=Accounting(42);a.advance(observation(.1,raw='',query_rc=1));a.advance(reap(.8))
    checked('reaping_grace_exceeded_stays_censored','reaping_grace_exceeded' in a.censor_reasons)
    a=Accounting(42);a.advance(observation(.1,raw='',query_rc=1))
    r=a.advance(dict(before=dict(at=.8,returncode=None),query=None,after=dict(at=.801,returncode=None)))
    checked('unconfirmed_absence_after_grace_requests_termination',r['action']=='terminate' and not r['terminal_state_observed'])
    for label,event in [('pid_mismatch',observation(.1,pid=43)),('unknown_stat',observation(.1,stat='?')),
        ('invalid_modifier',observation(.1,stat='R?')),('ambiguous_live_zero_RSS',observation(.1,rss='0')),
        ('failed_query_with_data',observation(.1,query_rc=2))]:
        a=Accounting(42);a.advance(event);checked(label,bool(a.censor_reasons))
    a=Accounting(42);e=observation(.1);e['query']['end']=1.2;e['after']['at']=1.3;a.advance(e)
    checked('query_timeout_censored',bool(a.censor_reasons))
    a=Accounting(42);e=observation(.1);a.advance(e);a.advance(e)
    checked('duplicate_timestamps_censored',bool(a.censor_reasons))
    a=Accounting(42);a.advance(observation(.2));a.advance(observation(.1))
    checked('out_of_order_timestamps_censored',bool(a.censor_reasons))
    a=Accounting(42);a.advance(observation(.1,rc=0));a.advance(observation(.2))
    checked('no_query_after_owned_process_reaped',bool(a.censor_reasons))
    a=Accounting(42);e=reap(.1);e['query']=observation(.1)['query'];a.advance(e)
    checked('already_reaped_before_query_rejected',bool(a.censor_reasons))
    a=Accounting(42);a.advance(observation(.1,rc=0));a.checked_child_cpu(42,.1,90.)
    checked('checked_final_CPU_updates_resource_censoring','cpu_limit' in a.censor_reasons and a.cpu_highwater==90.)
    a=Accounting(42);a.advance(observation(.1));a.checked_child_cpu(42,.1,.438)
    checked('child_CPU_cannot_mix_with_live_rounded_counters',bool(a.censor_reasons) and a.cpu_highwater==.43)
    a=Accounting(42);a.advance(observation(.1,rss='1048577',rc=0))
    checked('RSS_threshold_censored','rss_limit' in a.censor_reasons)
    a=Accounting(42);a.advance(reap(120.))
    checked('late_confirmation_wall_censored','wall_limit' in a.censor_reasons)
    a=Accounting(42);a.advance(observation(.1,rc=0));base=good_report()
    checked('ordinary_return_requires_clean_finalization',classify_execution(a,base)=='finalized_ordinary_return')
    for key in ('identity_valid','finalized','handler_restored','stable_signal_ledger','finalized_after_restoration','raw_payload_complete'):
        bad=dict(base);bad[key]=False
        checked('invalid_report_'+key,classify_execution(a,bad)=='invalid_finalization_or_identity')
    signalled=dict(base,signals=[dict(signum=24)])
    checked('signal_preserved_return_is_separate',classify_execution(a,signalled)=='finalized_signal_observed_return')
    checked('missing_final_record_censored',classify_execution(a,None)=='censored_missing_final_report')
    a=Accounting(42);a.advance(reap(.1,1))
    checked('bad_exit_cannot_be_overridden_by_result',classify_execution(a,base)=='censored_process_or_monitor')
    a=Accounting(42);a.advance(observation(.1,cpu='1:30.00',rc=0))
    checked('resource_censoring_cannot_be_overridden_by_result',classify_execution(a,base)=='censored_process_or_monitor')
    checked('backend_status_is_not_exclusion',classify_execution(Accounting(42,phase='REAPED',returncode=0),dict(base,solver_status=2))=='backend_or_validation_error')
    for key,value in [('owned_pid',True),('owned_pid',0),('cpu_limit',float('inf')),('wall_limit',float('nan')),
        ('rss_limit',True),('rss_limit',.5),('query_timeout',0),('reap_grace',-1),('started_at',float('nan'))]:
        try:Accounting(**dict({'owned_pid':42},**{key:value}))
        except ValueError:checked('invalid_configuration_'+key,True)
        else:raise AssertionError((key,value))
    malformed=[None,[],{},dict(before=[],after=[]),dict(before={},after=[])]
    for i,event in enumerate(malformed):
        a=Accounting(42);a.advance(event);checked('malformed_event_mapping_'+str(i),bool(a.censor_reasons))
    for key,value in [('stdout',None),('stdout',123),('returncode',False),('returncode',None)]:
        event=observation(.1);event['query'][key]=value
        a=Accounting(42);a.advance(event);checked('malformed_query_'+key+'_'+str(value),bool(a.censor_reasons))
    for status in (True,False,None,'1'):
        a=Accounting(42);a.advance(reap(.1))
        checked('strict_solver_status_'+str(status),classify_execution(a,dict(base,solver_status=status))=='backend_or_validation_error')
    for signals in (None,{},7,[None],[dict(signum=True)],[dict(signum=0)]):
        a=Accounting(42);a.advance(reap(.1))
        checked('strict_signal_ledger_'+str(signals),classify_execution(a,dict(base,signals=signals))=='invalid_finalization_or_identity')
    report=dict(passed=True,scope='deterministic_policy_only',checks=names,count=len(names),
        source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('accounting_policy.py','check_policy.py')},
        optimizer_api_attempts=0,experimental_workers=0,OS_queries=0,research_cases=0,
        actual_native_adapter_integration_validated=False,platform_process_state_behavior_validated=False)
    target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
if __name__=='__main__':main()
