"""Scientific failure-map plots from fixed-predictor stress data."""
from pathlib import Path
import json,os
os.environ["MPLCONFIGDIR"]="/private/tmp/structure-decoder-stress-mpl"
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator,FuncFormatter,NullFormatter
ROOT=Path(__file__).resolve().parent

def main():
    rows=json.loads((ROOT/"results/discovery_summaries_reviewed.json").read_text())
    confirmation=json.loads((ROOT/"results/confirmation_summaries_reviewed.json").read_text())
    boundary=json.loads((ROOT/"results/boundary_summaries.json").read_text())
    box=json.loads((ROOT/"results/feature_box_summaries.json").read_text())
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False})
    fig,axes=plt.subplots(2,2,figsize=(12,8.8),constrained_layout=True)
    ax=axes[0,0]
    for outside,color,label in ((False,"#34745e","Within old marginal ranges"),(True,"#c07833","Outside at least one range")):
        rr=[r for r in rows if bool(r["outside_training_features"])==outside and not r["censored"]]
        x=[r["predictions"]["p95_ns"]["B2"]["padded_ns"]/r["budget_ns"] for r in rr]
        y=[r["p95_wall_ns"]/r["budget_ns"] for r in rr]
        ax.scatter(x,y,label=label,color=color,s=32,alpha=.85)
    censored=[r for r in rows if r["censored"]]
    ax.scatter([r["predictions"]["p95_ns"]["B2"]["padded_ns"]/r["budget_ns"] for r in censored],
               [r["p95_wall_ns"]/r["budget_ns"] for r in censored],marker="x",s=65,color="#925c9c",label="Censored; descriptive")
    ax.scatter([r["padded_prediction_ns"]/5e6 for r in box],[r["p95_wall_ns"]/5e6 for r in box],
               marker="*",s=120,color="#7e5799",label="Selected feature-box challenge")
    ax.axvline(1,color="gray",linestyle="--");ax.axhline(1,color="gray",linestyle="--")
    ax.set(xscale="log",yscale="log",xlabel="Frozen padded p95 / illustrative budget",ylabel="Measured p95 / budget",
           title="A  Forecast versus service budget (point estimates)")
    ax.xaxis.set_major_locator(FixedLocator([.2,.5,1,2,4]));ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.legend(fontsize=7,loc="lower right")
    ax=axes[0,1]
    for outside,color,label in ((False,"#34745e","Within ranges"),(True,"#c07833","Outside ranges")):
        rr=[r for r in rows if bool(r["outside_training_features"])==outside and not r["censored"]]
        ax.scatter([r["raw_p95_underprediction_ratio"] for r in rr],[r["raw_mean_underprediction_ratio"] for r in rr],
                   color=color,s=32,label=label,alpha=.85)
    ax.axhline(1.5,color="gray",linestyle="--");ax.axvline(1.5,color="gray",linestyle="--")
    ax.set(xscale="log",yscale="log",xlabel="Measured / raw predicted p95",ylabel="Measured / raw predicted mean",
           title="B  Mean and p95 prediction errors differ")
    ax.xaxis.set_major_locator(FixedLocator([1,1.5,2,3]));ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f"{x:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.legend(fontsize=7)
    ax=axes[1,0]
    for program,color in (("q4_P01","#34679c"),("q4_P03","#a45349")):
        start=next(r for r in rows if r["program"]==program and r["distance"]==5 and r["rounds"]==10 and r["p"]==.001 and r["placement"]=="spread")
        end=next(r for r in confirmation if r["program"]==program and r["p"]==.003)
        rr=[dict(p=.001,miss_probability=start["wall_miss_probability"],miss_interval=start["wall_miss_interval"]),
            *[r for r in boundary if r["program"]==program],
            *[r for r in box if r["name"].startswith(program)],
            dict(p=.003,miss_probability=end["wall_miss_probability"],miss_interval=end["wall_miss_interval"])]
        rr=sorted(rr,key=lambda r:r["p"])
        xs=np.array([r["p"]*100 for r in rr]);ys=np.array([r["miss_probability"]*100 for r in rr])
        intervals=np.array([r["miss_interval"] for r in rr])*100
        ax.errorbar(xs,ys,yerr=np.vstack((ys-intervals[:,0],intervals[:,1]-ys)),marker="o",capsize=3,color=color,label=program)
    ax.axhline(5,color="gray",linestyle="--",label="Illustrative 5% limit")
    ax.set(xlabel="Physical noise parameter p (%)",ylabel="5 ms service-budget miss rate (%)",
           title="C  Noise boundary with H and L held fixed")
    ax.xaxis.set_major_locator(FixedLocator([.1,.15,.2,.25,.3]))
    ax.legend(fontsize=7);ax.text(.02,.96,"Selected tasks; phase-specific adjusted intervals",transform=ax.transAxes,va="top",fontsize=7)
    ax=axes[1,1]
    replays=json.loads((ROOT/"results/mechanisms/replays.json").read_text())
    for is_slow,color,label in ((False,"#7b8b96","First shots"),(True,"#ae7133","Selected slow shots")):
        rr=[r for r in replays if r["selected_slow"]==is_slow and r["lsd_replay_cpu_ns"]>0]
        ax.scatter([r["max_final_cluster_bits"] for r in rr],[r["lsd_replay_cpu_ns"]/1e6 for r in rr],s=28,color=color,label=label)
    ax.set(xscale="log",yscale="log",xlabel="Largest recorded final LSD cluster (mechanism bits)",
           ylabel="Standalone LSD replay CPU (ms)",title="D  Selected mechanism replays (not population data)")
    ax.legend(fontsize=7)
    fig.suptitle("Frozen-model stress exploration · connected logical-Z tasks · no model refitting",fontsize=12)
    fig.savefig(ROOT/"results/failure_map.png",dpi=180);fig.savefig(ROOT/"results/failure_map.pdf")

if __name__=="__main__":main()
