"""Static supplementary figure from saved post hoc controls."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
component=json.loads((ROOT/"results/component_control/summary.json").read_text())
replay=json.loads((ROOT/"results/slow_replay/summary.json").read_text())
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
fig,axes=plt.subplots(1,2,figsize=(11,4.8),constrained_layout=True)
ax=axes[0]
for j,(family,color) in enumerate((("fanout","#34689c"),("repeated","#c77832"))):
    rows=[r for r in component if r["family"]==family]
    offsets={"early":-.10,"spread":0,"late":.10}
    xx=[r["distance"]+offsets[r["placement"]]+(-.18 if j==0 else .18) for r in rows]
    ax.scatter(xx,[r["mean_speedup"] for r in rows],s=45,label=family,color=color,alpha=.9)
ax.axhline(1,color="gray",linestyle="--",linewidth=1)
ax.set(xticks=[3,5,7],xlabel="Code distance (jitter separates placements)",
       ylabel="Joint mean / sequential component mean",title="A  Ordinary decomposition control")
ax.legend(title="Program",fontsize=9)
ax.text(.04,.17,"54,000 paired physical shots\nSame failure indicators on all tested shots",
        transform=ax.transAxes,va="top",fontsize=9)
ax=axes[1]
extremes=[r for r in replay if r["kind"]=="extreme"]
xx=np.array([r["original_wall_ns"] for r in extremes])/1e6
yy=np.array([r["replay_cpu_median_ns"] for r in extremes])/1e6
ax.scatter(xx,yy,s=45,color="#4b866e")
low=min(xx.min(),yy.min())*.97;high=max(xx.max(),yy.max())*1.03
ax.plot([low,high],[low,high],color="gray",linestyle="--",linewidth=1)
ax.set(xlim=(low,high),ylim=(low,high),xlabel="Original selected wall time (ms)",
       ylabel="Median replay process CPU time (ms)",title="B  Selected extremes consume decoder CPU")
ax.text(.04,.96,"10 slowest primary shots, 3 replays each\nSelection does not estimate tail probability",
        transform=ax.transAxes,va="top",fontsize=9)
fig.suptitle("Post hoc diagnostic controls · logical-Z sector · fixed BP+LSD-0",fontsize=12)
fig.savefig(ROOT/"results/diagnostic_controls.png",dpi=180)
fig.savefig(ROOT/"results/diagnostic_controls.pdf")
