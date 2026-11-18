"""Pure fake wait/kill contracts; no child, ps, solver or quantum call."""
import ast,json,os,signal,sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from owner import KernelChild,usage_dict
from runner import parse,sha,validate_config
ROOT=Path(__file__).resolve().parent
def main():
    target=ROOT/'offline_checks.json';assert not target.exists()
    checks=[]
    def check(name,value):assert value,name;checks.append(name)
    usage=SimpleNamespace(ru_utime=.2,ru_stime=.03,ru_maxrss=1024)
    class Fake:
        def __init__(self,answers):self.answers=list(answers);self.calls=[];self.kills=[]
        def wait(self,pid,flags):
            self.calls.append((pid,flags));value=self.answers.pop(0)
            if isinstance(value,BaseException):raise value
            return value
        def kill(self,pid,signum):self.kills.append((pid,int(signum)))
    def owner(answers):
        fake=Fake(answers);obj=KernelChild(fake.wait,fake.kill);obj.bind(424242);return obj,fake
    o,f=owner([(0,object(),object()),(424242,0,usage)])
    check('PID0_ignores_status_and_usage',o.poll() is None and not o.reaped and not o.errors)
    check('owned_final_status_and_usage',o.poll()['returncode']==0 and o.reaped)
    n=len(f.calls);o.poll();o.send(signal.SIGTERM,[])
    check('cached_poll_and_no_signal_after_reaping',len(f.calls)==n and not f.kills)
    check('every_wait_is_exact_positive_PID',all(p==424242 and flags==os.WNOHANG for p,flags in f.calls))
    for name,answer in [('foreign_PID',(424243,0,usage)),('ECHILD',ChildProcessError('fake')),
        ('malformed_returned_PID',(True,0,usage))]:
        o,f=owner([answer]);o.poll();o.send(signal.SIGTERM,[])
        check(name+'_lost_no_stale_signal',o.lost and o.final is None and not f.kills)
    for name,bad in [('nan_CPU',SimpleNamespace(ru_utime=float('nan'),ru_stime=0.,ru_maxrss=1)),
        ('negative_RSS',SimpleNamespace(ru_utime=.1,ru_stime=.01,ru_maxrss=-1)),('missing_usage',object()),
        ('nonfinite_total',SimpleNamespace(ru_utime=1e308,ru_stime=1e308,ru_maxrss=1))]:
        o,f=owner([(424242,0,bad)]);o.poll();o.poll();o.send(signal.SIGKILL,[])
        check(name+'_reaped_before_usage_validation',o.reaped and o.final is None and o.errors and len(f.calls)==1 and not f.kills)
    o,f=owner([(424242,(signal.SIGSTOP<<8)|0x7f,usage),(424242,signal.SIGKILL,usage)])
    o.poll();check('nonterminal_status_not_final',not o.reaped and not o.lost and bool(o.errors))
    o.poll();check('owned_cleanup_can_obtain_later_final',o.reaped and o.final['returncode']==-9)
    o,f=owner([(424242,7<<8,usage)]);check('nonzero_exit_preserved',o.poll()['returncode']==7)
    o,f=owner([InterruptedError('fake'),(424242,0,usage)]);o.poll()
    check('interrupted_nonblocking_poll_keeps_ownership',not o.reaped and not o.lost and not o.errors)
    check('retry_after_interruption_obtains_final',o.poll()['returncode']==0)
    with patch.object(signal,'getsignal',return_value=signal.SIG_IGN):
        try:KernelChild()
        except RuntimeError:check('ignored_SIGCHLD_rejected_before_spawn',True)
        else:raise AssertionError('SIGCHLD ignored accepted')
    for pid in (0,-1,True):
        try:KernelChild().bind(pid)
        except ValueError:check('invalid_owned_PID_'+str(pid),True)
        else:raise AssertionError(pid)
    check('Darwin_RSS_units_explicit',usage_dict(usage)['peak_rss_bytes']==1024 if sys.platform=='darwin' else usage_dict(usage)['peak_rss_bytes']==1048576)
    check('explicit_exit_candidate_not_live',parse('424242 ?E 0 0:00.00',424242)['kind']=='candidate')
    check('live_zero_sample_remains_live_for_rejection',parse('424242 R 1 0:00.00',424242)['kind']=='live')
    for raw in ('424242 ?NOPE 0 0:00.00','424243 R 1 0:00.10','424242 R nan 0:00.10'):
        try:parse(raw,424242)
        except ValueError:check('malformed_interim_'+raw,True)
        else:raise AssertionError(raw)
    for key,value in [('cpu_limit',float('nan')),('wall_limit',float('inf')),('cpu_limit',True),('rss_limit',0)]:
        cfg=dict(cpu_limit=3.,wall_limit=4.,rss_limit=268435456,OS_CPU_request=[5,6]);cfg[key]=value
        try:validate_config(cfg)
        except ValueError:check('bad_config_'+key+'_'+str(value),True)
        else:raise AssertionError(cfg)
    tree=ast.parse((ROOT/'runner.py').read_text());calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
    check('owned_worker_uses_posix_spawn',any(isinstance(n.func,ast.Attribute) and n.func.attr=='posix_spawn' for n in calls))
    check('no_Popen_poll_wait_competitor',not any(isinstance(n.func,ast.Attribute) and n.func.attr in ('Popen','waitpid','wait','getrusage') for n in calls))
    report=dict(passed=True,count=len(checks),checks=checks,actual_workers=0,optimizer_calls=0,decoder_calls=0,
        source_hashes={p.name:sha(p) for p in ROOT.glob('*.py')})
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('checks','source_hashes')}))
if __name__=='__main__':main()
