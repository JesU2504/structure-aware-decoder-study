"""One exact-PID kernel reaper. No Popen, aggregate usage or process-state guessing."""
from __future__ import annotations
import math,os,signal,sys,threading,time

def usage_dict(usage):
    values={k:getattr(usage,k) for k in ('ru_utime','ru_stime','ru_maxrss')}
    for value in values.values():
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
            raise ValueError('Invalid final kernel resource usage')
    if not isinstance(values['ru_maxrss'],int):raise ValueError('Nonintegral peak RSS')
    total=float(values['ru_utime']+values['ru_stime'])
    if not math.isfinite(total):raise ValueError('Nonfinite final total CPU')
    return dict(user_cpu=float(values['ru_utime']),system_cpu=float(values['ru_stime']),
        total_cpu=total,native_peak_rss=values['ru_maxrss'],
        native_RSS_unit='bytes' if sys.platform=='darwin' else 'KiB',
        peak_rss_bytes=values['ru_maxrss']*(1 if sys.platform=='darwin' else 1024))

class KernelChild:
    def __init__(self,wait_fn=None,kill_fn=None):
        if signal.getsignal(signal.SIGCHLD)!=signal.SIG_DFL:
            raise RuntimeError('SIGCHLD must have its default disposition')
        self.pid=None;self.thread=threading.get_ident();self.events=[];self.signals=[]
        self.wait_fn=wait_fn or os.wait4;self.kill_fn=kill_fn or os.kill
        self.reaped=False;self.lost=False;self.final=None;self.errors=[]
    def bind(self,pid):
        if self.pid is not None or isinstance(pid,bool) or not isinstance(pid,int) or pid<=0:
            raise ValueError('Bind exactly one positive owned PID')
        self.pid=pid
    def check_thread(self):
        if threading.get_ident()!=self.thread:raise RuntimeError('Only the owner thread may reap or signal')
    def poll(self):
        self.check_thread()
        if self.reaped or self.lost:return self.final # Cached; no second OS reap.
        if self.pid is None:raise RuntimeError('Child not bound')
        event=dict(requested_pid=self.pid,flags=int(os.WNOHANG),started=time.monotonic())
        try:
            pid,status,usage=self.wait_fn(self.pid,os.WNOHANG)
            event['ended']=time.monotonic();event['returned_pid']=pid
            if isinstance(pid,bool) or not isinstance(pid,int) or pid<0:
                self.errors.append('invalid_returned_PID');self.lost=True
            elif pid==0:
                event['status_and_usage_ignored']=True
            elif pid!=self.pid:
                self.errors.append('foreign_PID_returned');self.lost=True
            elif not isinstance(status,int) or isinstance(status,bool) or not 0<=status<=65535:
                self.errors.append('invalid_wait_status');self.lost=True
            elif not (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                # Not final reaping. Retain ownership for cleanup; never fake completion.
                event['nonterminal_status']=status;self.errors.append('nonterminal_wait_status')
            else:
                self.reaped=True # Kernel consumed this PID even if its usage record is invalid.
                event['raw_status']=status
                try:
                    final_usage=usage_dict(usage)
                    self.final=dict(pid=pid,raw_status=status,returncode=os.waitstatus_to_exitcode(status),
                        reaped_at=event['ended'],usage=final_usage)
                    event['final']=self.final
                except (TypeError,ValueError,AttributeError) as exc:self.errors.append('invalid_final_usage: '+str(exc))
        except InterruptedError:
            event.update(ended=time.monotonic(),interrupted=True)
        except (ChildProcessError,OSError) as exc:
            event.update(ended=time.monotonic(),ownership_error=f'{type(exc).__name__}: {exc}')
            self.errors.append('owned_reaping_failed');self.lost=True # Never kill a possibly recycled PID.
        self.events.append(event)
        return self.final
    def send(self,signum,reasons):
        self.check_thread();self.poll()
        if self.reaped or self.lost:
            return dict(sent=False,reason='already_reaped_or_ownership_lost')
        record=dict(pid=self.pid,signum=int(signum),reasons=list(reasons),requested_at=time.monotonic())
        try:self.kill_fn(self.pid,signum);record['API_returned']=True
        except OSError as exc:record.update(API_returned=False,error=f'{type(exc).__name__}: {exc}')
        self.signals.append(record);return record
    def wait_until(self,deadline):
        while not self.reaped and not self.lost:
            self.poll()
            if self.reaped or self.lost or time.monotonic()>=deadline:break
            time.sleep(min(.005,max(0.,deadline-time.monotonic())))
        return self.final
    def stop(self,reasons,grace=.5):
        for signum in (signal.SIGTERM,signal.SIGKILL):
            self.poll()
            if self.reaped or self.lost:break
            sent=self.send(signum,reasons)
            if not sent.get('API_returned'):continue
            sent['wait_started']=time.monotonic();self.wait_until(sent['wait_started']+grace)
            sent['wait_ended']=time.monotonic();sent['wait_timed_out']=not self.reaped and not self.lost
            sent['returncode_after_wait']=self.final['returncode'] if self.final else None
        return self.final
