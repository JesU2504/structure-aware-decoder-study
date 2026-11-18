"""Freeze and bound the offline diagnostic; preserves all old artifacts."""
from __future__ import annotations
import hashlib,importlib.metadata as metadata,json,os,platform,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
HEAD=ROOT.parent/"headroom_cached_order_2026-11-17"
OLD=ROOT.parent/"natural_noise_reproduction_2026-11-17"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,v):
    q=p.with_name(p.name+".tmp");q.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n");q.replace(p)

def prepare():
    assert not (ROOT/"frozen.json").exists(),"Preserve previous plan"
    for name,digest in read(HEAD/"manifest.json")["files"].items():assert sha(HEAD/name)==digest,name
    cases=read(HEAD/"selection.json");assert len(cases)==24
    assert [c["case_id"] for c in cases]==sorted(set(c["case_id"] for c in cases))
    paths=[ROOT/"PROTOCOL.md",ROOT/"diagnose.py",ROOT/"audit.py",Path(__file__),HEAD/"manifest.json",HEAD/"frozen.json",HEAD/"selection.json",HEAD/"result_audit.json",HEAD/"worker_result.json",HEAD/"audit_process_result.json",OLD/"manifest.json",OLD/"entry/H.npz",OLD/"entry/L.npz",OLD/"entry/priors.npy"]
    for name in ("task_specific_expert.md","task_specific_supervisor.md"):
        paths.append(ROOT.parent/"framework_search_2026-11-17"/name)
    for case in cases:
        cid=case["case_id"]
        paths += [Path(case["cached_npz"]),Path(case["cached_metadata"])]
        paths += [HEAD/sub/f"{cid:04d}.{suffix}" for sub in ("gates","search") for suffix in ("npz","json")]
    if (ROOT/"PREFLIGHT.md").exists():paths.append(ROOT/"PREFLIGHT.md")
    frozen=dict(files={str(p.resolve()):sha(p) for p in paths},cases=cases,
        versions={k:metadata.version(k) for k in ("numpy","scipy")},python=sys.version,platform=platform.platform(),
        limits=dict(child_cpu_seconds=600,wall_seconds=900,child_rss_bytes=1073741824),
        candidate_count_per_case=10447,logical_label_convention="absoluteLrowi_bit_i",score_atol=1e-8,score_rtol=1e-12,
        independent_audit_chunk=128,new_decoder_calls=0,new_physical_samples=0,new_search_candidates=0,new_fits=0)
    save(ROOT/"frozen.json",frozen)
    print(json.dumps(dict(frozen=True,files=len(frozen["files"]),cases=24,frozen_sha256=sha(ROOT/"frozen.json"))))

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

def classify(process,report):
    if process["watchdog_reason"] in ("wall_limit","rss_limit"):return "resource_censored"
    if process["watchdog_reason"]:return "infrastructure_stopped"
    if process["returncode"] in (-signal.SIGXCPU,-signal.SIGKILL):return "resource_or_signal_stopped"
    if process["returncode"]==1 and isinstance(report,dict) and report.get("status")=="resource_stopped":return "resource_censored"
    if process["returncode"]!=0:return "abnormal_exit"
    if not isinstance(report,dict):return "missing_report"
    if report.get("status")!="completed":return report.get("status","invalid_report")
    if report.get("cases_completed")!=24:return "incomplete_report"
    return "completed"

def run(stage):
    assert stage in ("analysis","audit")
    output=ROOT/(stage+"_process.json");assert not output.exists(),"Preserve previous stage"
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    if stage=="analysis":
        complete=dict(status="completed",cases_completed=24)
        for code,reason,report,expected in [(0,None,complete,"completed"),(1,None,complete,"abnormal_exit"),(-signal.SIGXCPU,None,complete,"resource_or_signal_stopped"),(-signal.SIGKILL,None,complete,"resource_or_signal_stopped"),(0,None,None,"missing_report"),(0,None,dict(status="completed",cases_completed=23),"incomplete_report"),(0,"rss_limit",complete,"resource_censored"),(0,"wall_limit",complete,"resource_censored"),(0,"monitor_failure",complete,"infrastructure_stopped"),(0,None,dict(status="validation_failed"),"validation_failed"),(1,None,dict(status="resource_stopped"),"resource_censored")]:
            assert classify(dict(returncode=code,watchdog_reason=reason),report)==expected
        probes={}
        probes["wall"]=watch([sys.executable,"-c","import time; time.sleep(.5)"],.08,1073741824,ROOT/"probe_wall.log")
        probes["rss"]=watch([sys.executable,"-c","import time; time.sleep(.5)"],2,1048576,ROOT/"probe_rss.log")
        probes["cpu"]=watch([sys.executable,"-c","import resource; resource.setrlimit(resource.RLIMIT_CPU,(1,1))\nwhile True:pass"],4,1073741824,ROOT/"probe_cpu.log")
        passed=probes["wall"]["watchdog_reason"]=="wall_limit" and probes["rss"]["watchdog_reason"]=="rss_limit" and probes["cpu"]["returncode"] in (-signal.SIGKILL,-signal.SIGXCPU) and probes["cpu"]["watchdog_reason"] is None
        save(ROOT/"watchdog_adapters.json",dict(passed=passed,probes=probes,exit_classifier_cases=11))
        if not passed:save(output,dict(passed=False,status="watchdog_adapter_stopped"));return
        (ROOT/"cases").mkdir()
    else:
        assert read(ROOT/"analysis_process.json")["passed"]
    script="diagnose.py" if stage=="analysis" else "audit.py"
    limits=frozen["limits"]
    process=watch([sys.executable,str(ROOT/script)],limits["wall_seconds"],limits["child_rss_bytes"],ROOT/(stage+".log"),echo=True)
    report=read(ROOT/(stage+"_result.json")) if (ROOT/(stage+"_result.json")).exists() else None
    process["status"]=classify(process,report);process["passed"]=process["status"]=="completed"
    if stage=="audit":process["passed"]=process["passed"] and report.get("passed") is True
    process["frozen_sha256"]=sha(ROOT/"frozen.json")
    save(output,process)
    if stage=="analysis" and process["passed"]:
        files=[ROOT/"analysis_result.json",ROOT/"analysis_process.json",ROOT/"algebra_adapters.json",ROOT/"watchdog_adapters.json",ROOT/"journal.jsonl"]+sorted((ROOT/"cases").iterdir())
        save(ROOT/"analysis_output_manifest.json",dict(files={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print(json.dumps(process),flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","analysis","audit"):raise SystemExit("Usage: control.py prepare|analysis|audit")
    if sys.argv[1]=="prepare":prepare()
    else:run(sys.argv[1])
