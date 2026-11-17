"""Prepare/freeze and execute the bounded natural-noise replication."""
from __future__ import annotations

import time
START_CPU, START_WALL = time.process_time(), time.monotonic()
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import sys
import sysconfig

ROOT = Path(__file__).resolve().parent
ENTRY = ROOT / "entry"
SOURCE = ROOT / "sources" / "Adaptive-qLDPC-8cc3201"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["MPLCONFIGDIR"] = str(ROOT / "runtime_cache")
sys.dont_write_bytecode = True
import numpy as np
import scipy.sparse as sp
import stim

CONFIGS = [dict(name="osd20", kind="osd", cap=20, method="OSD_0", order=0, force=False),
           dict(name="lsd30", kind="lsd", cap=30, method="LSD_0", order=0, force=False),
           dict(name="lsd100", kind="lsd", cap=100, method="LSD_0", order=0, force=False)]
FORCED = [dict(name="forced_lsd0", kind="lsd", cap=30, method="LSD_0", order=0, force=True),
          dict(name="forced_lsd_cs2", kind="lsd", cap=30, method="LSD_CS", order=2, force=True)]
SEEDS = [2026111731, 2026111732]


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_inputs():
    return (sp.load_npz(ENTRY / "source_H.npz").tocsr(),
            sp.load_npz(ENTRY / "source_L.npz").tocsr(),
            np.load(ENTRY / "source_priors.npy"))


def prepare():
    assert not (ROOT / "frozen.json").exists(), "Preserve the frozen setup"
    gate = read(ENTRY / "result.json")
    assert gate["status"] == "pass" and all(gate["checks"].values())
    manifest = read(ROOT / "source_manifest.json")
    for name, expected in manifest["files"].items():
        assert sha(SOURCE / name) == expected["sha256"]
    circuit = stim.Circuit.from_file(ENTRY / "bb144_r24_p0.007_z.stim")
    blocks = [circuit.compile_detector_sampler(seed=seed).sample(256, separate_observables=True) for seed in SEEDS]
    syndromes = np.concatenate([b[0] for b in blocks]).astype(np.uint8)
    actual = np.concatenate([b[1] for b in blocks]).astype(np.uint8)
    assert syndromes.shape == (512,1800) and actual.shape == (512,12)
    np.savez_compressed(ROOT / "shots.npz", syndrome=syndromes, actual=actual,
        seed=np.repeat(np.asarray(SEEDS,dtype=np.uint64),256), within_seed=np.tile(np.arange(256),2))
    rng = np.random.Generator(np.random.PCG64(2026111733))
    jobs = [dict(case_id=i, config_index=int(j)) for i in range(512) for j in rng.permutation(3)]
    save(ROOT / "jobs.json",jobs)
    paths = [ROOT / "ENTRY_PROTOCOL.md", ROOT / "EXECUTION_PROTOCOL.md", ROOT / "check_entry.py",
             ROOT / "source_manifest.json", Path(__file__), ROOT / "jobs.json", ROOT / "shots.npz"]
    paths += sorted(p for p in ENTRY.iterdir() if p.is_file())
    paths += [SOURCE / p for p in manifest["files"]]
    package = Path(sysconfig.get_paths()["purelib"]) / "ldpc"
    for module in ("bp_decoder", "bposd_decoder", "bplsd_decoder"):
        paths += sorted((package / module).glob("*.so"))
        paths += sorted((package / module).glob("*.pyx"))
    frozen = dict(files={str(p.resolve()):sha(p) for p in paths}, configs=CONFIGS, forced_configs=FORCED,
        seeds=SEEDS, shots_per_seed=256, job_order_seed=2026111733, main_calls=1536,
        limits=dict(invocations=1800,cpu_seconds=1200,wall_seconds=1800),
        versions={name:metadata.version(name) for name in ("numpy","scipy","stim","ldpc")},
        python=platform.python_version(),system=platform.platform(),
        setup_scope="Public source Z-check-only circuit; native primary fast path, not upstream full sweeps",
        frozen_before_decoder_calls=True)
    assert frozen["versions"]["ldpc"]=="2.4.1"
    save(ROOT / "frozen.json",frozen)
    print(json.dumps(dict(frozen=True,natural_circuit_shots=512,main_jobs=len(jobs),files_hashed=len(paths))))


class StopBudget(Exception):
    pass


def run():
    frozen = read(ROOT / "frozen.json")
    for name,digest in frozen["files"].items():
        assert sha(Path(name))==digest,name
    assert not (ROOT / "invocations.jsonl").exists(), "Preserve any previous run"
    from ldpc import BpOsdDecoder
    from ldpc.bplsd_decoder import BpLsdDecoder
    (ROOT / "calls").mkdir()
    h,l,p=load_inputs()
    shots=np.load(ROOT / "shots.npz")
    jobs=read(ROOT / "jobs.json")
    records=[]

    def event(value):
        with (ROOT / "invocations.jsonl").open("a") as file:
            file.write(json.dumps(value,sort_keys=True)+"\n")
            file.flush()

    def check_budget():
        lim=frozen["limits"]
        if len(records)>=lim["invocations"] or time.process_time()-START_CPU>=lim["cpu_seconds"] or time.monotonic()-START_WALL>=lim["wall_seconds"]:
            raise StopBudget("Declared between-call management limit reached")

    def construct(cfg,matrix=h,channel=p,stats=False,label=None):
        check_budget()
        c0,w0=time.process_time_ns(),time.perf_counter_ns()
        common=dict(error_channel=channel.tolist(),max_iter=cfg["cap"],bp_method="ms",
                    ms_scaling_factor=0.625,schedule="parallel",omp_thread_count=1,
                    random_schedule_seed=0,input_vector_type="syndrome")
        if cfg["kind"]=="osd":
            decoder=BpOsdDecoder(matrix,osd_method=cfg["method"],osd_order=cfg["order"],**common)
            assert decoder.osd_method.upper()==cfg["method"] and decoder.osd_order==cfg["order"]
        else:
            decoder=BpLsdDecoder(matrix,lsd_method=cfg["method"],lsd_order=cfg["order"],
                                 always_run_lsd=cfg["force"],bits_per_step=1,**common)
            decoder.set_do_stats(stats)
            assert decoder.lsd_method.upper()==cfg["method"] and decoder.lsd_order==cfg["order"]
        assert decoder.schedule=="parallel" and decoder.max_iter==cfg["cap"]
        assert abs(decoder.ms_scaling_factor-0.625)<1e-15 and decoder.omp_thread_count==1
        cost=dict(cpu_ns=time.process_time_ns()-c0,wall_ns=time.perf_counter_ns()-w0)
        event(dict(event="construction",label=label,config=cfg,**cost))
        return decoder,cost

    def invoke(phase,case_id,cfg,syndrome,actual,matrix=h,logicals=l,channel=p,decoder=None,stats=False,first_call=False):
        check_budget()
        index=len(records)
        event(dict(event="start",index=index,phase=phase,case_id=case_id,config=cfg,
                   run_cpu=time.process_time()-START_CPU,run_wall=time.monotonic()-START_WALL))
        fresh=decoder is None
        init=dict(cpu_ns=0,wall_ns=0)
        if fresh:
            decoder,init=construct(cfg,matrix,channel,stats,label=f"call_{index}")
        event(dict(event="decode_start",index=index))
        c0,w0=time.process_time_ns(),time.perf_counter_ns()
        correction=np.asarray(decoder.decode(syndrome),dtype=np.uint8).copy()
        decode_cpu,decode_wall=time.process_time_ns()-c0,time.perf_counter_ns()-w0
        assert correction.shape==(matrix.shape[1],) and np.isin(correction,[0,1]).all()
        bp=np.asarray(decoder.bp_decoding,dtype=np.uint8).copy()
        llrs=np.asarray(decoder.log_prob_ratios,dtype=np.float64).copy()
        native_readout=np.asarray(decoder.osd0_decoding,dtype=np.uint8).copy() if cfg["kind"]=="osd" else correction
        readout_equal=np.array_equal(correction,native_readout)
        predicted=np.asarray(logicals@correction).ravel()%2
        syndrome_prediction=np.asarray(matrix@correction).ravel()%2
        residual=int(np.count_nonzero(syndrome_prediction!=syndrome))
        logical_difference=int(np.count_nonzero(predicted!=actual))
        outcome="invalid_correction" if residual else "logical_failure" if logical_difference else "correct"
        full_stats=decoder.statistics if stats and cfg["kind"]=="lsd" else None
        nclusters=len(full_stats["individual_cluster_stats"]) if full_stats else 0
        row=dict(index=index,phase=phase,case_id=case_id,config=cfg,fresh_instance=fresh,first_call_in_block=first_call,
                 bp_converged=bool(decoder.converge),bp_iterations=int(decoder.iter),zero_syndrome=not bool(syndrome.any()),
                 syndrome_weight=int(syndrome.sum()),syndrome_residual=residual,logical_difference=logical_difference,
                 outcome=outcome,init_cpu_ns=init["cpu_ns"],init_wall_ns=init["wall_ns"],
                 decode_cpu_ns=decode_cpu,decode_wall_ns=decode_wall,source_readout_equal=bool(readout_equal),
                 statistics_enabled=stats,cluster_count=nclusters,postprocessing_observed=nclusters>0 if stats else None,
                 correction_sha256=hashlib.sha256(correction.tobytes()).hexdigest(),bp_sha256=hashlib.sha256(bp.tobytes()).hexdigest())
        np.savez_compressed(ROOT / "calls" / f"{index:04d}.npz",correction=correction,bp=bp,llrs=llrs,
                            syndrome=syndrome,actual=actual,predicted=predicted,source_readout=native_readout)
        save(ROOT / "calls" / f"{index:04d}.json",dict(row,statistics=full_stats))
        records.append(row)
        event(dict(event="complete",**row))
        assert readout_equal,"Source osd0 readout differs from native returned correction"
        return row

    status,message="running",""
    selected=[]
    try:
        # Eleven counted predeclared adapters, all disjoint from experiment shots.
        for cfg in CONFIGS:
            for cols in ([],[0]):
                e=np.zeros(h.shape[1],dtype=np.uint8);e[cols]=1
                row=invoke("adapter_bb",f"bb_{len(records)}",cfg,np.asarray(h@e).ravel()%2,np.asarray(l@e).ravel()%2)
                assert row["outcome"]=="correct","BB zero/singleton adapter failure"
        toy_h=sp.csr_matrix(np.array([[1,1,0],[0,1,1]],dtype=np.uint8))
        toy_l=sp.csr_matrix(np.array([[1,1,1]],dtype=np.uint8))
        toy_p=np.full(3,0.01)
        for cfg in [CONFIGS[0]]+FORCED:
            row=invoke("adapter_toy","toy",cfg,np.ones(2,dtype=np.uint8),np.ones(1,dtype=np.uint8),
                       matrix=toy_h,logicals=toy_l,channel=toy_p,stats=cfg["force"])
            output=np.load(ROOT / "calls" / f"{row['index']:04d}.npz")["correction"]
            candidates=[np.array([(i>>j)&1 for j in range(3)],dtype=np.uint8) for i in range(8)]
            valid=[v for v in candidates if np.array_equal(toy_h@v%2,np.ones(2,dtype=np.uint8))]
            weights=np.log((1-toy_p)/toy_p)
            assert abs(float(output@weights)-min(float(v@weights) for v in valid))<1e-12
            assert row["outcome"]=="correct" and row["bp_converged"]
            if cfg["force"]:
                assert row["postprocessing_observed"],"Forced path did not execute after BP convergence"
        for cfg in FORCED:
            row=invoke("adapter_bb_forced","bb_forced",cfg,np.asarray(h[:,0].toarray()).ravel(),np.asarray(l[:,0].toarray()).ravel(),stats=True)
            assert row["outcome"]=="correct" and row["postprocessing_observed"]
        save(ROOT / "adapter_result.json",dict(passed=True,decoder_calls=len(records),source_native_readout_verified=True,
                                                forced_after_bp_convergence_verified=True))
        print(json.dumps(dict(adapters_passed=True,counted_calls=len(records))),flush=True)
        baseline={}
        instances={}
        for j,job in enumerate(jobs):
            case,cfg=job["case_id"],CONFIGS[job["config_index"]]
            block=case//256
            key=(block,cfg["name"])
            if key not in instances:
                instances[key]=construct(cfg,label=f"block_{block}_{cfg['name']}")[0]
            row=invoke("main",case,cfg,shots["syndrome"][case],shots["actual"][case],decoder=instances[key],first_call=case%256==0)
            baseline[case,cfg["name"]]=row
            if (j+1)%192==0:
                print(json.dumps(dict(main_calls_completed=j+1,primary_failures_so_far=sum(r["config"]["name"]=="osd20" and r["outcome"]!="correct" for r in baseline.values()),
                                     cpu_seconds=time.process_time()-START_CPU)),flush=True)
        failed=[i for i in range(512) if baseline[i,"osd20"]["outcome"]!="correct"][:8]
        successes=[i for i in range(512) if baseline[i,"osd20"]["outcome"]=="correct"]
        used=set();pairs=[]
        for case in failed:
            available=[i for i in successes if i not in used]
            control=min(available,key=lambda i:(i//256!=case//256,abs(baseline[i,"osd20"]["syndrome_weight"]-baseline[case,"osd20"]["syndrome_weight"]),i)) if available else None
            pairs.append(dict(failure=case,control=control,same_seed_block=bool(control is not None and control//256==case//256),
                              syndrome_weight_difference=baseline[control,"osd20"]["syndrome_weight"]-baseline[case,"osd20"]["syndrome_weight"] if control is not None else None))
            selected.append(case)
            if control is not None:
                selected.append(control);used.add(control)
        save(ROOT / "selected_pairs.json",pairs)
        for case in selected:
            for cfg in CONFIGS:
                row=invoke("replay",case,cfg,shots["syndrome"][case],shots["actual"][case])
                old=baseline[case,cfg["name"]]
                assert all(row[k]==old[k] for k in ("outcome","correction_sha256","bp_sha256","bp_converged","bp_iterations")),"Fresh replay differs from persistent instance"
            for cfg in FORCED:
                row=invoke("forced",case,cfg,shots["syndrome"][case],shots["actual"][case],stats=True)
                assert row["zero_syndrome"] or row["postprocessing_observed"],"Forced post-processing not verified"
        status="completed"
        message="Fixed sample and selected-case checks complete" if failed else "No primary failure in fixed sample; stop without extending"
    except StopBudget as exc:
        status,message="resource_stopped",str(exc)
    except Exception as exc:
        status,message="error_stopped",f"{type(exc).__name__}: {exc}"
        raise
    finally:
        journal=[json.loads(line) for line in (ROOT / "invocations.jsonl").read_text().splitlines()]
        started=sum(r["event"]=="decode_start" for r in journal)
        main_rows=[r for r in records if r["phase"]=="main"]
        summary=dict(status=status,message=message,decoder_calls_started=started,decoder_calls_completed=len(records),
            incomplete_decode_calls=started-len(records),main_calls_completed=len(main_rows),selected_cases=selected,
            counts={cfg["name"]:{o:sum(r["config"]["name"]==cfg["name"] and r["outcome"]==o for r in main_rows)
                    for o in ("correct","logical_failure","invalid_correction")} for cfg in CONFIGS},
            cpu_seconds=time.process_time()-START_CPU,wall_seconds=time.monotonic()-START_WALL,
            frozen_sha256=sha(ROOT / "frozen.json"),natural_circuit_noise_shots=512,training_samples=0,
            scope="Published-source Z-check-only memory; paired controls; no predictor or compiler claim")
        save(ROOT / "run_result.json",summary)
        print(json.dumps(summary),flush=True)


if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in ("prepare","run"):
        raise SystemExit("Usage: experiment.py prepare|run")
    prepare() if sys.argv[1]=="prepare" else run()
