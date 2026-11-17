"""Qualify censored fields and summarize fixed-predictor boundary evidence."""
from pathlib import Path
import json,time
import numpy as np
ROOT=Path(__file__).resolve().parent

def main():
    summaries={}
    for phase in ("discovery","confirmation"):
        records=json.loads((ROOT/"results"/f"{phase}_summaries.json").read_text())
        for row in records:
            row["stopped_statistics_descriptive_only"]=row["censored"]
            if row["censored"]:row["logical_z_interval"]=None
        (ROOT/"results"/f"{phase}_summaries_reviewed.json").write_text(json.dumps(records,indent=2)+"\n")
        summaries[phase]=records
    within=[r for r in summaries["discovery"] if not r["outside_training_features"] and not r["censored"]]
    by_axis={}
    for axis in sorted({r["axis"] for r in summaries["discovery"]}):
        rows=[r for r in summaries["discovery"] if r["axis"]==axis]
        complete=[r for r in rows if not r["censored"]]
        by_axis[axis]=dict(cases=len(rows),censored=sum(r["censored"] for r in rows),
                          raw_p95_ratio_median=float(np.median([r["raw_p95_underprediction_ratio"] for r in complete])),
                          raw_p95_ratio_max=float(max(r["raw_p95_underprediction_ratio"] for r in complete)),
                          mean_ratio_median=float(np.median([r["raw_mean_underprediction_ratio"] for r in complete])),
                          confirmed_discovery_admission_errors=sum(r["confident_false_admission"] for r in rows))
    mechanism=json.loads((ROOT/"results/mechanisms/replays.json").read_text())
    slow=[r for r in mechanism if r["selected_slow"]]
    result=dict(discovery_shots=sum(r["shots"] for r in summaries["discovery"]),
                confirmation_shots=sum(r["shots"] for r in summaries["confirmation"]),
                within_range_scope="Initial discovery only; the later feature-box challenge has a counterexample",
                within_range_cases=len(within),within_range_max_raw_p95_ratio=max(r["raw_p95_underprediction_ratio"] for r in within),
                within_range_max_raw_p95_overprediction_factor=max(1/r["raw_p95_underprediction_ratio"] for r in within),
                within_range_max_raw_mean_ratio=max(r["raw_mean_underprediction_ratio"] for r in within),
                within_range_max_raw_mean_overprediction_factor=max(1/r["raw_mean_underprediction_ratio"] for r in within),
                within_range_confident_admission_errors=sum(r["confident_false_admission"] for r in within),
                by_axis=by_axis,mechanism_replays=len(mechanism),selected_slow_replays=len(slow),
                median_slow_standalone_lsd_fraction=float(np.median([r["lsd_replay_cpu_ns"]/(r["bp_replay_cpu_ns"]+r["lsd_replay_cpu_ns"]) for r in slow])),
                all_standalone_corrections_match=all(r["standalone_correction_matches"] for r in mechanism),
                all_instrumented_corrections_match=all(r["instrumented_correction_matches"] for r in mechanism),
                largest_recorded_final_cluster_bits=max(r["max_final_cluster_bits"] for r in mechanism))
    for phase in ("boundary", "feature_box"):
        summaries[phase]=json.loads((ROOT/"results"/f"{phase}_summaries.json").read_text())
    result["phase_counts"]={phase:dict(cases=len(rows),shots=sum(r["shots"] for r in rows),
                                      censored_cases=sum(r["censored"] for r in rows))
                            for phase,rows in summaries.items()}
    result["physical_shots_total"]=sum(v["shots"] for v in result["phase_counts"].values())
    result["unique_new_configurations"]=len({r["name"] for rows in summaries.values() for r in rows})
    result["feature_box_confident_false_admissions"]=[r["name"] for r in summaries["feature_box"]
                                                      if r["confident_false_admission"]]
    # Diagnostic only: same pair of CPU clock reads as the measurement wrapper.
    prior=ROOT/"results/review_summary.json"
    if prior.exists() and "clock_only_control" in json.loads(prior.read_text()):
        result["clock_only_control"]=json.loads(prior.read_text())["clock_only_control"]
    else:
        clock=[]
        for _ in range(10000):
            w=time.perf_counter_ns();c=time.process_time_ns()
            cp=time.process_time_ns()-c;wa=time.perf_counter_ns()-w
            clock.append((wa,cp))
        clock=np.array(clock)
        result["clock_only_control"]=dict(measured_after_campaign=True,subtracted=False,samples=len(clock),
                median_wall_ns=float(np.median(clock[:,0])),p95_wall_ns=float(np.quantile(clock[:,0],.95)),
                median_cpu_ns=float(np.median(clock[:,1])))
    (ROOT/"results/review_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
