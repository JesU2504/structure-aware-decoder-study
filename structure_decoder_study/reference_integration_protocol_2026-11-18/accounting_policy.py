"""Prospective accounting policy prototype. Pure logic: no processes or solvers.

This does not implement a runtime monitor. A future controller must perform
the recorded polls/queries/actions and pass the separately frozen entry gate.
"""
from __future__ import annotations
from dataclasses import dataclass,field
from copy import deepcopy
import math,re

def cpu_seconds(token):
    if not re.fullmatch(r'(?:[0-9]+-)?[0-9]+:[0-9]{2}(?::[0-9]{2})?(?:\.[0-9]+)?',token):
        raise ValueError('Invalid CPU token')
    prefix='-' in token;days=0
    if prefix:
        d,token=token.split('-');days=int(d)
    parts=token.split(':');seconds=float(parts[-1])
    if seconds>=60:raise ValueError('Invalid seconds')
    if len(parts)==2:
        if prefix:raise ValueError('Day prefix requires hours')
        return int(parts[0])*60+seconds
    hours,minutes=int(parts[0]),int(parts[1])
    if minutes>=60 or (prefix and hours>=24):raise ValueError('Invalid hours/minutes')
    value=days*86400+hours*3600+minutes*60+seconds
    if not math.isfinite(value):raise ValueError('Nonfinite CPU')
    return value

def parse_record(raw,owned_pid):
    fields=raw.split()
    if len(fields)!=4:raise ValueError('Expected PID,stat,RSS,TIME')
    pid,stat,rss,token=fields
    if not pid.isascii() or not pid.isdigit() or int(pid)!=owned_pid:raise ValueError('PID mismatch')
    if not stat or stat[0] not in 'IRSTUZ' or any(c not in '+<>AELNSsVWX' for c in stat[1:]):
        raise ValueError('Unknown Darwin process state/modifier')
    if not rss.isascii() or not rss.isdigit():raise ValueError('Invalid RSS')
    return dict(pid=owned_pid,stat=stat,state=stat[0],rss_bytes=int(rss)*1024,cpu_seconds=cpu_seconds(token),cpu_token=token)

def finite(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('Expected finite numeric observation')
    return float(value)

def code(value):
    if value is not None and (isinstance(value,bool) or not isinstance(value,int)):
        raise ValueError('Invalid Popen return code')
    return value

@dataclass
class Accounting:
    owned_pid:int
    started_at:float=0.
    cpu_limit:float=90.
    wall_limit:float=120.
    rss_limit:int=1073741824
    query_timeout:float=1.
    reap_grace:float=.5
    phase:str='RUNNING'
    cpu_highwater:float=0.
    rss_highwater:int=0
    last_at:float=0.
    reaping_started:float|None=None
    terminal_state_observed:bool=False
    returncode:int|None=None
    censor_reasons:list=field(default_factory=list)
    records:list=field(default_factory=list)
    cpu_sources:list=field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.owned_pid,bool) or not isinstance(self.owned_pid,int) or self.owned_pid<=0:
            raise ValueError('Invalid owned PID')
        if isinstance(self.rss_limit,bool) or not isinstance(self.rss_limit,int) or self.rss_limit<=0:
            raise ValueError('Invalid RSS budget')
        for key in ('cpu_limit','wall_limit','query_timeout','reap_grace'):
            if finite(getattr(self,key))<=0:raise ValueError('Invalid budget/grace')
        if self.phase not in ('RUNNING','REAPING','REAPED'):raise ValueError('Invalid phase')
        if finite(self.cpu_highwater)<0 or self.rss_highwater<0:raise ValueError('Invalid initial accounting')
        self.last_at=finite(self.started_at)

    def fail(self,reason):
        if reason not in self.censor_reasons:self.censor_reasons.append(reason)

    def budget(self,at):
        if self.cpu_highwater>=self.cpu_limit:self.fail('cpu_limit')
        if self.rss_highwater>self.rss_limit:self.fail('rss_limit')
        if at-self.started_at>=self.wall_limit:self.fail('wall_limit')

    def snapshot(self):
        action=('retain_censored' if self.phase=='REAPED' else 'reap_censored' if self.phase=='REAPING' and self.terminal_state_observed else 'terminate') if self.censor_reasons else (
            'terminal' if self.phase=='REAPED' else 'wait_reap' if self.phase=='REAPING' else 'continue')
        return dict(phase=self.phase,cpu_highwater=self.cpu_highwater,rss_highwater=self.rss_highwater,
            returncode=self.returncode,terminal_state_observed=self.terminal_state_observed,
            censor_reasons=list(self.censor_reasons),action=action,
            injections_allowed=self.phase=='RUNNING' and not self.censor_reasons)

    def advance(self,event):
        """Consume evidence with before/after Popen polls and optional ps query.

        No OS action is performed. Errors stay sticky across later reaping.
        A caller must execute terminate/reap actions and retain their evidence.
        """
        if not isinstance(event,dict):
            self.records.append(dict(invalid_event_type=type(event).__name__))
            self.fail('monitor_invalid: event is not a mapping');return self.snapshot()
        self.records.append(deepcopy(event))
        if self.phase=='REAPED':
            self.fail('observation_after_reaping');return self.snapshot()
        try:
            before=event['before'];after=event['after'];query=event.get('query')
            if not isinstance(before,dict) or not isinstance(after,dict):raise ValueError('Invalid poll mappings')
            if query is not None and not isinstance(query,dict):raise ValueError('Invalid query mapping')
            t0=finite(before['at']);t1=finite(after['at'])
            bcode=code(before['returncode']);acode=code(after['returncode'])
            if not self.last_at<=t0<=t1 or t1<=self.last_at:raise ValueError('Duplicate/out-of-order observation')
            if self.reaping_started is not None and t1-self.reaping_started>self.reap_grace:
                self.fail('reaping_grace_exceeded')
            if bcode is not None:
                if query is not None:raise ValueError('Query after reaping / PID reuse risk')
                if acode!=bcode:raise ValueError('Reaped return code changed')
            elif self.phase=='REAPING':
                if query is not None:raise ValueError('Query or live transition during reaping')
            else:
                if query is None:raise ValueError('Missing active-process query')
                if not isinstance(query.get('stdout'),str):raise ValueError('Invalid query stdout type')
                if isinstance(query.get('returncode'),bool) or not isinstance(query.get('returncode'),int):
                    raise ValueError('Invalid query return-code type')
                start=finite(query['start']);end=finite(query['end'])
                if not t0<=start<=end<=t1:raise ValueError('Invalid query interval')
                if query.get('error') or end-start>self.query_timeout:raise ValueError('Failed/timed-out query')
                if query['stdout'].strip():
                    if query['returncode']!=0:raise ValueError('Failed query with data')
                    record=parse_record(query['stdout'].strip(),self.owned_pid)
                    cpu=record['cpu_seconds'];rss=record['rss_bytes']
                    if record['state']!='Z':
                        # A live inconsistent record is invalid even if acode is now set.
                        if rss==0:raise ValueError('Ambiguous zero live RSS')
                        if cpu<self.cpu_highwater:raise ValueError('Live CPU counter decreased')
                    self.cpu_highwater=max(self.cpu_highwater,cpu)
                    self.rss_highwater=max(self.rss_highwater,rss)
                    self.cpu_sources.append(dict(kind='validated_ps',at=end,cpu=cpu,state=record['state']))
                    if record['state']=='Z':
                        self.phase='REAPING';self.reaping_started=end;self.terminal_state_observed=True
                else:
                    if query['returncode'] not in (0,1):raise ValueError('Unexplained empty-query failure')
                    # Missing PID is not proof of exit until owned Popen reaping.
                    self.phase='REAPING';self.reaping_started=end
            if acode is not None:
                self.phase='REAPED';self.returncode=acode
            elif bcode is not None:raise ValueError('Inconsistent reap evidence')
            self.last_at=t1;self.budget(t1)
        except (KeyError,TypeError,ValueError,OverflowError) as exc:
            self.fail('monitor_invalid: '+str(exc))
            # Preserve an independently confirmed reap without clearing the error.
            after=event.get('after',{})
            if not isinstance(after,dict):after={}
            value=after.get('returncode')
            if isinstance(value,int) and not isinstance(value,bool):
                self.phase='REAPED';self.returncode=value
        return self.snapshot()

    def checked_child_cpu(self,pid,at,cpu):
        """Caller first checks artifact hash/identity; include final CPU in budget.

        This is accounting evidence, not a proof that no unobserved peak occurred.
        """
        try:
            at=finite(at);cpu=finite(cpu)
            if self.phase!='REAPED' or pid!=self.owned_pid or cpu<0 or not self.started_at<=at<=self.last_at:
                raise ValueError('Invalid child CPU evidence')
            self.cpu_highwater=max(self.cpu_highwater,cpu)
            self.cpu_sources.append(dict(kind='checked_child_snapshot',at=at,cpu=cpu))
            self.budget(self.last_at)
        except (TypeError,ValueError) as exc:self.fail('child_evidence_invalid: '+str(exc))
        return self.snapshot()

def classify_execution(state,report):
    """Execution axis only. Does not validate a correction or a witness claim."""
    if state.censor_reasons or state.phase!='REAPED' or state.returncode!=0:
        return 'censored_process_or_monitor'
    if not isinstance(report,dict):return 'censored_missing_final_report'
    required=('identity_valid','finalized','handler_restored','stable_signal_ledger','finalized_after_restoration','raw_payload_complete')
    if not all(report.get(k) is True for k in required):return 'invalid_finalization_or_identity'
    status=report.get('solver_status')
    if isinstance(status,bool) or not isinstance(status,int) or status not in (0,1):return 'backend_or_validation_error'
    signals=report.get('signals')
    if not isinstance(signals,list):return 'invalid_finalization_or_identity'
    for event in signals:
        if not isinstance(event,dict) or isinstance(event.get('signum'),bool) or not isinstance(event.get('signum'),int) or event['signum']<=0:
            return 'invalid_finalization_or_identity'
    # Full ledger/timestamps are independently audited by the future adapter.
    if signals:return 'finalized_signal_observed_return'
    return 'finalized_ordinary_return'
