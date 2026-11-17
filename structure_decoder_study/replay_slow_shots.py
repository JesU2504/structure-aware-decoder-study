"""Post hoc CPU/wall replay diagnostic; selected extremes are not population data.

Select the ten largest individual primary wall times, plus a median-latency
syndrome from each selected shot's case/session. Replay each three times in a
shuffled serial order, with warmed, fixed-configuration decoders. Record both
process CPU and wall time and verify syndrome/failure reproduction. This can
diagnose whether extreme shots involve decoder CPU work; it does not estimate
tail probabilities or prove a runtime distribution. Primary data is immutable.
"""
from pathlib import Path
import json,time
import numpy as np
import stim
from study import ROOT,make_decoder,convert,seed,save_json,digest


def main():
    out=ROOT/"results"/"slow_replay"
    out.mkdir(parents=True,exist_ok=True)
    config=dict(implementation_sha256=digest(Path(__file__).read_bytes()),
                primary_config_sha256=digest((ROOT/"frozen_config.json").read_bytes()),
                post_hoc=True,selection="ten globally largest primary shot wall times and matched medians",
                repeats=3,cpu_clock="process_time_ns",wall_clock="perf_counter_ns")
    save_json(out/"config.json",config)
    candidates=[]
    for path in sorted((ROOT/"results").glob("session_*/*.npz")):
        a=np.load(path)
        for j in np.argsort(a["latency_ns"])[-10:]:
            candidates.append((int(a["latency_ns"][j]),str(path.relative_to(ROOT)),int(j)))
    selected=sorted(candidates,reverse=True)[:10]
    tasks=[];decoder_cache={};sample_cache={}
    for original_ns,relative,j in selected:
        path=ROOT/relative
        source=np.load(path)
        summary=json.loads(path.with_suffix(".json").read_text())
        name=summary["name"]
        if name not in decoder_cache:
            c=stim.Circuit((ROOT/"circuits"/f"{name}.stim").read_text())
            h,l,p,_=convert(c.detector_error_model())
            d=make_decoder(h,p)
            warm=c.compile_detector_sampler(seed=seed("slow_replay_warm",name)).sample(32).astype(np.uint8)
            for syndrome in warm:d.decode(syndrome)
            decoder_cache[name]=(c,h,l,d)
        c,h,l,d=decoder_cache[name]
        if relative not in sample_cache:
            det,obs=c.compile_detector_sampler(seed=summary["seed"]).sample(summary["shots"],separate_observables=True)
            sample_cache[relative]=(det.astype(np.uint8),obs)
        for kind,idx in (("extreme",j),("matched_median",int(np.argsort(source["latency_ns"])[len(source["latency_ns"])//2]))):
            tasks.append(dict(name=name,kind=kind,source=relative,index=idx,
                              original_wall_ns=int(source["latency_ns"][idx]),
                              original_failure=bool(source["logical_z_failure"][idx]),
                              original_iterations=int(source["bp_iterations"][idx]),
                              original_bp_converged=bool(source["bp_converged"][idx])))
    save_json(out/"selected_shots.json",tasks)
    observations=[]
    for repeat in range(3):
        order=np.arange(len(tasks))
        np.random.default_rng(seed("slow_replay_order",repeat)).shuffle(order)
        for task_index in order:
            task=tasks[task_index]
            c,h,l,d=decoder_cache[task["name"]]
            det,obs=sample_cache[task["source"]]
            syndrome=det[task["index"]]
            wall0=time.perf_counter_ns();cpu0=time.process_time_ns()
            correction=d.decode(syndrome)
            cpu_ns=time.process_time_ns()-cpu0;wall_ns=time.perf_counter_ns()-wall0
            assert np.array_equal(h@correction%2,syndrome)
            failure=bool(np.any(l@correction%2!=obs[task["index"]]))
            assert failure==task["original_failure"]
            observations.append(dict(task=int(task_index),repeat=repeat,wall_ns=wall_ns,cpu_ns=cpu_ns,
                                     bp_iterations=d.iter,bp_converged=bool(d.converge)))
    save_json(out/"observations.json",observations)
    summaries=[]
    for j,task in enumerate(tasks):
        rr=[r for r in observations if r["task"]==j]
        wall=float(np.median([r["wall_ns"] for r in rr]));cpu=float(np.median([r["cpu_ns"] for r in rr]))
        summaries.append(dict(**task,replay_wall_median_ns=wall,replay_cpu_median_ns=cpu,
                              cpu_wall_ratio=cpu/wall,replay_original_wall_ratio=wall/task["original_wall_ns"]))
    save_json(out/"summary.json",summaries)
    print(json.dumps(dict(shots=len(tasks),replay_decodes=len(observations),syndrome_and_failure_reproduction=True,
                         extremes=[{k:r[k] for k in ("name","original_wall_ns","replay_wall_median_ns","replay_cpu_median_ns","cpu_wall_ratio")}
                                   for r in summaries if r["kind"]=="extreme"])),flush=True)


if __name__=="__main__":main()
