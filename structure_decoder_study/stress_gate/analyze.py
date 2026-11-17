"""Fixed-predictor failure map; no fitting to new timings."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from scipy.stats import beta,binom

ROOT=Path(__file__).resolve().parent


def probability_interval(k,n,alpha):
    if not n:return [0.,1.]
    return [0. if k==0 else float(beta.ppf(alpha/2,k,n-k+1)),
            1. if k==n else float(beta.ppf(1-alpha/2,k+1,n-k))]


def quantile_interval(values,p,alpha):
    values=np.sort(values);n=len(values)
    lo=int(binom.ppf(alpha/2,n,p));hi=int(binom.ppf(1-alpha/2,n,p))+1
    return [0. if lo==0 else float(values[lo-1]),
            None if hi>n else float(values[hi-1])]


def analyze(phase):
    config=json.loads((ROOT/"run_config.json").read_text())
    cases=json.loads((ROOT/"corpus.json").read_text())
    if phase=="confirmation":
        selection=json.loads((ROOT/"confirmation_selection.json").read_text())
        cases=[r for r in cases if r["name"] in selection["names"]]
    nc=len(cases);summaries=[]
    for case in cases:
        raw=[];session_stats=[];censored=False
        for session in range(3):
            path=ROOT/"results"/phase/f"session_{session}"/f"{case['name']}.npz"
            a=np.load(path);meta=json.loads(path.with_suffix(".json").read_text())
            raw.append(a);censored|=meta["censored"]
            for clock in ("wall","cpu"):
                k=int(np.sum(a[f"{clock}_ns"]>case["budget_ns"]))
                session_stats.append(dict(session=session,clock=clock,shots=len(a[f"{clock}_ns"]),misses=k,
                                          miss_interval=probability_interval(k,len(a[f"{clock}_ns"]),.05/(nc*3))))
        wall=np.concatenate([a["wall_ns"] for a in raw]);cpu=np.concatenate([a["cpu_ns"] for a in raw])
        failures=np.concatenate([a["logical_z_failure"] for a in raw])
        iterations=np.concatenate([a["bp_iterations"] for a in raw]);converged=np.concatenate([a["bp_converged"] for a in raw])
        row={k:case[k] for k in ("name","program","axis","distance","blocks","rounds","p","placement",
                                 "features","outside_training_features","nearest_training_distance","predictions","budget_ns")}
        row.update(shots=len(wall),censored=bool(censored),session_stats=session_stats,
                   mean_wall_ns=float(wall.mean()),p95_wall_ns=float(np.quantile(wall,.95)),
                   mean_cpu_ns=float(cpu.mean()),p95_cpu_ns=float(np.quantile(cpu,.95)),
                   max_wall_ns=int(wall.max()),max_cpu_ns=int(cpu.max()),
                   bp_fallback_fraction=float(np.mean(~converged)),bp_iterations_mean=float(iterations.mean()),
                   logical_z_failures=int(failures.sum()),logical_z_failure_fraction=float(failures.mean()),
                   logical_z_interval=probability_interval(int(failures.sum()),len(wall),.05/nc))
        for clock,values in (("wall",wall),("cpu",cpu)):
            k=int(np.sum(values>case["budget_ns"]))
            row[f"{clock}_miss_probability"]=k/len(values)
            row[f"{clock}_miss_interval"]=(None if censored else probability_interval(k,len(values),.05/nc))
        row["p95_wall_interval"]=(None if censored else quantile_interval(wall,.95,.05/nc))
        prediction=case["predictions"]["p95_ns"]["B2"]
        row["raw_p95_underprediction_ratio"]=row["p95_wall_ns"]/prediction["raw_ns"]
        row["padded_p95_underprediction_ratio"]=row["p95_wall_ns"]/prediction["padded_ns"]
        row["raw_mean_underprediction_ratio"]=row["mean_wall_ns"]/case["predictions"]["mean_ns"]["B2"]["raw_ns"]
        row["raw_admitted"]=prediction["raw_ns"]<=case["budget_ns"]
        row["padded_admitted"]=prediction["padded_ns"]<=case["budget_ns"]
        row["confident_false_admission"]=(not censored and row["padded_admitted"] and row["wall_miss_interval"][0]>.05)
        row["all_sessions_false_admission"]=(not censored and row["padded_admitted"] and
                     all(s["miss_interval"][0]>.05 for s in session_stats if s["clock"]=="wall"))
        row["confident_raw_underprediction_1_5"]=(not censored and row["p95_wall_interval"][0]>1.5*prediction["raw_ns"])
        row["confident_padded_underprediction_1_5"]=(not censored and row["p95_wall_interval"][0]>1.5*prediction["padded_ns"])
        row["confident_conservative_rejection"]=(not censored and not row["padded_admitted"] and row["wall_miss_interval"][1]<.05)
        # Rare-event means are descriptive; no finite-variance/coverage claim.
        nslow=max(1,int(np.ceil(.01*len(wall))))
        row["top_one_percent_time_fraction"]=float(np.sort(wall)[-nslow:].sum()/wall.sum())
        summaries.append(row)
    aggregate=dict(phase=phase,cases=len(summaries),observed_shots=sum(r["shots"] for r in summaries),
                   censored_cases=[r["name"] for r in summaries if r["censored"]],
                   confident_false_admissions=[r["name"] for r in summaries if r["confident_false_admission"]],
                   all_session_false_admissions=[r["name"] for r in summaries if r["all_sessions_false_admission"]],
                   raw_material_underpredictions=[r["name"] for r in summaries if r["confident_raw_underprediction_1_5"]],
                   padded_material_underpredictions=[r["name"] for r in summaries if r["confident_padded_underprediction_1_5"]],
                   confident_conservative_rejections=[r["name"] for r in summaries if r["confident_conservative_rejection"]],
                   confidence_scope="Bonferroni exact-binomial intervals under stated IID assumptions; not a deployment guarantee")
    (ROOT/"results"/f"{phase}_summaries.json").write_text(json.dumps(summaries,indent=2)+"\n")
    (ROOT/"results"/f"{phase}_analysis.json").write_text(json.dumps(aggregate,indent=2)+"\n")
    if phase=="discovery":
        eligible=[r for r in summaries if not r["censored"]]
        chosen=sorted(eligible,key=lambda r:(not r["confident_false_admission"],-r["padded_p95_underprediction_ratio"],r["name"]))[:6]
        output=dict(names=[r["name"] for r in chosen],selection="False-admission priority, then largest padded p95 underprediction ratio; name tie-break",
                    discovery_analysis_sha256=hashlib.sha256((ROOT/"results/discovery_analysis.json").read_bytes()).hexdigest())
        (ROOT/"confirmation_selection.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(aggregate,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("phase",choices=["discovery","confirmation"])
    analyze(parser.parse_args().phase)
