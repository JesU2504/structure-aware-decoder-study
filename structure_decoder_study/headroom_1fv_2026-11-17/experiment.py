"""Frozen, label-free Python 1FV diagnostic with global baseline gate."""
from __future__ import annotations

import time
START_CPU, START_WALL = time.process_time(), time.monotonic()
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/"natural_noise_reproduction_2026-11-17"
SOURCE=OLD/"sources"/"Adaptive-qLDPC-8cc3201"
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[key]="1"
sys.dont_write_bytecode=True
ATOL,RTOL=1e-8,1e-12


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,value):
    temporary=path.with_name(path.name+".tmp")
    temporary.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
    temporary.replace(path)


def prepare():
    import numpy as np
    assert not (ROOT/"frozen.json").exists(),"Preserve a previous frozen plan"
    previous=read(OLD/"manifest.json")
    for name,digest in previous["files"].items():
        assert sha(OLD/name)==digest,name
    events=[json.loads(line) for line in (OLD/"invocations.jsonl").read_text().splitlines()]
    primary=[r for r in events if r["event"]=="complete" and r["phase"]=="main" and r["config"]["name"]=="osd20"]
    assert len(primary)==512
    failures=sorted(r["case_id"] for r in primary if r["outcome"]=="logical_failure")
    assert len(failures)==12
    controls=[]
    for block in range(2):
        controls.extend(sorted(r["case_id"] for r in primary if r["case_id"]//256==block and r["outcome"]=="correct" and not r["bp_converged"])[:6])
    assert len(set(controls))==12 and not set(controls)&set(failures)
    selected=[]
    for case_id in sorted(failures+controls):
        row=next(r for r in primary if r["case_id"]==case_id)
        assert not row["bp_converged"] and row["syndrome_residual"]==0
        path=OLD/"calls"/f"{row['index']:04d}.npz"
        data=np.load(path)
        assert data["llrs"].dtype==np.float64 and data["llrs"].shape==(12240,) and np.isfinite(data["llrs"]).all()
        assert hashlib.sha256(data["correction"].tobytes()).hexdigest()==row["correction_sha256"]
        selected.append(dict(case_id=case_id,role="failure" if case_id in failures else "success_control",
            cached_call=row["index"],cached_npz=str(path.resolve()),cached_metadata=str((OLD/"calls"/f"{row['index']:04d}.json").resolve())))
    save(ROOT/"selection.json",selected)
    paths=[ROOT/"PROTOCOL.md",ROOT/"RISK_REVIEW.md",Path(__file__),ROOT/"selection.json",OLD/"manifest.json",
           OLD/"frozen.json",OLD/"result_audit.json",OLD/"shots.npz",OLD/"source_manifest.json",
           OLD/"entry/H.npz",OLD/"entry/L.npz",OLD/"entry/priors.npy",OLD/"entry/result.json",
           SOURCE/"failure_prediction/__init__.py",SOURCE/"failure_prediction/osd_internals.py",SOURCE/"failure_prediction/adaptive_v1.py"]
    paths += [Path(row[key]) for row in selected for key in ("cached_npz","cached_metadata")]
    frozen=dict(files={str(p.resolve()):sha(p) for p in paths},cases=selected,
        versions={name:metadata.version(name) for name in ("numpy","scipy","ldpc","stim")},
        rank=1794,n_columns=12240,free_candidates=10446,score_atol=ATOL,score_rtol=RTOL,chunk=256,
        limits=dict(child_cpu_seconds=600,wall_seconds=900,child_rss_bytes=1073741824),
        target="Pinned Python stable-order full 1FV branch, not hidden native OSD-CS pivots",
        new_shots=0,new_native_decoder_calls=0,source_commit=previous["source_commit"])
    save(ROOT/"frozen.json",frozen)
    print(json.dumps(dict(frozen=True,failures=failures,controls=controls,files_hashed=len(paths))))


class GateMismatch(Exception):
    pass


class ValidationFailure(Exception):
    pass


class BudgetStop(Exception):
    pass


def peak_rss_bytes():
    raw=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(raw if sys.platform=="darwin" else raw*1024)


def worker():
    import numpy as np
    import scipy.sparse as sp
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():
        if sha(Path(name))!=digest: raise ValidationFailure(f"Input changed: {name}")
    sys.path.insert(0,str(SOURCE))
    from failure_prediction import osd_internals as oi
    from failure_prediction import adaptive_v1 as av
    limits=frozen["limits"]
    resource.setrlimit(resource.RLIMIT_CPU,(limits["child_cpu_seconds"],limits["child_cpu_seconds"]+5))
    def cpu_stop(_s,_f): raise BudgetStop("Child CPU limit")
    signal.signal(signal.SIGXCPU,cpu_stop)
    def check_budget():
        if time.process_time()-START_CPU>=limits["child_cpu_seconds"] or time.monotonic()-START_WALL>=limits["wall_seconds"] or peak_rss_bytes()>limits["child_rss_bytes"]:
            raise BudgetStop("Worker CPU, wall or peak RSS limit")
    def event(value):
        with (ROOT/"journal.jsonl").open("a") as f:
            f.write(json.dumps(dict(value,cpu=time.process_time()-START_CPU,wall=time.monotonic()-START_WALL,peak_rss_bytes=peak_rss_bytes()),sort_keys=True)+"\n")
            f.flush()
    def rank_gf2(matrix):
        a=sp.csr_matrix(matrix);pivots={}
        for i in range(a.shape[0]):
            w=sum(1<<int(j) for j,v in zip(a.indices[a.indptr[i]:a.indptr[i+1]],a.data[a.indptr[i]:a.indptr[i+1]]) if int(v)%2)
            while w:
                j=w.bit_length()-1
                if j in pivots:w^=pivots[j]
                else:pivots[j]=w;break
        return len(pivots)
    def require(value,message):
        if not value:raise ValidationFailure(message)
    def adapters():
        # Noncanonical COO duplicates must cancel, including across word boundaries.
        toy=sp.coo_matrix((np.ones(8,dtype=np.uint8),([0,0,0,1,1,2,2,2],[0,0,63,64,65,0,130,130])),shape=(3,131))
        packed=oi.pack_matrix(toy,131,1)
        expected=toy.toarray()%2
        require(np.array_equal(oi.unpack_columns(packed,131),expected),"Packed XOR/word-boundary adapter")
        hm=np.array([[1,1,0,1,1],[0,1,1,0,0],[1,0,1,1,1]],dtype=np.uint8)
        llr=np.array([-3.,-2.,1.,0.1,0.2])
        for name,prob,syndrome in (("positive_tie",np.array([.01,.03,.02,.1,.1]),hm[:,0]),
                                  ("zero_tie",np.full(5,.1),hm[:,0]),
                                  ("zero_syndrome",np.full(5,.1),np.zeros(3,dtype=np.uint8))):
            ph=oi.pack_matrix(sp.csr_matrix(hm),5,1)
            info=oi.osd0_information_set(ph,syndrome,llr,5,2)
            require(info is not None,"Toy reconstruction returned no information set")
            weight=np.log(1/prob)
            delta,free,rf=av.score_one_free_prefix(info,weight,5,5)
            out=av.pick_one_free(info,delta,free,rf,len(free))
            valid=[]
            for bits in range(32):
                v=np.array([(bits>>j)&1 for j in range(5)],dtype=np.uint8)
                if np.array_equal(hm@v%2,syndrome) and int(v[free].sum())<=1:valid.append(v)
            require(len(valid)==len(free)+1,"Toy candidate coverage")
            scores=np.array([float(weight@v) for v in valid])
            require(np.array_equal(hm@out%2,syndrome),"Toy candidate syndrome")
            require(abs(float(weight@out)-float(scores.min()))<1e-10,"Toy direct optimum")
            if name=="positive_tie":require(np.flatnonzero(out).tolist()==[3],"Positive tie first-argmax rule")
            else:require(np.array_equal(out,info["solution"]),"Zero-improvement/no-change rule")
        check_budget()
        save(ROOT/"algebra_adapters.json",dict(passed=True,packed_xor_word_boundaries=True,dependent_row_toys=3,new_decoder_calls=0))

    status,message="running",""
    gate_rows=[];search_rows=[]
    try:
        adapters()
        h=sp.load_npz(OLD/"entry/H.npz").tocsr()
        priors=np.load(OLD/"entry/priors.npy")
        require(h.shape==(1800,12240) and np.isin(h.data,[0,1]).all(),"Actual H dimensions/binary")
        require(np.isfinite(priors).all() and np.all((priors>0)&(priors<1)),"Priors outside score domain")
        require(rank_gf2(h)==1794,"Independent actual rank")
        weight=np.log(1/priors)
        packed=oi.pack_matrix(h,12240,1)
        packed_digest=hashlib.sha256(packed.tobytes()).hexdigest()
        require(np.array_equal(oi.unpack_columns(packed,12240),h.toarray()),"Actual packed matrix mismatch")
        # GLOBAL GATE: no real-case score invocation before all cases pass.
        for case in frozen["cases"]:
            check_budget();cid=case["case_id"]
            event(dict(event="gate_start",case_id=cid))
            data=np.load(case["cached_npz"])
            llr=data["llrs"].copy();syndrome=data["syndrome"].copy();reference=data["correction"].copy()
            require(llr.dtype==np.float64 and np.isfinite(llr).all(),"Cached LLR integrity")
            require(np.array_equal(h@reference%2,syndrome),"Cached native e0 invalid")
            c0,w0=time.process_time_ns(),time.perf_counter_ns()
            info=oi.osd0_information_set(packed,syndrome,llr,12240,1794)
            elapsed=dict(reconstruction_cpu_ns=time.process_time_ns()-c0,reconstruction_wall_ns=time.perf_counter_ns()-w0)
            require(info is not None,"Information-set reconstruction failed")
            order,pivot,e0=info["order"],info["pivot_cols"],info["solution"]
            require(np.array_equal(np.sort(order),np.arange(12240)),"Ordering not permutation")
            require(len(pivot)==1794 and len(set(pivot.tolist()))==1794,"Pivot coverage")
            free=oi.free_columns(info,12240)
            require(len(free)==10446 and len(set(free.tolist()))==10446 and not set(free.tolist())&set(pivot.tolist()),"Free/pivot coverage")
            require(not e0[free].any() and np.isin(e0,[0,1]).all(),"Baseline not pivot-only binary")
            require(rank_gf2(h[:,pivot])==1794,"Actual pivot columns not independent")
            require(np.array_equal(oi.extract_columns(info["reduced"],pivot),np.eye(1794,dtype=np.uint8)),"Reduced pivots not identity")
            require(np.array_equal(h@e0%2,syndrome),"Baseline fails one of all1800 constraints")
            require(hashlib.sha256(packed.tobytes()).hexdigest()==packed_digest,"Source mutated packed input")
            _,inverse,counts=np.unique(llr,return_inverse=True,return_counts=True)
            is_pivot=np.zeros(12240,dtype=bool);is_pivot[pivot]=True
            pivot_group_counts=np.bincount(inverse[is_pivot],minlength=len(counts))
            boundary_ties=int(np.count_nonzero((pivot_group_counts>0)&(pivot_group_counts<counts)))
            equality=np.array_equal(e0,reference)
            row=dict(case_id=cid,baseline_equal=bool(equality),baseline_difference=int(np.count_nonzero(e0!=reference)),
                tie_fraction=oi.tie_fraction(llr),pivot_free_tie_groups=int(boundary_ties),**elapsed)
            np.savez_compressed(ROOT/"gates"/f"{cid:04d}.npz",**info)
            save(ROOT/"gates"/f"{cid:04d}.json",row)
            gate_rows.append(row);event(dict(event="gate_complete",**row))
            print(json.dumps(dict(gates_completed=len(gate_rows),case_id=cid,baseline_equal=bool(equality))),flush=True)
            if not equality:raise GateMismatch(f"Case {cid}: reconstructed e0 differs in {row['baseline_difference']} bits")
            check_budget()
        save(ROOT/"global_gate.json",dict(passed=True,cases=len(gate_rows),no_real_search_before_all_gates=True))
        event(dict(event="all_gates_passed",cases=len(gate_rows)))

        for case in frozen["cases"]:
            check_budget();cid=case["case_id"]
            event(dict(event="search_start",case_id=cid))
            stored=np.load(ROOT/"gates"/f"{cid:04d}.npz")
            info={key:stored[key].copy() for key in stored.files}
            e0,pivot=info["solution"],info["pivot_cols"]
            c0,w0=time.process_time_ns(),time.perf_counter_ns()
            delta,free,rf=av.score_one_free_prefix(info,weight,12240,12240)
            full=av.pick_one_free(info,delta,free,rf,len(free))
            score_cost=dict(full_source_cpu_ns=time.process_time_ns()-c0,full_source_wall_ns=time.perf_counter_ns()-w0)
            c0,w0=time.process_time_ns(),time.perf_counter_ns()
            corrections={str(len(free)):full,**{str(k):av.pick_one_free(info,delta,free,rf,k) for k in (500,1000)}}
            secondary_cost=dict(secondary_prefix_pick_cpu_ns=time.process_time_ns()-c0,secondary_prefix_pick_wall_ns=time.perf_counter_ns()-w0)
            require(len(free)==10446 and rf.shape==(1794,10446) and np.isfinite(delta).all() and np.isin(rf,[0,1]).all(),"Full source candidate arrays invalid")
            c0,w0=time.process_time_ns(),time.perf_counter_ns()
            baseline_score=float(weight@e0)
            hp=h[:,pivot].tocsr();direct_scores=np.empty(len(free));max_delta_error=0.
            for start in range(0,len(free),256):
                check_budget();end=min(start+256,len(free));block=rf[:,start:end]
                require(np.array_equal(hp@block%2,h[:,free[start:end]].toarray()),"Candidate violates full dependent-row parity certificate")
                flipped=np.bitwise_xor(e0[pivot,None],block)
                direct=weight[pivot]@flipped.astype(np.float64)+weight[free[start:end]]
                direct_scores[start:end]=direct
                independent_delta=baseline_score-direct
                max_delta_error=max(max_delta_error,float(np.max(np.abs(independent_delta-delta[start:end]))))
                require(np.allclose(delta[start:end],independent_delta,atol=ATOL,rtol=RTOL),"Source delta disagrees with direct score")
            outputs={}
            for key,out in corrections.items():
                k=int(key);head=delta[:min(k,len(delta))];best=int(np.argmax(head))
                chosen=int(free[best]) if head[best]>0 else None
                require(np.array_equal(h@out%2,h@e0%2),"Selected candidate syndrome invalid")
                selected_score=float(weight@out)
                minimum=min(baseline_score,float(direct_scores[:min(k,len(free))].min()))
                require(np.isclose(selected_score,minimum,atol=ATOL,rtol=RTOL),"Selected candidate not direct-score minimum within tolerance")
                outputs[key]=dict(chosen_free_column=chosen,source_delta=float(head[best]) if chosen is not None else 0.,score=selected_score)
            best=float(delta.max());sorted_delta=np.sort(delta)
            tol=ATOL+RTOL*max(abs(best),abs(baseline_score))
            validation_cost=dict(validation_cpu_ns=time.process_time_ns()-c0,validation_wall_ns=time.perf_counter_ns()-w0)
            row=dict(case_id=cid,free_candidates=len(free),baseline_score=baseline_score,outputs=outputs,
                max_delta_absolute_error=max_delta_error,best_source_delta=best,second_best_margin=float(sorted_delta[-1]-sorted_delta[-2]),
                candidates_near_best=int(np.count_nonzero(np.abs(delta-best)<=tol)),near_zero_best=abs(best)<=tol,
                **score_cost,**secondary_cost,**validation_cost)
            np.savez_compressed(ROOT/"search"/f"{cid:04d}.npz",delta=delta,free=free,rf=rf,direct_scores=direct_scores,
                baseline=e0,correction_500=corrections["500"],correction_1000=corrections["1000"],correction_full=corrections[str(len(free))])
            save(ROOT/"search"/f"{cid:04d}.json",row)
            search_rows.append(row);event(dict(event="search_complete",case_id=cid))
            print(json.dumps(dict(searches_completed=len(search_rows),case_id=cid)),flush=True)
            check_budget()
        status,message="completed","All global gates and full-search cases completed; outputs remain unscored by logical truth in worker"
    except GateMismatch as exc:
        status,message="baseline_mismatch",str(exc)
    except BudgetStop as exc:
        status,message="resource_stopped",str(exc)
    except Exception as exc:
        status,message="validation_or_infrastructure_stopped",f"{type(exc).__name__}: {exc}"
    finally:
        result=dict(status=status,message=message,gates_completed=len(gate_rows),searches_completed=len(search_rows),
            all_gate_rows=gate_rows,all_search_rows=search_rows,child_cpu_seconds=time.process_time()-START_CPU,
            child_wall_seconds=time.monotonic()-START_WALL,peak_child_rss_bytes=peak_rss_bytes(),
            new_native_decoder_calls=0,new_physical_shots=0,actual_labels_loaded_by_worker=False,
            frozen_sha256=sha(ROOT/"frozen.json"))
        save(ROOT/"worker_result.json",result)
        print(json.dumps({k:v for k,v in result.items() if k not in ("all_gate_rows","all_search_rows")}),flush=True)


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


def classify_worker_result(process,report):
    if process["watchdog_reason"] in ("wall_limit","rss_limit"):
        return "resource_censored"
    if process["watchdog_reason"]:
        return "infrastructure_stopped"
    if process["returncode"]!=0:
        return "worker_exit_stopped"
    if not isinstance(report,dict) or not isinstance(report.get("status"),str):
        return "missing_or_invalid_worker_report"
    if report["status"]=="completed" and (report.get("gates_completed")!=24 or report.get("searches_completed")!=24):
        return "incomplete_worker_report"
    return report["status"]


def run():
    assert not (ROOT/"controller_result.json").exists(),"Preserve previous attempt"
    frozen=read(ROOT/"frozen.json")
    for name,digest in frozen["files"].items():assert sha(Path(name))==digest,name
    (ROOT/"gates").mkdir();(ROOT/"search").mkdir()
    complete=dict(status="completed",gates_completed=24,searches_completed=24)
    classifier_cases=[(0,None,complete,"completed"),(1,None,complete,"worker_exit_stopped"),
        (-signal.SIGXCPU,None,complete,"worker_exit_stopped"),(-signal.SIGKILL,None,complete,"worker_exit_stopped"),
        (0,None,None,"missing_or_invalid_worker_report"),(0,None,dict(status="completed",gates_completed=24,searches_completed=23),"incomplete_worker_report"),
        (0,"rss_limit",complete,"resource_censored"),(0,"wall_limit",complete,"resource_censored"),
        (0,"monitor_failure",complete,"infrastructure_stopped"),(0,None,dict(status="baseline_mismatch"),"baseline_mismatch")]
    for code,reason,report,expected in classifier_cases:
        assert classify_worker_result(dict(returncode=code,watchdog_reason=reason),report)==expected
    save(ROOT/"exit_classifier_adapters.json",dict(passed=True,cases=len(classifier_cases),abnormal_exit_cannot_be_completed=True))
    # Watchdog probes use tiny limits; they do not run decoding or real-case algebra.
    probes={}
    probes["wall"]=watch([sys.executable,"-c","import time; time.sleep(0.5)"],.08,1073741824,ROOT/"probe_wall.log")
    probes["rss"]=watch([sys.executable,"-c","import time; time.sleep(0.5)"],2,1048576,ROOT/"probe_rss.log")
    probes["cpu"]=watch([sys.executable,"-c","import resource; resource.setrlimit(resource.RLIMIT_CPU,(1,1))\nwhile True: pass"],4,1073741824,ROOT/"probe_cpu.log")
    passed=(probes["wall"]["watchdog_reason"]=="wall_limit" and probes["rss"]["watchdog_reason"]=="rss_limit" and probes["cpu"]["returncode"] in (-signal.SIGKILL,-signal.SIGXCPU) and probes["cpu"]["watchdog_reason"] is None)
    save(ROOT/"watchdog_adapters.json",dict(passed=passed,probes=probes,rss_scope="child process; ps RSS KiB converted to bytes"))
    if not passed:
        save(ROOT/"controller_result.json",dict(status="watchdog_adapter_stopped",new_native_decoder_calls=0,new_physical_shots=0));return
    print(json.dumps(dict(watchdog_adapters_passed=True)),flush=True)
    limits=frozen["limits"]
    result=watch([sys.executable,str(Path(__file__).resolve()),"worker"],limits["wall_seconds"],limits["child_rss_bytes"],ROOT/"worker.log",echo=True)
    report=None
    if (ROOT/"worker_result.json").exists():
        try:report=read(ROOT/"worker_result.json")
        except (OSError,ValueError) as exc:result["worker_report_read_error"]=str(exc)
    result["status"]=classify_worker_result(result,report)
    result["controller_cpu_seconds"]=time.process_time()-START_CPU
    result["frozen_sha256"]=sha(ROOT/"frozen.json")
    save(ROOT/"controller_result.json",result)
    print(json.dumps(result),flush=True)


if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","run","worker"):
        raise SystemExit("Usage: experiment.py prepare|run|worker")
    {"prepare":prepare,"run":run,"worker":worker}[sys.argv[1]]()
