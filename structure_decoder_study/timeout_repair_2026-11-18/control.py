"""Bounded calibration and frozen synthetic confirmation; no research data."""
from __future__ import annotations
import hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
from result_guard import atomic_json
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def checked_classification(process,report):
    if process["watchdog_reason"] or process["returncode"]!=0:return "process_censored_or_failed"
    if not isinstance(report,dict):return "missing_report"
    if report.get("finalized") is not True or report.get("handler_restored") is not True:return "unfinalized_or_unrestored_report"
    return report.get("classification","invalid_report")

def run_child(name,scenario,n=200,limit=.15,folder="confirmation",wall=8.,inject=False):
    out=ROOT/folder/name;out.mkdir(parents=True)
    cfg=dict(scenario=scenario,n=n,time_limit=limit,seed=2026111801,output=str(out.resolve()))
    atomic_json(out/"config.json",cfg)
    started=time.monotonic();peak=0;reason=None;injection=None;monitor_error=None
    with (out/"stdout.log").open("w") as stream:
        proc=subprocess.Popen([sys.executable,str(ROOT/"worker.py"),str(out/"config.json")],stdout=stream,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            if time.monotonic()-started>wall:reason="wall_limit"
            try:
                result=subprocess.run(["ps","-o","rss=","-p",str(proc.pid)],capture_output=True,text=True,timeout=1)
                if result.stdout.strip():
                    rss=int(result.stdout.strip())*1024;peak=max(peak,rss)
                    if rss>1073741824:reason="rss_limit"
                elif result.returncode and proc.poll() is None:monitor_error="ps returned no active RSS"
            except Exception as exc:monitor_error=f"{type(exc).__name__}: {exc}"
            if monitor_error:reason="monitor_failure"
            marker="persist_ready.json" if scenario=="late_persistence" else "ready.json"
            if inject and injection is None and (out/marker).exists():
                ready=read(out/marker)
                if time.monotonic()-ready["at"]["monotonic"]>=.02:
                    injection=dict(pid=proc.pid,signum=int(signal.SIGXCPU),sent_at_monotonic=time.monotonic(),ready=ready)
                    try:proc.send_signal(signal.SIGXCPU);injection["sent"]=True
                    except ProcessLookupError:injection["sent"]=False
            if reason:
                proc.terminate()
                try:proc.wait(timeout=.5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
                break
            time.sleep(.01)
        code=proc.wait()
    process=dict(returncode=code,watchdog_reason=reason,monitor_error=monitor_error,peak_rss_bytes=peak,
        wall_seconds=time.monotonic()-started,controlled_injection=injection,expected_wall_limit=wall)
    report=read(out/"result.json") if (out/"result.json").exists() else None
    process["classification"]=checked_classification(process,report)
    atomic_json(out/"process.json",process)
    row=dict(name=name,scenario=scenario,folder=out.relative_to(ROOT).as_posix(),process=process,
        has_incumbent=report.get("has_incumbent") if report else None,solver_status=report.get("solver_status") if report else None)
    print(json.dumps(dict(name=name,returncode=code,classification=process["classification"],solver_status=row["solver_status"],has_incumbent=row["has_incumbent"])),flush=True)
    return row

def calibrate():
    assert not (ROOT/"calibration_result.json").exists(),"Preserve calibration"
    started=time.monotonic();rows=[]
    rows.append(run_child("no_incumbent","normal",200,0.,"calibration"))
    chosen=None
    for n,limit in [(200,.15),(300,.5),(400,1.)]:
        if time.monotonic()-started+10>35:break
        row=run_child(f"with_{n}","normal",n,limit,"calibration");rows.append(row)
        report_path=ROOT/row["folder"]/"result.json"
        report=read(report_path) if report_path.exists() else None
        if row["process"]["classification"]=="solver_limit_with_incumbent" and report and report["incumbent_valid"]:
            chosen=dict(n=n,time_limit=limit,seed=2026111801);break
    no=read(ROOT/rows[0]["folder"]/"result.json") if (ROOT/rows[0]["folder"]/"result.json").exists() else None
    passed=bool(no and rows[0]["process"]["classification"]=="solver_limit_no_incumbent" and chosen is not None and time.monotonic()-started<=35)
    atomic_json(ROOT/"calibration_result.json",dict(passed=passed,rows=rows,selected_with_incumbent=chosen,
        optimization_calls=len(rows),controller_wall_seconds=time.monotonic()-started,source_hashes={n:sha(ROOT/n) for n in ("PLAN.md","worker.py","result_guard.py","control.py")}))

def freeze():
    assert not (ROOT/"frozen.json").exists(),"Preserve freeze"
    c=read(ROOT/"calibration_result.json");assert c["passed"]
    for name,digest in c["source_hashes"].items():assert sha(ROOT/name)==digest,name
    paths=[ROOT/n for n in ("PLAN.md","worker.py","result_guard.py","control.py","audit.py","PREFLIGHT.md","calibration_result.json")]
    paths+=list((ROOT/"calibration").rglob("*"))
    paths=[p for p in paths if p.is_file()]
    old=ROOT.parent/"reference_probe_2026-11-18/manifest.json"
    paths.append(old)
    f=dict(files={str(p.resolve()):sha(p) for p in paths},selected_fixture=c["selected_with_incumbent"],
        confirmation_scenarios=["timeout_none","timeout_incumbent","legacy_injected","deferred_injected","optimal","soft_cpu","hard_cpu","wall_guard","late_persistence"],
        max_confirmation_optimizer_calls=5,real_research_calls=0,wall_seconds_each=8,rss_bytes=1073741824,
        calibration_controller_wall_cap=35,confirmation_controller_wall_cap=85)
    atomic_json(ROOT/"frozen.json",f);print(json.dumps(dict(frozen=True,files=len(f["files"]),sha256=sha(ROOT/"frozen.json"))))

def confirm():
    assert not (ROOT/"confirmation_result.json").exists(),"Preserve confirmation"
    f=read(ROOT/"frozen.json")
    for name,digest in f["files"].items():assert sha(Path(name))==digest,name
    # Abnormal exit or watchdog cause can never be masked by a result file.
    ok=dict(returncode=0,watchdog_reason=None)
    assert checked_classification(dict(ok,returncode=1),dict(classification="solver_completed"))=="process_censored_or_failed"
    assert checked_classification(dict(ok,watchdog_reason="wall_limit"),dict(classification="solver_completed"))=="process_censored_or_failed"
    assert checked_classification(ok,None)=="missing_report"
    t=time.monotonic();chosen=f["selected_fixture"];n=chosen["n"];limit=chosen["time_limit"]
    rows=[]
    specs=[("timeout_none","normal",200,0.,False,8.),("timeout_incumbent","normal",n,limit,False,8.),
        ("legacy_injected","legacy_signal",n,limit,True,8.),("deferred_injected","deferred_signal",n,limit,True,8.),
        ("optimal","normal",6,1.,False,8.),("soft_cpu","cpu_soft",0,0.,False,8.),
        ("hard_cpu","cpu_hard",0,0.,False,8.),("wall_guard","wall_kill",0,0.,False,.15),
        ("late_persistence","late_persistence",6,0.,True,8.)]
    for name,scenario,native_n,native_limit,inject,wall in specs:
        if time.monotonic()-t+10>85:break
        rows.append(run_child(name,scenario,native_n,native_limit,inject=inject,wall=wall))
        atomic_json(ROOT/"confirmation_progress.json",dict(rows=rows))
    atomic_json(ROOT/"confirmation_result.json",dict(rows=rows,controller_wall_seconds=time.monotonic()-t,
        confirmation_optimizer_calls=sum(r["scenario"] not in ("cpu_soft","cpu_hard","wall_kill","late_persistence") for r in rows),
        all_scenarios_attempted=len(rows)==len(specs),real_research_calls=0,frozen_sha256=sha(ROOT/"frozen.json")))
    files=list((ROOT/"confirmation").rglob("*"))+[ROOT/"confirmation_result.json"]
    atomic_json(ROOT/"output_manifest.json",dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in files if p.is_file()}))

if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("calibrate","freeze","confirm"):raise SystemExit("Usage: control.py calibrate|freeze|confirm")
    {"calibrate":calibrate,"freeze":freeze,"confirm":confirm}[sys.argv[1]]()
