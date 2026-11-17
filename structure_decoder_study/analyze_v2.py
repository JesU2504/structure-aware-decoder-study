"""Fixed-family-holdout analysis of the exploratory pilot, not risk calibration."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import time
import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name]="1"

import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

ROOT=Path(__file__).resolve().parent
MODELS={
    "B0_volume":["volume","distance"],
    "B1_dimensions":["distance","n_detectors","n_faults"],
    "B2_sparsity_activity":["distance","n_detectors","n_faults","nnz","prior_sum","expected_activity"],
    "B3_structure":["distance","n_detectors","n_faults","nnz","prior_sum","expected_activity",
                    "row_degree_var","col_degree_var","row_degree_p95","col_degree_p95",
                    "hyperedge_fraction","components","largest_component_fraction",
                    "component_size_second_moment","two_step_mean"],
}


def save(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")


def score(pred,actual,groups):
    absolute=np.abs(np.log(pred/actual))
    family={g:float(absolute[groups==g].mean()) for g in sorted(set(groups))}
    return dict(mean_absolute_log_error=float(absolute.mean()),
                multiplicative_error=float(np.exp(absolute.mean())),
                median_multiplicative_error=float(np.exp(np.median(absolute))),
                family_balanced_multiplicative_error=float(np.exp(np.mean(list(family.values())))),
                family_mae_log=family,
                underpredict_by_20pct_fraction=float(np.mean(pred<actual/1.2)))


def predictions(records,y,groups):
    results={}
    for model,columns in MODELS.items():
        x=np.log1p([[r["features"][column] for column in columns] for r in records])
        pred=np.full(len(y),np.nan)
        for family in sorted(set(groups)):
            held=groups==family
            estimator=make_pipeline(StandardScaler(),Ridge(alpha=1.0))
            estimator.fit(x[~held],np.log(y[~held]))
            pred[held]=np.exp(estimator.predict(x[held]))
        assert np.isfinite(pred).all()
        results[model]=pred
    return results


def main():
    records=json.loads((ROOT/"corpus.json").read_text())
    cfg=json.loads((ROOT/"frozen_config.json").read_text())
    groups=np.array([r["case"]["family"] for r in records])
    metrics={}
    session_values={}
    data={}
    summaries=[]
    for record in records:
        times=[]
        iterations=[]
        converged=[]
        failures=0
        zero=0
        row={"name":record["name"],**record["case"],**record["features"]}
        sess=[]
        for session in range(cfg["sessions"]):
            path=ROOT/"results"/f"session_{session}"/f"{record['name']}.npz"
            a=np.load(path)
            s=json.loads(path.with_suffix(".json").read_text())
            assert len(a["latency_ns"])==cfg["shots"]
            assert not a["invalid_correction"].any()
            assert s["config_sha256"]==hashlib.sha256((ROOT/"frozen_config.json").read_bytes()).hexdigest()
            times.append(a["latency_ns"])
            iterations.append(a["bp_iterations"])
            converged.append(a["bp_converged"])
            failures+=int(a["logical_z_failure"].sum())
            zero+=int(np.sum(a["syndrome_weight"]==0))
            sess.append(dict(mean_ns=float(a["latency_ns"].mean()),p95_ns=float(np.quantile(a["latency_ns"],.95)),
                             init_ns=s["decoder_init_ns"]))
        tt=np.concatenate(times)
        ii=np.concatenate(iterations)
        cc=np.concatenate(converged)
        row.update(mean_ns=float(tt.mean()),p95_ns=float(np.quantile(tt,.95)),p99_ns=float(np.quantile(tt,.99)),
                   mean_bp_iterations=float(ii.mean()),bp_fallback_fraction=float(np.mean(~cc)),
                   logical_z_failures=failures,shots=len(tt),zero_syndrome_fraction=zero/len(tt),
                   mean_session_max_min=float(max(s["mean_ns"] for s in sess)/min(s["mean_ns"] for s in sess)),
                   p95_session_max_min=float(max(s["p95_ns"] for s in sess)/min(s["p95_ns"] for s in sess)))
        summaries.append(row)
        session_values[record["name"]]=sess
        data[record["name"]]=dict(times=tt,iterations=ii,converged=cc)
    output_rows=[]
    comparison={}
    primary_predictions={}
    for target in ("mean_ns","p95_ns"):
        y=np.array([r[target] for r in summaries])
        preds=predictions(records,y,groups)
        primary_predictions[target]=preds
        metrics[target]={model:score(p,y,groups) for model,p in preds.items()}
        # Family bootstrap of the difference in MAE-log. Small group count limits
        # interpretation; this is not a test-set-selected significance claim.
        fams=sorted(set(groups))
        b2=np.array([metrics[target]["B2_sparsity_activity"]["family_mae_log"][g] for g in fams])
        b3=np.array([metrics[target]["B3_structure"]["family_mae_log"][g] for g in fams])
        delta=b2-b3
        rng=np.random.default_rng(17613)
        draws=delta[rng.integers(0,len(delta),size=(10000,len(delta)))].mean(axis=1)
        comparison[target]=dict(b2_minus_b3_family_mae_log=float(delta.mean()),
                               exploratory_family_bootstrap_95ci=np.quantile(draws,[.025,.975]).tolist(),
                               heldout_families=len(fams))
        for j,r in enumerate(records):
            output_rows.append(dict(name=r["name"],family=groups[j],target=target,actual_ns=float(y[j]),
                                    **{model:float(pred[j]) for model,pred in preds.items()}))
    connected=np.array([r["features"]["components"]==1 for r in records])
    connected_metrics={}
    if len(set(groups[connected]))>=3:
        subset=[r for r,keep in zip(records,connected) if keep]
        for target in ("mean_ns","p95_ns"):
            y=np.array([r[target] for r in summaries])[connected]
            preds=predictions(subset,y,groups[connected])
            connected_metrics[target]={model:score(p,y,groups[connected]) for model,p in preds.items()}
    budget_rows=[]
    y=np.array([r["p95_ns"] for r in summaries])
    deadlines=np.geomspace(y.min()*.8,y.max()*1.2,60)
    for model,pred in primary_predictions["p95_ns"].items():
        for deadline in deadlines:
            actual=y<=deadline
            admitted=pred<=deadline
            unsafe=admitted&~actual
            rejected=~admitted&actual
            budget_rows.append(dict(model=model,deadline_ns=float(deadline),admitted=int(admitted.sum()),
                                    false_admission_rate=float(unsafe.sum()/max(1,admitted.sum())),
                                    false_rejection_rate=float(rejected.sum()/max(1,actual.sum())),
                                    misclassification_fraction=float(np.mean(unsafe|rejected))))
    spreads=[]
    for d in (3,5,7):
        for q in (2,4):
            rr=[r for r in summaries if r["distance"]==d and r["blocks"]==q]
            for target in ("mean_ns","p95_ns"):
                lo=min(rr,key=lambda r:r[target]); hi=max(rr,key=lambda r:r[target])
                spreads.append(dict(distance=d,blocks=q,target=target,ratio=hi[target]/lo[target],
                                    fastest=lo["name"],slowest=hi["name"]))
    # Refit each independent session with exactly the same held-out-family rules.
    per_session={}
    for session in range(cfg["sessions"]):
        per_session[str(session)]={}
        for target in ("mean_ns","p95_ns"):
            yy=np.array([session_values[r["name"]][session][target] for r in records])
            pp=predictions(records,yy,groups)
            per_session[str(session)][target]={model:score(p,yy,groups) for model,p in pp.items()}
    result=dict(cases=len(records),shots=sum(r["shots"] for r in summaries),families=sorted(set(groups)),
                metrics=metrics,structure_comparison=comparison,connected_cases=int(connected.sum()),
                connected_metrics=connected_metrics,per_session=per_session,matched_volume_spreads=spreads,
                invalid_corrections=0,logical_z_failures=sum(r["logical_z_failures"] for r in summaries),
                median_session_mean_max_min=float(np.median([r["mean_session_max_min"] for r in summaries])),
                median_session_p95_max_min=float(np.median([r["p95_session_max_min"] for r in summaries])),
                scope=cfg["scope"],calibrated_risk=False)
    save(ROOT/"results"/"analysis.json",result)
    save(ROOT/"results"/"case_summaries.json",summaries)
    for filename,rows in (("predictions.csv",output_rows),("budget_diagnostics.csv",budget_rows),("case_summaries.csv",summaries)):
        with (ROOT/"results"/filename).open("w") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)
    # Publication-style static artifact; all points are measured or held-out fits.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    fig,axes=plt.subplots(2,2,figsize=(12,8.6),constrained_layout=True)
    ax=axes[0,0]
    colors=plt.get_cmap("tab10")
    for j,g in enumerate(sorted(set(groups))):
        idx=groups==g
        xx=np.array([r["n_detectors"] for r in summaries])[idx]
        ax.scatter(xx,np.array([r["mean_ns"] for r in summaries])[idx]/1e6,label=g,s=24,alpha=.8,color=colors(j))
    ax.set(xscale="log",yscale="log",xlabel="Detector count",ylabel="Mean decode call (ms)",title="A  Measured cost, including zero syndromes")
    ax.legend(fontsize=7,ncol=2)
    ax=axes[0,1]
    for model,color in (("B2_sparsity_activity","#3366aa"),("B3_structure","#d47722")):
        ax.scatter(y/1e6,primary_predictions["p95_ns"][model]/1e6,s=18,alpha=.7,label=model,color=color)
    low=min(y.min(),*(p.min() for p in primary_predictions["p95_ns"].values()))/1e6
    high=max(y.max(),*(p.max() for p in primary_predictions["p95_ns"].values()))/1e6
    ax.plot([low,high],[low,high],color="gray",linestyle="--",linewidth=1)
    ax.set(xscale="log",yscale="log",xlabel="Measured p95 (ms)",ylabel="Held-out prediction (ms)",title="B  Leave-program-family-out predictions")
    ax.legend(fontsize=7)
    ax=axes[1,0]
    fams=sorted(set(groups))
    delta=[metrics["p95_ns"]["B2_sparsity_activity"]["family_mae_log"][g]-metrics["p95_ns"]["B3_structure"]["family_mae_log"][g] for g in fams]
    ax.bar(np.arange(len(fams)),delta,color=["#3d8269" if v>=0 else "#aa5b59" for v in delta])
    ax.axhline(0,color="gray",linewidth=1)
    ax.set_xticks(np.arange(len(fams)),fams,rotation=35,ha="right")
    ax.set(ylabel="B2 error − B3 error (absolute log)",title="C  Structural-feature gain by held-out family")
    ax=axes[1,1]
    for model in MODELS:
        rr=[r for r in budget_rows if r["model"]==model]
        ax.plot([r["deadline_ns"]/1e6 for r in rr],[r["misclassification_fraction"] for r in rr],label=model)
    ax.set(xscale="log",xlabel="Per-task p95 budget (ms)",ylabel="Misclassified fraction",title="D  Descriptive admission errors; uncalibrated")
    ax.legend(fontsize=7)
    fig.suptitle("Exploratory TMCBS logical-Z sector pilot · fixed decoder · full-block windows",fontsize=13)
    fig.savefig(ROOT/"results"/"pilot_overview.png",dpi=180)
    fig.savefig(ROOT/"results"/"pilot_overview.pdf")
    plt.close(fig)
    print(json.dumps(dict(cases=result["cases"],shots=result["shots"],comparison=comparison,
                          p95={k:round(v["family_balanced_multiplicative_error"],4) for k,v in metrics["p95_ns"].items()},
                          connected_p95={k:round(v["family_balanced_multiplicative_error"],4) for k,v in connected_metrics.get("p95_ns",{}).items()},
                          median_session_p95_max_min=result["median_session_p95_max_min"])))


if __name__=="__main__":main()
