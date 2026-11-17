"""Selected mechanism replays, separate from uninstrumented stress timings."""
from pathlib import Path
import json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from stress import convert,make_decoder,seed,save_json,digest,DECODER_CONFIG
import stim
from ldpc import BpDecoder
from ldpc.lsd_decoder import LsdDecoder


def timed(function,*args):
    w=time.perf_counter_ns();c=time.process_time_ns()
    value=function(*args)
    return value,time.perf_counter_ns()-w,time.process_time_ns()-c


def main():
    summaries=json.loads((ROOT/"results/discovery_summaries.json").read_text())
    cases={r["name"]:r for r in json.loads((ROOT/"corpus.json").read_text())}
    selected=sorted([r for r in summaries if not r["censored"] and r["features"]["n_faults"]<=8000],
                    key=lambda r:(-r["padded_p95_underprediction_ratio"],r["name"]))[:6]
    output=ROOT/"results/mechanisms";output.mkdir(parents=True,exist_ok=True)
    save_json(output/"selection.json",dict(names=[r["name"] for r in selected],
               implementation_sha256=digest(Path(__file__).read_bytes()),post_hoc=True,
               population_estimator=False,elapsed_counter_units="not verified; do not interpret as time"))
    results=[]
    for summary in selected:
        name=summary["name"];case=cases[name]
        circuit=stim.Circuit.from_file(str(ROOT/"circuits"/f"{name}.stim"))
        h,l,priors,_=convert(circuit.detector_error_model())
        full=make_decoder(h,priors);instrumented=make_decoder(h,priors,stats=True)
        options={k:v for k,v in DECODER_CONFIG.items() if k not in ("lsd_order","lsd_method")}
        bp=BpDecoder(h,error_channel=priors,**options)
        lsd=LsdDecoder(h,bits_per_step=1,lsd_method="LSD_0",lsd_order=0)
        sources=[];allshots=[]
        for session in range(3):
            path=ROOT/"results/discovery"/f"session_{session}"/f"{name}.npz"
            raw=np.load(path);meta=json.loads(path.with_suffix(".json").read_text())
            d,o=circuit.compile_detector_sampler(seed=meta["seed"]).sample(meta["planned_shots"],separate_observables=True)
            sources.append((raw,d.astype(np.uint8),o))
            allshots.extend((int(t),session,j) for j,t in enumerate(raw["wall_ns"]))
        selected_shots={(0,j) for j in range(min(4,len(sources[0][0]["wall_ns"])))}
        slow_refs={(session,j) for _,session,j in sorted(allshots,reverse=True)[:4]}
        selected_shots.update(slow_refs)
        warm=circuit.compile_detector_sampler(seed=seed("stress_mechanism_warm",name)).sample(16).astype(np.uint8)
        for s in warm:full.decode(s);bp.decode(s)
        for session,j in sorted(selected_shots):
            raw,d,o=sources[session];s=d[j]
            correction,full_wall,full_cpu=timed(full.decode,s)
            checkpoint=np.flatnonzero(raw["checkpoint_indices"]==j)
            assert len(checkpoint)==1 and np.array_equal(correction,raw["checkpoint_corrections"][checkpoint[0]])
            bp_correction,bp_wall,bp_cpu=timed(bp.decode,s)
            if bp.converge:
                combined=bp_correction;lsd_wall=lsd_cpu=0
            else:
                weights=np.ascontiguousarray(bp.log_prob_ratios,dtype=float)
                combined,lsd_wall,lsd_cpu=timed(lsd.decode,s,weights)
            assert np.array_equal(h@correction%2,s) and np.array_equal(h@combined%2,s)
            failure=bool(np.any(l@correction%2!=o[j]))
            assert failure==bool(raw["logical_z_failure"][j])
            instrumented.reset_cluster_stats()
            measured,stat_wall,stat_cpu=timed(instrumented.decode,s)
            stats=instrumented.statistics
            clusters=list(stats["individual_cluster_stats"].values())
            detail=[{k:v[k] for k in ("final_bit_count","undergone_growth_steps","nr_merges",
                                      "absorbed_by_cluster","nr_of_non_zero_check_matrix_entries")} for v in clusters]
            row=dict(name=name,session=session,index=j,syndrome_weight=int(s.sum()),
                     selected_slow=((session,j) in slow_refs),original_wall_ns=int(raw["wall_ns"][j]),
                     replay_wall_ns=full_wall,replay_cpu_ns=full_cpu,bp_replay_wall_ns=bp_wall,bp_replay_cpu_ns=bp_cpu,
                     lsd_replay_wall_ns=lsd_wall,lsd_replay_cpu_ns=lsd_cpu,bp_converged=bool(bp.converge),bp_iterations=bp.iter,
                     bp_stage_matches=(bp.converge==full.converge),
                     standalone_correction_matches=bool(np.array_equal(combined,correction)),
                     instrumented_correction_matches=bool(np.array_equal(measured,correction)),
                     instrumented_wall_ns=stat_wall,instrumented_cpu_ns=stat_cpu,
                     cluster_entries=len(clusters),max_final_cluster_bits=max([v["final_bit_count"] for v in clusters],default=0),
                     max_cluster_nonzeros=max([v["nr_of_non_zero_check_matrix_entries"] for v in clusters],default=0),
                     summed_growth_steps=sum(v["undergone_growth_steps"] for v in clusters),
                     native_elapsed_counter=stats["elapsed_time"],native_counter_units="unverified",cluster_details=detail)
            results.append(row)
            save_json(output/"replays.json",results)
        print(json.dumps(dict(diagnosed=name,shots=len(selected_shots))),flush=True)
    print(json.dumps(dict(replays=len(results),all_standalone_match=all(r["standalone_correction_matches"] for r in results),
                          all_instrumented_match=all(r["instrumented_correction_matches"] for r in results))),flush=True)


if __name__=="__main__":main()
