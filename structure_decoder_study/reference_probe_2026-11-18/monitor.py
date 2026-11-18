"""Bounded process monitor reused from the audited preceding study."""
import json,subprocess,time
def watch(command,wall_limit,rss_limit,logfile,echo=False):
    started=time.monotonic();peak=0;reason=None;offset=0;monitor_error=None
    with logfile.open("w") as output:
        proc=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            if time.monotonic()-started>wall_limit:reason="wall_limit"
            try:
                response=subprocess.run(["ps","-o","rss=","-p",str(proc.pid)],capture_output=True,text=True,timeout=2)
                if response.stdout.strip():
                    rss=int(response.stdout.strip())*1024;peak=max(peak,rss)
                    if rss>rss_limit:reason="rss_limit"
                elif response.returncode and proc.poll() is None:
                    monitor_error="ps returned no process RSS while child appeared active"
            except Exception as exc:
                monitor_error=f"{type(exc).__name__}: {exc}"
            if monitor_error:reason="monitor_failure"
            if reason:
                proc.terminate()
                try:proc.wait(timeout=2)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
                break
            if echo:
                with logfile.open() as log:
                    log.seek(offset);text=log.read();offset=log.tell()
                if text:print(text,end="",flush=True)
            time.sleep(0.02)
        code=proc.wait()
    if echo:
        with logfile.open() as log:log.seek(offset);text=log.read()
        if text:print(text,end="",flush=True)
    return dict(returncode=code,watchdog_reason=reason,monitor_error=monitor_error,peak_observed_child_rss_bytes=peak,wall_seconds=time.monotonic()-started)
