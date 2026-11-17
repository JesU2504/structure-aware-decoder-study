"""Write an evidence-led report and static scientific figures for this gate."""
from common import *


def main():
    assert read(ROOT/"model_audit.json")["passed"] and read(ROOT/"bridge_audit.json")["passed"]
    models = read(ROOT/"model_summary.json")
    bridge = read(ROOT/"bridge_analysis.json")
    corpus = read(ROOT/"corpus.json")
    def factor(domain, model, target):
        return next(r["heldout_error_factor"] for r in models["rows"] if r["domain"] == domain and r["model"] == model and r["target"] == target)
    def development_table(target):
        rows = ["| Model | Original groups | Fixed-noise new parents | Mixed-noise new parents |", "|---|---:|---:|---:|"]
        for kind in ("linear", "rbf"):
            for features in ("base6", "density8", "graph16"):
                model = kind+"_"+features
                rows.append("| "+model+" | "+" | ".join(f"{factor(d, model, target):.5f}" for d in ("original", "fixed_noise", "mixed_noise"))+" |")
        return "\n".join(rows)
    score = {(r["model"], r["target"]): r for r in bridge["model_scores"]}
    bridge_rows = ["| Model | Mean error factor | p95 error factor |", "|---|---:|---:|"]
    for model in sorted({r["model"] for r in bridge["model_scores"]}):
        bridge_rows.append(f"| {model} | {score[model,'mean_ns']['heldout_parent_error_factor']:.5f} | {score[model,'p95_ns']['heldout_parent_error_factor']:.5f} |")
    decisions = [r for r in bridge["schedule_decisions"] if r["choice_is_nontrivial"]]
    decision_rows = ["| Policy | Point-oracle matches (of 4) | Parent-balanced point regret factor |", "|---|---:|---:|"]
    for row in bridge["policy_regret"]:
        decision_rows.append(f"| {row['policy']} | {row['point_oracle_matches']} | {row['parent_balanced_point_regret_factor']:.5f} |")
    admission_rows = ["| Budget ms | Nonlinear base, raw | Nonlinear graph, raw | Nonlinear base, padded | Nonlinear graph, padded | Profile upper |",
                      "|---:|---:|---:|---:|---:|---:|"]
    chosen_policies = ["rbf_density8/raw", "rbf_graph16/raw", "rbf_density8/padded", "rbf_graph16/padded", "profile_upper"]
    for budget in BUDGET_MS:
        values = []
        for policy in chosen_policies:
            row = next(r for r in bridge["budget_sweep"] if r["budget_ms"] == budget and r["policy"] == policy)
            values.append(f"{row['qualified_confident_false_admissions']} / {row['qualified_confident_conservative_rejections']} / {row['qualified_admitted']}")
        admission_rows.append(f"| {budget:g} | "+" | ".join(values)+" |")
    bp = [r for r in bridge["paired_controls"] if r["alternative"] == "whole100"]
    component = next(r for r in bridge["paired_controls"] if r["alternative"] == "components30")
    features_base = np.median([r["feature_timing"]["base_density_ns"] for r in corpus])/1e6
    features_graph = np.median([r["feature_timing"]["full_stable_ns"] for r in corpus])/1e6
    profile_cost = np.median([r["timed_decode_wall_ns"] for r in bridge["profiling"].values()])/1e6
    new_only = {}
    for model in ("rbf_density8", "rbf_graph16"):
        new_only[model] = {}
        for target in TARGETS:
            details = score[model, target]["parent_mae_log"]
            new_only[model][target] = float(np.exp(np.mean([v for g,v in details.items() if g.startswith("new/")])))
    report = f"""# Validation-gate findings

Prepared on 13 November; model audit, bridge measurements, and analysis completed
15 November 2026 (Asia/Tokyo client date). This is internal development/calibration
evidence, not a final reserved-parent test or external peer review.

## Decision

The gate does **not** justify expanding a topology-focused p95/admission paper
automatically. A modest nonlinear model using the original base information
outperforms graph-augmented models on held-out p95 prediction. In the bridge's
quality-screened schedule choices, the graph features add no demonstrated
selection benefit over that stronger base control.

This changes the interpretation of the earlier learning-curve result: extra
training helped the structural model, but that alone did not establish that it
needed extra graph information rather than a more suitable use of existing
inputs. Underfitting and overfitting are not uniquely diagnosed, and topology is
not proved universally unnecessary.

There is a separate **exploratory mean-latency signal** favoring nonlinear graph
features in some comparisons. It is preserved below. Switching the headline to
throughput would be a new hypothesis requiring a prospective decision experiment,
not successful completion of the prespecified p95 gate.

## What was completed

- Six model variants: linear/RBF-kernel ridge crossed with base6, density8, and
  graph16. The primary four-way comparison uses density8 and graph16. Density
  ratios are functions of base6 and add no new information.
- Nested parent/motif holdouts, training-only scaling and kernel/target centering,
  fixed parameter grids, and equal procedures across feature sets. There are
  186 outer model fits. The sampled row-sensitive graph feature is excluded.
- Nineteen bridge configurations, balanced across four-/six-block calibration
  parents, two noise rates, and burst/spread placement, plus three exact old
  references. Stable features passed 57 relabeling checks.
- Three fresh timing processes, randomized 64-shot blocks, paired BP30/BP100
  physical streams, and ordinary component decomposition for the disconnected
  memory reference.
- **{bridge['physical_evaluation_shots']:,} new physical evaluation shots** and
  **{bridge['evaluation_decoder_calls']:,} evaluation decoder calls**; a disjoint
  **{bridge['physical_profiling_shots']:,}-shot profiling stream**; and
  {bridge['physical_warmup_shots']:,} separate physical warmup shots. No resource
  cap stopped a configuration. Warmups are not evaluation observations.

No new final-test parents were opened. The new configurations use previously
inspected parents, so the bridge is calibration rather than unseen-program
confirmation. Old frozen predictions and measurement files remain unchanged.

## Stronger controls on existing development data

All table values are exp(mean absolute log prediction error), equally weighted
over held-out groups. One is perfect; lower is better. Models use log1p inputs
and log targets. The three columns are distinct declared evaluation domains.

### Primary p95 target

{development_table('p95_ns')}

The primary nonlinear base-versus-graph comparison is 1.03970 versus 1.05093 at
fixed noise, and 1.04216 versus 1.05755 with mixed noise. Even the nonlinear model
with the original six inputs beats the graph-augmented controls in p95 here.
The very large improvement from the old mixed-noise linear base6 to linear
density8 also shows how a change of representation can help without new
information. This is a bounded model-class comparison, not an exhaustive proof.

### Secondary mean target

{development_table('mean_ns')}

Nonlinear graph16 improves mixed-noise mean prediction relative to nonlinear
base controls, while its fixed-noise mean improvement over nonlinear base6 is
negligible. Linear graph16 is worse on the mixed-noise mean target. Thus neither
the feature set nor one chosen target should be declared a universal winner.

## Frozen-prediction bridge performance

Bridge predictions were recorded before new timing. Each calibration parent's
configurations are excluded from its fitted model and inner selection. Exact
old references use the corresponding original-motif outer fit; new calibration
parents use the corresponding mixed-noise new-parent fit. Both sides of a feature
comparison use the same data. The following aggregate gives equal weight to the
three old and four new parent groups; it is a calibration mixture, not a random
application-population estimate.

{chr(10).join(bridge_rows)}

Restricting descriptively to the four new bridge parents retains the same
direction: nonlinear density8 versus graph16 p95 factors are
{new_only['rbf_density8']['p95_ns']:.5f} versus {new_only['rbf_graph16']['p95_ns']:.5f}; mean factors are
{new_only['rbf_density8']['mean_ns']:.5f} versus {new_only['rbf_graph16']['mean_ns']:.5f}.
The observed mean benefit is a development signal; heavy-tail mean uncertainty
and changed measurement context still need prospective treatment.

## Concrete same-program choices

The objective was CPU service p95 at matched logical action, distance, rounds,
and instruction/TICK counts. No quantum-duration improvement is asserted.
Candidate quality is shared across all policies using a retrospective one-sided
logical-Z upper-bound screen of 1% per whole task. This is a declared pilot screen,
not a full FTQC accuracy target or a deployable learned accuracy policy.

Four pairs have both alternatives screen-qualified; one further pair has only
one qualified alternative and three have none. The four nontrivial pairs are
all at p=0.0003, one for each calibration parent. Burst is the point-estimate
lowest-p95 variant in all four. Three cost orders have disjoint declared p95
intervals; the q4_P00 order is unresolved.

{chr(10).join(decision_rows)}

The nonlinear graph model's wrong point choice is q6_P03, whose cost order is
interval-resolved; its selected spread variant has about 5.49% larger measured
p95 than burst. The nonlinear density8 base and direct profiling match all four
point oracles, including the unresolved one. This is four calibration choices,
not a population success rate or a proof of oracle equality. Uncertainty in the
finite measured oracle is retained.

## Admission is a tradeoff, not just prediction MAE

The full prespecified budget sweep is retained. Each cell below is **confident
false admissions / confident conservative rejections / total admitted**, among
the ten BP30 screen-qualified configurations. Miss-rate truth is unresolved where
its adjusted interval crosses 5%; unresolved cases are not counted as either
confirmed error. All nineteen-configuration counts and raw model variants are
in `bridge_analysis.json`.

{chr(10).join(admission_rows)}

The 2 ms row must not be hidden: raw nonlinear graph16 has zero confident false
admissions versus one for raw nonlinear density8, but it admits fewer candidates
and has one confident conservative rejection versus zero. The graph model can
therefore look better on a selected risk metric while being more conservative.
This is not a matched-risk superiority result. Historical safety margins remove
that observed false admission but reject many feasible cases; the profile upper
bound has a different cost/conservatism tradeoff.

At the inherited illustrative 5 ms budget there is again no confident false
admission difference between the base and graph predictors. None of these
diagnostic budgets has been established as a deployment requirement. No useful
system-wide risk guarantee follows from service-time intervals.

## Decoder configuration alternative

Increasing max BP iterations from 30 to 100 increases measured p95 in all 19
configurations: the ratio ranges from {min(r['p95_wall_ratio'] for r in bp):.3f} to
{max(r['p95_wall_ratio'] for r in bp):.3f}, with median {np.median([r['p95_wall_ratio'] for r in bp]):.3f}.
Median mean-CPU ratio is {np.median([r['mean_cpu_ratio'] for r in bp]):.3f}.
Across paired evaluation shots, {sum(r['logical_improved'] for r in bp)} logical-Z outcomes improve and
{sum(r['logical_worsened'] for r in bp)} worsen. Those pooled counts mix workloads; they do not certify
equal accuracy, noninferiority, or a globally optimal BP cap. This one alternative
does not support the concern that simply giving BP more iterations repairs the
observed cost behavior on the bridge.

Ordinary component decomposition on the memory reference gives p95 ratio
{component['p95_wall_ratio']:.3f} and mean-CPU ratio {component['mean_cpu_ratio']:.3f}, with
{component['logical_improved']} improved and {component['logical_worsened']} worsened logical-Z outcomes. Its per-call timing includes
gather/merge work. This confirms a standard baseline's value for that case; it
is not a new decoder algorithm or a full-system speedup.

## Context and overhead

Across the eleven exact historical references, current/historical p95 ratios
range from {min(r['p95_current_historical_ratio'] for r in bridge['historical_bridge']):.3f} to
{max(r['p95_current_historical_ratio'] for r in bridge['historical_bridge']):.3f}, with median
{np.median([r['p95_current_historical_ratio'] for r in bridge['historical_bridge']]):.3f}.
The interleaved bridge thus does not reveal a large uniform cohort multiplier.
Individual shifts and mean changes remain, and this does not isolate frequency,
thermal state, implementation ordering, syndrome uncertainty, or background load.

The optimized feature implementation's median recorded base-density time is
{features_base:.4f} ms and full stable-feature time {features_graph:.4f} ms. For comparison, median
timed service cost of the 192 profiling calls per configuration is
{profile_cost:.2f} ms. These are different scopes: profiling initialization and
warmup, shared circuit/DEM generation, validation, and amortization must be counted
for an end-to-end comparison. Inference timings and construction metadata are
retained; these numbers alone are not an overhead-adjusted compiler speedup.

## Confidence and integrity qualifications

All 29,184 evaluation and 3,648 profiling physical streams were replayed. Every
one of 63,552 stored correction vectors was checked against the syndrome and
logical-observable outcome. All 186 outer-model split/metric records were checked;
18 nested fits and their margins were reproduced using separate sklearn code.
The audits passed and all earlier artifact manifests still match. This is internal
checking by the same assistant, not independent peer review or another simulator.

Intervals assume IID shots within a stable context. Repeated-process variation
is not proof of deployment coverage. Logical-quality and timing intervals are
separate adjusted families and do not form a joint 95% safety certificate.
Retrospective calibration eligibility and previously inspected parent identities
prevent calling the decision exercise a fresh compiler validation.

The original frozen-model noise-transfer failures remain intact; these newer
fits do not retroactively repair them. The work continues to cover a logical-Z
sector, full-block CPU decoding, and the specified implementations only.

See `RESUMPTION_2026-11-15.md` and `ANALYSIS_IMPLEMENTATION_NOTE.md`: the model work
predates bridge measurement, while analysis implementation was written after
measurement launch and before case-level outcome inspection. No external
pre-registration or external timestamp is claimed.

## Research disposition

Do not launch a large reserved-parent p95/topology campaign on the strength of
the earlier learning curves. The stronger base control and the concrete choices
remove its present justification. Preserve the raw admission tradeoff and the
mean-cost signal rather than selecting only a favorable metric.

If the project continues, choose explicitly between (a) decision-calibrated
transfer/profiling with strong base controls and matched risk, or (b) a new
mean-service/throughput hypothesis using the stable graph features. Either
requires a novelty check and a separately declared prospective utility test with
new reserved parents; neither is established as a publishable contribution by
this gate. Current data remain development evidence and the reserved test remains
unused. The original compiler headline has not passed its entry condition.
"""
    (ROOT/"findings.md").write_text(report)
    plot(models, bridge)
    print("Wrote findings and validation-gate figures")


def plot(models, bridge):
    import os
    os.environ["MPLCONFIGDIR"] = "/private/tmp/structure-decoder-validation-mpl"
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = ["Linear\nbase+density", "Linear\n+ graph", "Nonlinear\nbase+density", "Nonlinear\n+ graph"]
    methods = ["linear_density8", "linear_graph16", "rbf_density8", "rbf_graph16"]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.8), constrained_layout=True)
    for panel, values, title in ((axes[0,0], models["rows"], "A  Development: mixed-noise parent holdout"),
                                 (axes[0,1], bridge["model_scores"], "B  Interleaved calibration bridge")):
        for offset, target, color, label in ((-.18, "mean_ns", "#36836b", "Mean"), (.18, "p95_ns", "#3d68aa", "p95")):
            heights = []
            for method in methods:
                selected = next(r for r in values if r["model"] == method and r["target"] == target and r.get("domain", "mixed_noise") == "mixed_noise")
                heights.append(selected.get("heldout_error_factor", selected.get("heldout_parent_error_factor")))
            panel.bar(np.arange(4)+offset, np.array(heights)-1, bottom=1, width=.34, color=color, label=label)
        panel.set_xticks(np.arange(4), labels)
        panel.set_ylim(1, 1.27)
        panel.set_ylabel("Error factor (1 is perfect)")
        panel.set_title(title)
        panel.legend(frameon=False)
    panel = axes[1,0]
    eligible = [r for r in bridge["schedule_decisions"] if r["choice_is_nontrivial"]]
    methods_c = ["linear_density8", "linear_graph16", "rbf_density8", "rbf_graph16", "profile_point"]
    colors = ["#99b9df", "#edbf8a", "#3768ac", "#bb722d", "#398770"]
    labels_c = ["Linear base", "Linear + graph", "Nonlinear base", "Nonlinear + graph", "Direct profile"]
    for index, (method, color, label) in enumerate(zip(methods_c, colors, labels_c)):
        heights = np.array([r["policies"][method]["point_regret_factor"] for r in eligible])
        panel.bar(np.arange(4)+(index-2)*.15, heights-1, bottom=1, width=.14, color=color, label=label)
        panel.scatter(np.arange(4)+(index-2)*.15, heights, color=color, s=17, zorder=3)
    panel.set_xticks(np.arange(4), [r["parent"].removeprefix("new/")+("*" if not r["cost_order_resolved_by_intervals"] else "") for r in eligible])
    panel.set_ylabel("Selected p95 / measured point oracle")
    panel.set_ylim(.995, 1.27)
    panel.set_title("C  Four quality-screened calibration choices")
    panel.text(.02, .95, "* Cost order unresolved; p=0.0003 in all four", transform=panel.transAxes, va="top", fontsize=9)
    panel.legend(frameon=False, fontsize=8, loc="upper right")
    panel = axes[1,1]
    lookup = {(r["name"], r["setting"]):r for r in bridge["summaries"]}
    plotted = set()
    maximum = 0.
    for row in bridge["paired_controls"]:
        base = lookup[row["name"], "whole30"]
        alt = lookup[row["name"], row["alternative"]]
        group = "Decomposition" if row["alternative"] == "components30" else ("Old reference" if base["source"] == "old_exact" else f"{base['blocks']} blocks")
        color = {"Decomposition":"#398770", "Old reference":"#777777", "4 blocks":"#3768ac", "6 blocks":"#bb722d"}[group]
        x, y = base["p95_wall_ns"]/1e6, alt["p95_wall_ns"]/1e6
        maximum = max(maximum, x, y)
        panel.scatter(x, y, color=color, marker="*" if group == "Decomposition" else "o", s=90 if group == "Decomposition" else 35,
                      label=group if group not in plotted else None)
        plotted.add(group)
    panel.plot([0, maximum], [0, maximum], ls="--", color="#777777", lw=1)
    panel.set_xlabel("BP30 whole-task p95 (ms)")
    panel.set_ylabel("Alternative setting p95 (ms)")
    panel.set_title("D  BP100 costs more; ordinary decomposition helps")
    panel.legend(frameon=False, fontsize=8)
    for panel in axes.flat:
        panel.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Validation gate · declared controls and calibration decisions\nLogical-Z CPU service scope; no reserved-parent or deployment claim", fontsize=13)
    fig.savefig(ROOT/"validation_gate.png", dpi=180)
    fig.savefig(ROOT/"validation_gate.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
