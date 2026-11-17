"""Write a numerical report from the saved summaries and audited endpoints."""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent


def main():
    summary = json.loads((ROOT/"summary.json").read_text())
    audit = json.loads((ROOT/"audit.json").read_text())
    assert audit["passed"]
    def select(experiment, size, model, target="p95_ns"):
        return next(r for r in summary["rows"] if r["experiment"] == experiment and r["size"] == size
                    and r["model"] == model and r["target"] == target)
    def table(experiment, target="p95_ns"):
        lines = ["| Training size | Training cases (range) | Base | Base + graph | Graph, sampled feature omitted |",
                 "|---|---:|---:|---:|---:|"]
        for size in sorted({r["size"] for r in summary["rows"] if r["experiment"] == experiment}):
            rows = [select(experiment, size, model, target) for model in ("B2", "B3", "B3_stable")]
            base = rows[0]
            lines.append(f"| {size} | {base['train_cases_min']}–{base['train_cases_max']} | "
                         + " | ".join(f"{r['heldout_error_factor']:.5f}" for r in rows) + " |")
        return "\n".join(lines)
    subgroup_rows = []
    for experiment, label in (("expansion_fixed_noise", "Fixed p=0.001"), ("expansion_mixed_noise", "Mixed noise")):
        for blocks in (4, 6):
            values = []
            for model in ("B2", "B3", "B3_stable"):
                details = select(experiment, 11, model)["group_details"]
                values.append(float(np.exp(np.mean([v["heldout_mae_log"] for group, v in details.items()
                                                     if f"/q{blocks}_" in group]))))
            subgroup_rows.append(f"| {label} | {blocks} | "+" | ".join(f"{value:.5f}" for value in values)+" |")
    report = """# Incremental-training results

13 November 2026. Post hoc development analysis of existing measurements.

## Main finding

Adding distinct measured programs substantially improves the structural model's
held-out prediction. Its original disadvantage is not a reliable indication that
the graph information is useless. The fixed-noise result becomes a small,
feature-sensitive advantage for the full graph model. The mixed-noise comparison
gives a larger and more consistent p95 advantage for both augmented feature sets.
These observations support a training-data/support limitation as one plausible
explanation, without uniquely diagnosing underfitting versus overfitting.

No new decoder shots were collected. The original 78 configurations were joined
with 47 complete discovery configurations, giving 125 available examples. The
single resource-censored discovery configuration was excluded before fitting.
The primary fixed-noise expansion uses 117 available configurations in total,
with each held-out program's configurations excluded from its training set.

## What was run

- Original pilot: seven related motif groups, merging single/repeated logical-CNOT
  implementations. For each fixed held-out group, every training subset of two
  through six other groups was evaluated.
- Expansion: retain the original 78 examples as training, hold each of 12 new
  parents out in turn, and add 0/2/4/6/8/11 of the other parents. Ten seeded nested
  orders per held-out parent use exactly the same subsets for all models.
- For every subset, each model and each target selected its own ridge penalty
  using only inner training-group holdouts. The grid was 0.0001 through 10000
  in powers of ten. Every scaler was fitted inside its own training split.
- Compare base inputs (six), base plus original graph summaries (15), and a
  declared sensitivity omitting the row-number-sensitive sampled feature (14).

There were 1,839 outer subset/order evaluations and 5,517 model evaluations,
using 2,610 distinct cached final training fits and 32,613 SVD decompositions.
These are computational evaluations, not independent experimental replications.
The fitting campaign took about 13 seconds on one configured thread at reduced
process priority; long optimization is unnecessary for these small direct fits.

## Held-out p95 error curves

Values are exp(mean absolute log error), with equal weight for each held-out
group after averaging its training subsets/orders. One is perfect; lower is
better. The groups tested in one curve stay fixed as training increases.
Each table is a separate evaluation domain and should be read within that domain.

### Original pilot

Training size counts motif groups. The base model remains better at the largest
training size, even though the augmented models improve substantially.

{original}

### Primary expansion: fixed noise

Training size counts additional new parents on top of the original 78 examples.
At the endpoint, the full graph model is better in six of 12 held-out parents;
the version omitting the sampled feature is better in five of 12. Thus the small
aggregate full-model advantage is not uniform or robust to the declared feature
sensitivity.

{fixed}

### Secondary expansion: mixed noise

At the endpoint, both augmented feature sets improve on the base model in
11 of 12 held-out parents. The full-model error factor is 1.09949 versus 1.13135
for the base; omitting the sampled feature gives 1.10235. This is more encouraging
than the fixed-noise comparison. However, the additional data change noise and
program coverage together, so the improvement cannot be assigned solely to
training-set size or uniquely to graph structure.

{mixed}

## Where the gains occur

The following is a descriptive endpoint breakdown, not a newly selected primary
test. It shows why the small aggregate fixed-noise advantage needs care.

| Domain | Blocks | Base | Base + graph | Graph, sampled feature omitted |
|---|---:|---:|---:|---:|
{subgroups}

At fixed noise, the four-block held-out programs favor the base model on average,
while the six-block programs favor graph additions. Each of the four six-block
parents has only one measured configuration. This concentration and the unequal
group composition prevent a general claim that the augmented model now wins.
The mixed-noise p95 result also favors graph additions on the four-block subset.

## Training gaps and the mean target

The plots retain training errors as dashed lines. These are equal-training-group
resubstitution errors; they are not estimates of generalization. They need not
decrease as data are added because the training distribution and selected penalty
change. Some held-out parents can be easier than the average training group.

The mean-latency endpoint does not show the same consistent structural advantage:

| Domain | Base | Base + graph | Graph, sampled feature omitted |
|---|---:|---:|---:|
{means}

Both targets and all three feature sets are retained in `summary.json`, rather
than selecting a favorable target or dropping the sensitivity result.

## What the tests do and do not establish

The results support taking the limited-training concern seriously. They weaken
any broad interpretation of the original negative p95 comparison. They do not
show that extra fitting time is needed: direct ridge solves have no epoch budget.
They also do not prove that a sufficiently flexible base-input model would lose,
that static topology is necessary, or that a practical admission policy improves.
The six base inputs may require nonlinear responses or interactions, which this
comparison does not test.

These are previously inspected development data. There is no fresh blind test,
confidence claim from repeated orders, or asymptotic learning-curve claim. Only
12 new parent programs are available, with unequal case composition. Old targets
use 6,000 shots per case and discovery targets 768; target-estimation precision
therefore differs. Some high-noise cases have poor logical-Z accuracy. The scope
remains one-sector full-block CPU decoding, without a logical-accuracy filter,
feature-extraction overhead comparison, or demonstrated useful compiler schedule.

All earlier frozen coefficients and safety-margin counterexamples remain intact.
These new models use newly selected penalties and are developmental fits; their
prediction errors do not establish a safe replacement admission rule.

The next comparison should use one predeclared interaction-capable base-input
model against the same model with stable graph descriptors, with balanced
independent noise/size variation and new reserved programs. Logical accuracy and
actual compiler decision value must be explicit gates before a paper-level claim.

## Numerical and artifact checks

The separate sklearn audit verified all 5,517 outer-model metrics and memberships,
fixed test sets, and nested expansion orders. It reproduced 114 model fits and
their inner hyperparameter selections using sklearn pipelines and a Cholesky
solver instead of the experiment's vectorized SVD path. Maximum prediction
difference was {pred_diff:.3g} in log units; maximum inner-loss difference was
{loss_diff:.3g}. The audit passed. This is separate checking code by the same
assistant, not external review.

All earlier manifest entries were reverified, including the original 905-file
artifact. `run_config.json` records the protocol, code, input, feature-column,
and package hashes before the fits. This is local provenance, not external
preregistration. Raw fold predictions, selected alphas, inner losses, counts,
and checkpoints are retained.

Outputs: `learning_curves.png`, `learning_curves_sensitivity.png`, `summary.json`,
`audit.json`, `preparation.json`, and `checkpoints/`.
"""
    means = []
    for experiment, label, size in (("original", "Original pilot, 6 groups", 6),
                                    ("expansion_fixed_noise", "Fixed-noise expansion, +11", 11),
                                    ("expansion_mixed_noise", "Mixed-noise expansion, +11", 11)):
        means.append("| "+label+" | "+" | ".join(f"{select(experiment, size, m, 'mean_ns')['heldout_error_factor']:.5f}"
                                                  for m in ("B2", "B3", "B3_stable"))+" |")
    report = report.format(original=table("original"), fixed=table("expansion_fixed_noise"),
                           mixed=table("expansion_mixed_noise"), subgroups="\n".join(subgroup_rows),
                           means="\n".join(means), pred_diff=audit["max_log_prediction_difference"],
                           loss_diff=audit["max_inner_loss_difference"])
    (ROOT/"findings.md").write_text(report)
    print("Wrote findings.md from audited summary")


if __name__ == "__main__":
    main()
