"""Main-thread signal recording for isolated solver workers; no budget changes."""
from __future__ import annotations
import json,os,resource,signal,sys,threading,time
from pathlib import Path

def atomic_json(path,value):
    path=Path(path);temporary=path.with_name(path.name+".tmp")
    temporary.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")
    temporary.replace(path)

def telemetry():
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return dict(monotonic=time.monotonic(),cpu_absolute=time.process_time(),
        ru_utime=usage.ru_utime,ru_stime=usage.ru_stime,
        peak_rss_bytes=int(usage.ru_maxrss if sys.platform=="darwin" else usage.ru_maxrss*1024),
        rlimit_cpu=list(resource.getrlimit(resource.RLIMIT_CPU)),sigxcpu_handler=str(signal.getsignal(signal.SIGXCPU)),pid=os.getpid())

class SignalLedger:
    """Use only in a fresh main-thread child; persist before leaving the context.

    This does not suppress hard limits or turn a signalled run into success.
    It only avoids throwing away a result at a delayed SIGXCPU handoff.
    """
    def __init__(self):self.events=[];self.phase="created";self.previous=None
    def __enter__(self):
        if threading.current_thread() is not threading.main_thread():raise RuntimeError("Main-thread use required")
        self.previous=signal.getsignal(signal.SIGXCPU)
        def record(signum,_frame):
            event=dict(signum=int(signum),phase=self.phase,origin="unknown")
            try:event["handled_at"]=telemetry()
            except Exception as exc:event["telemetry_error"]=f"{type(exc).__name__}: {exc}"
            self.events.append(event) # No file I/O or deliberate exception here.
        signal.signal(signal.SIGXCPU,record)
        return self
    def __exit__(self,kind,value,traceback):
        signal.signal(signal.SIGXCPU,self.previous)
        return False

def classify(solver_status,has_incumbent,signal_events):
    if signal_events:return "signal_observed_result_preserved"
    if solver_status==1:return "solver_limit_with_incumbent" if has_incumbent else "solver_limit_no_incumbent"
    if solver_status==0:return "solver_completed"
    return "solver_error_or_other_status"
