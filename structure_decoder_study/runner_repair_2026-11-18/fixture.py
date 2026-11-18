"""Fixed stdlib-only runner controls. No numerical/decoder packages."""
import json,os,resource,signal,sys,time
from pathlib import Path
def save(path,data):
    temporary=path.with_name(path.name+'.tmp');temporary.write_text(json.dumps(data)+'\n');temporary.replace(path)
def main():
    config=json.loads(Path(sys.argv[1]).read_text());out=Path(config['output'])
    resource.setrlimit(resource.RLIMIT_CPU,(5,6))
    identity=dict(name=config['name'],nonce=config['nonce'],pid=os.getpid())
    def at():return dict(monotonic=time.monotonic(),cpu=time.process_time(),peak_RSS=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    save(out/'child_start.json',dict(identity=identity,at=at(),OS_CPU_request=[5,6],
        native_packages_present=any(n in sys.modules for n in ('numpy','scipy','ldpc','stim'))))
    mode=config['mode']
    if mode=='ignore_TERM':signal.signal(signal.SIGTERM,signal.SIG_IGN)
    if mode in ('cpu_work','final_CPU','barrier'):
        start=time.process_time();target=.12 if mode=='final_CPU' else .1
        while time.process_time()-start<target:unused=sum(i*i for i in range(1000))
    save(out/'ready.json',dict(identity=identity,at=at(),TERM_handler=int(signal.getsignal(signal.SIGTERM))))
    if mode=='rss':
        save(out/'allocation_start.json',dict(identity=identity,at=at(),requested_bytes=100663296))
        payload=bytearray(100663296)
        for index in range(0,len(payload),4096):payload[index]=7
        save(out/'allocated.json',dict(identity=identity,at=at(),committed_bytes=len(payload)))
        time.sleep(5)
    elif mode=='spin':
        while True:unused=sum(i*i for i in range(1000))
    elif mode in ('sleep','ignore_TERM'):time.sleep(5)
    elif mode=='barrier':assert sys.stdin.readline()=='EXIT\n'
    save(out/'child_final.json',dict(identity=identity,at=at()))
    raise SystemExit(7 if mode=='nonzero' else 0)
if __name__=='__main__':main()
