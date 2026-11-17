"""Aggregate the declared incremental-training experiments without model selection."""
from pathlib import Path
from collections import defaultdict
import json
import os
os.environ["MPLCONFIGDIR"] = "/private/tmp/structure-decoder-learning-mpl"
import numpy as np

ROOT = Path(__file__).resolve().parent
MODELS = ["B2", "B3", "B3_stable"]
TARGETS = ["mean_ns", "p95_ns"]


def load_jobs():
    return [j for p in sorted((ROOT/"checkpoints").glob("*.json"))
            for j in json.loads(p.read_text())["jobs"]]


def main():
    jobs = load_jobs()
    cells = defaultdict(lambda: defaultdict(list))
    counts = defaultdict(list)
    for job in jobs:
        counts[job["experiment"], job["size"]].append(job["train_cases"])
        for model in MODELS:
            result = job["models"][model]
            for index, target in enumerate(TARGETS):
                cells[job["experiment"], job["size"], model, target][job["held_group"]].append(
                    dict(train=result["train_mae_log_group_balanced"][index],
                         heldout=result["heldout_mae_log"][index], alpha=result["selected_alphas"][index]))
    rows = []
    for (experiment, size, model, target), groups in sorted(cells.items()):
        by_group = {group: dict(train_mae_log=float(np.mean([v["train"] for v in values])),
                               heldout_mae_log=float(np.mean([v["heldout"] for v in values])),
                               evaluated_orders_or_subsets=len(values)) for group, values in groups.items()}
        train = np.array([g["train_mae_log"] for g in by_group.values()])
        heldout = np.array([g["heldout_mae_log"] for g in by_group.values()])
        alpha_counts = defaultdict(int)
        for values in groups.values():
            for value in values:
                alpha_counts[str(value["alpha"])] += 1
        n = counts[experiment, size]
        rows.append(dict(experiment=experiment, size=size, model=model, target=target,
                         held_groups=len(groups), group_details=by_group,
                         training_error_factor=float(np.exp(train.mean())),
                         heldout_error_factor=float(np.exp(heldout.mean())),
                         heldout_group_factor_quartiles=np.exp(np.quantile(heldout, [.25, .75])).tolist(),
                         train_cases_min=min(n), train_cases_median=float(np.median(n)), train_cases_max=max(n),
                         selected_alpha_counts=dict(alpha_counts)))
    comparisons = []
    for experiment, size in sorted(counts):
        for target in TARGETS:
            matching = {r["model"]: r for r in rows if r["experiment"] == experiment and r["size"] == size and r["target"] == target}
            for model in MODELS[1:]:
                gain = {g: matching["B2"]["group_details"][g]["heldout_mae_log"]-details["heldout_mae_log"]
                        for g, details in matching[model]["group_details"].items()}
                comparisons.append(dict(experiment=experiment, size=size, target=target, augmented_model=model,
                    base_minus_augmented_mae_log=float(np.mean(list(gain.values()))),
                    held_groups_augmented_better=sum(v > 0 for v in gain.values()),
                    held_groups=len(gain), group_gains=gain))
    result = dict(post_hoc=True, jobs=len(jobs), model_outer_evaluations=len(jobs)*len(MODELS),
                  rows=rows, paired_comparisons=comparisons,
                  aggregation="Average log losses over orders/subsets within each held group, then equally over groups; exponentiate last",
                  group_quartiles_are_confidence_intervals=False,
                  frozen_stress_predictor_updated=False, decoder_shots_collected=0)
    (ROOT/"summary.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps([{k: r[k] for k in ("experiment", "size", "model", "heldout_error_factor", "training_error_factor")}
                      for r in rows if r["target"] == "p95_ns" and r["size"] in (0, 6, 11)], indent=2))
    plot(rows)


def plot(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    colors = {"B2": "#3366aa", "B3": "#c47728", "B3_stable": "#38836b"}
    labels = {"B2": "Base inputs", "B3": "Base + graph statistics", "B3_stable": "Graph statistics, sampled feature omitted"}
    experiments = ["original", "expansion_fixed_noise", "expansion_mixed_noise"]
    titles = ["Original pilot · 7 related groups", "Add new programs · fixed noise", "Add new programs · mixed noise"]
    for sensitivity in (False, True):
        models = MODELS if sensitivity else MODELS[:2]
        fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
        for column, experiment in enumerate(experiments):
            for row, target in enumerate(("p95_ns", "mean_ns")):
                ax = axes[row, column]
                for model in models:
                    rr = sorted([r for r in rows if r["experiment"] == experiment and r["target"] == target and r["model"] == model], key=lambda r: r["size"])
                    x = [r["size"] for r in rr]
                    ax.plot(x, [r["heldout_error_factor"] for r in rr], color=colors[model], marker="o", lw=2)
                    ax.plot(x, [r["training_error_factor"] for r in rr], color=colors[model], ls="--", lw=1.2)
                ax.axhline(1, color="#999999", lw=.8)
                ax.set_xticks(x)
                ax.set_xlabel("Training motif groups" if experiment == "original" else "New training programs added to 78 original cases")
                ax.set_ylabel(("p95" if target == "p95_ns" else "Mean")+" latency error factor")
                ax.set_ylim(bottom=.99)
                if row == 0:
                    ax.set_title(titles[column])
        handles = [Line2D([0], [0], color=colors[m], lw=2, label=labels[m]) for m in models]
        handles += [Line2D([0], [0], color="#555555", lw=2, label="Held-out groups"),
                    Line2D([0], [0], color="#555555", ls="--", label="Training (resubstitution)")]
        fig.legend(handles=handles, loc="outside lower center", ncol=3 if sensitivity else 4, frameon=False)
        fig.suptitle("Incremental training with nested regularization · post hoc analysis\nFixed test groups along each curve; overlapping orders are not independent replications", fontsize=13)
        name = "learning_curves_sensitivity" if sensitivity else "learning_curves"
        fig.savefig(ROOT/(name+".png"), dpi=180)
        fig.savefig(ROOT/(name+".pdf"))
        plt.close(fig)


if __name__ == "__main__":
    main()
