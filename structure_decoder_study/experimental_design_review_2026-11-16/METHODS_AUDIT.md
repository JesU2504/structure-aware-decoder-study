# Experiment-design and execution audit

16 November 2026. Requested before choosing the next research direction.

**Assessment: a useful, substantially checked exploratory study; insufficient
to settle the broad structural-information hypothesis or establish compiler
benefit.** Several weaknesses were real. Some were corrected earlier; the tuning
boundary warning had not been adequately addressed before this audit.

The separate AI supervisor independently confirmed the boundary warning, then
hit a usage limit before completing its methods report. This document is the
coordinating assistant's self-audit, with additional numerical verification. It
is not a completed independent supervisor review or external human peer review.
See [review status](REVIEW_STATUS.md).

## Undertraining: three different questions

**Insufficient optimization time:** not supported for these implementations.
The original dense ridge fits use direct Cholesky solves; the later ridge/kernel
paths use SVD/eigendecomposition. There are no epochs to extend. This agrees with
the pinned [Ridge](https://scikit-learn.org/1.8/modules/generated/sklearn.linear_model.Ridge.html)
and [KernelRidge](https://scikit-learn.org/1.8/modules/generated/sklearn.kernel_ridge.KernelRidge.html)
documentation. Original-grid predictions were reproduced exactly, and 36 selected
extended-grid target fits agreed with separate sklearn implementations to a
maximum 1.27e-8 in log prediction. See
[models.py:18](../validation_gate_2026-11-13/models.py#L18).

**Insufficient examples or domain coverage:** still plausible. The fitted dataset
has 125 task configurations and 19 related parent/motif groups. Hundreds of
thousands of physical shots improve labels; they do not create that many distinct
input graphs. The learning curves add program families, sizes and sometimes noise
coverage as well as quantity. They do not uniquely diagnose underfitting.

**Inadequate model, representation or tuning:** unresolved in general. Direct
optimization can accurately solve a poor modeling problem. Larger training/test
gaps can reflect overfitting or shift, while model bias and variance can coexist.
We should not have described underfitting as established from a learning curve.

Decoder BP iteration limits are a separate issue: the BP30/BP100 comparison
changes decoding work and potentially corrections, not predictor training time.

## Confirmed weaknesses and their status

| Issue | What the evidence establishes | Status and affected conclusion |
|---|---|---|
| Initial motif grouping | Single and repeated CNOT motifs can implement the same ideal map while occupying different original folds. No duplicate physical-shot leakage was identified. | Earlier interpretation of ideal-program holdout was too strong. Later fits merge these labels and audit parent equivalence. Generalization remains limited. |
| Approximate graph feature | `two_step_mean` samples fixed row IDs and changes under detector relabeling. | Confirmed representation weakness; excluded from the later stable feature comparison. Original full-feature results remain tests of that imperfect representation. |
| Tuning boundaries | All 31 RBF graph16 p95 fits chose minimum alpha; 29 also chose minimum gamma. | A real adequacy warning that should have been checked earlier. The bounded diagnostic below narrows, but does not exhaust, this concern. |
| Repeated development use | Later features, model classes and policies were considered after earlier outcomes. | Nested tuning protects a particular fit, not the entire evolving research process. All current outcomes remain development evidence. |
| Consumer selected late | Equal-TICK candidates, diagnostic budgets and an admission table preceded an established real decision contract. | Adequate for mechanism/prediction exploration, insufficient for a compiler-benefit claim. |
| Cost scope | Profiling savings excluded required preparation, warmup, label acquisition, caching and possible joint quality work. | Partial replay costs are valid within that boundary; they do not establish total savings. |

The first two issues were already documented in the
[earlier numerical review](../review/assessment.md). A metadata merge also caused
the original analysis script to stop before fitting; its versioned correction
did not change the observations or model specification. See the
[implementation amendment](../ANALYSIS_AMENDMENT.md). That was a real code error,
but not evidence that incorrect fitted results survived the correction.

## Bounded repair of the tuning concern

The [diagnostic protocol](GRID_DIAGNOSTIC_PROTOCOL.md) was written after detecting
boundaries and before fitting. It expands the grids symmetrically for all six
linear/RBF feature comparisons, preserving the same nested group splits,
training-only scaling, centering, targets, weighting and inner-selection rule:
alpha 1e-8 through 1e6; gamma multipliers 1e-4 through 1e2. No new circuits,
decoder samples, physical timings or reserved parents were used.

There were 372 outer-model evaluations: 186 original-grid reproductions and
186 expanded-grid evaluations. This is inspected-data sensitivity, not a new
independent test. Smaller error factors are better; one is perfect.

| p95 evaluation | Original density8 | Original graph16 | Expanded density8 | Expanded graph16 |
|---|---:|---:|---:|---:|
| Original groups | 1.03077 | 1.07649 | 1.04032 | 1.08577 |
| Fixed-noise parent holdout | 1.03970 | 1.05093 | 1.04002 | 1.04275 |
| Mixed-noise parent holdout | 1.04216 | 1.05755 | 1.04184 | 1.05561 |
| Inspected bridge | 1.09400 | 1.13334 | 1.10282 | 1.14615 |

The search restriction mattered: fixed-noise graph error improved noticeably.
It did not reverse these aggregate p95 comparisons, and some outcomes worsened.
A wider search lowers the selected inner validation loss but need not improve
outer performance; selection variance is a known issue
([Cawley and Talbot](https://jmlr.org/papers/v11/cawley10a.html)).

Expanded graph p95 fits still hit both new lower bounds in all 12 fixed-noise
folds and ten of 12 mixed-noise folds. We therefore cannot call the graph family
fully optimized. We stopped at the declared diagnostic boundary rather than
searching until a desired ranking appeared.

The mean-runtime signal also needs caution. Mixed-noise graph prediction retains
an exploratory advantage, but its inspected bridge mean error changes from
1.05270 to 1.07870; base6 RBF remains 1.07351. Thus one previously favorable
bridge mean ranking is sensitive to the tuning procedure. There is still no
demonstrated useful placement choice beyond the constant burst baseline.

## Does the comparison fairly test extra information?

The base is already strong: counts, sparsity and expected detector activity
contain information about the incidence matrix and noise. This is a test of
**additional selected summaries**, not structure versus no structure. See
[common.py:63](../validation_gate_2026-11-13/common.py#L63).

Adding coordinates to an isotropic RBF changes its distance metric. Graph16
does not automatically contain the density8 kernel as a zero-new-coordinate-
weight special case. This prevents a broad conclusion that the extra information
itself is useless. A feature-weighted kernel or another representation is an
untested model, not a correction we can assume will win.

We performed an additional arithmetic-only check using the saved inner losses:
allow the learner to choose density8 or graph16 within each outer training fold,
separately for each target, with ties favoring density8. This baseline-containing
selector uses no outer errors to make the choice and requires no new fit.
It chooses density8 for p95 in all 31 folds under **both** grids. It matches
the base p95 scores. It mostly chooses graph16 for mean latency, whose utility
and transfer still remain unproven. See
[the explicitly post hoc amendment](FEATURE_FALLBACK_AMENDMENT.md).

This is one valid feature-family selector, not a test of every architecture or
every weighting of structural information. It addresses forced use of the
augmented family without pretending to exhaust the information question.

## Design limitations that remain

**Precision, tails and context.** Old labels pool 6,000 shots, discovery labels
768, and bridge evaluation 1,536. Their precision differs. Earlier checks found
median ordinary p95 interval widths of about 1.26% and 8.95% for old/discovery
labels, and substantial rare-shot contributions to some means. The bridge's
median simultaneous-reference p95 interval width is about 5.05% of its estimate;
one case has a 3.92 maximum/minimum session p95 ratio. That variation could reflect
finite-sample tail behavior and/or context; the ratio alone does not prove drift.
Small model-score differences require uncertainty analysis rather than a binary
claim of superiority. The existing precision sensitivities are documented in
[the earlier assessment](../reviewer_perspective_2026-11-13/assessment.md).

**Training and evaluation weights.** Fits minimize configuration-weighted squared
log loss, while inner/outer reports average absolute log error equally over groups.
This is a legitimate declared choice, not a solver bug, but it does not isolate
sample quantity, represent a measured consumer workload, or establish optimal
weighting for unequal parent populations. Training-cohort and label-noise effects
remain mixed with domain coverage.

**Timing scope.** Warmup, fixed threads, randomized blocks/settings and three fresh
processes are useful controls. They do not control every host effect or make
shots IID. Original serial batches and later interleaved blocks also differ in
cache/service context. The bridge remeasures references and exposes some context
variation; it does not establish portability to a new machine or a shared pool.
See [bridge.py:119](../validation_gate_2026-11-13/bridge.py#L119).

**Censoring.** One discovery task, `q4_P03_d9_w18_p0_001_spread`, stopped at 681
observations and is excluded from the 125 complete-target dataset. Avoiding a
naive population quantile from stopped samples is correct, but the retained
dataset omits a difficult case. No all-task scaling conclusion follows from
complete cases alone. The bridge has no censored task. The resource cap is not
a native per-call decoder timeout.

**Uncertainty and repeated looks.** Binomial/order-statistic intervals are
conditional on the declared stable-context/IID model. Quality and timing are
separate interval families, not one joint 95% system guarantee. Thousands of
overlapping learning-curve fits do not create independent evidence. The empirical
maximum inner underprediction margin is not a calibrated shift certificate.
See [analyze_bridge.py:7](../validation_gate_2026-11-13/analyze_bridge.py#L7).

**Retrospective choices.** The quality screen and finite point-best candidate use
evaluation outcomes. They support a diagnostic ablation, not an available planner
oracle. Point regret is not necessarily a resolved population order. The analysis
script was implemented after timing started, although the protocol preceded
measurement and the note records that case outcomes had not been inspected.
A future confirmation study should freeze and dry-run its analysis before data.

**Quantum scope and benefit.** Single-sector logical-Z correctness and valid
correction vectors are useful checks. They do not establish full Pauli logical
accuracy, arbitrary-state circuit correctness, memory admission or reaction-time
feasibility. All bridge pairs have matched TICK counts, and burst is point-best
in all eight pairs. The experiment cannot demonstrate the quantum scheduling
benefit originally envisioned from those comparisons.

## What remains reliable, and what I would correct

Existing physical replay, matrix/correction checks and independent numerical
reproductions support the reported measurements in their restricted scope.
No new fatal implementation or split/preprocessing leakage defect was identified
in the examined final pipeline. Checksums establish preservation, not scientific
truth. Passing those checks cannot eliminate the limitations above.

I should have inspected tuning boundaries before treating the model comparison
as settled enough to motivate a broad research-direction recommendation. The
right statement is: **the tested summaries have not demonstrated incremental
p95 or compiler-decision value under these exploratory protocols.** Neither
underfitting nor the general uselessness of topology has been established.

The negative consumer gate still has a narrower valid meaning: the proposed
profiling workflow lacks a justified consumer/cost contract. A better predictor
would not by itself supply that contract. Historical construction/label-cost
illustrations do not prove all possible implementations uneconomic, and the
retrospective qualified subset does not certify production eligibility.

## Next steps after this review

1. Preserve this audit as a methodological addendum and use the corrected narrow
   claims. The bounded grid diagnostic and baseline-family fallback are complete;
   extra epochs are not the next experiment.
2. Bring the updated evidence to a human decoder/architecture researcher to
   identify one consequential decision and representative accessible workload.
   A specific model-transfer benchmark remains a candidate, not a salvage paper.
3. Only if that problem is established, design one prospective comparison with
   balanced program-level coverage, a baseline that can ignore extra features,
   justified boundary handling, target precision appropriate to the decision,
   appropriate quality/timeout accounting and full cost controls. Freeze one
   deployable model/selection recipe before genuinely new program families.
4. If that contract cannot be obtained, stop expanding the current branch. If
   it can, choose fresh-test size from the required effect and uncertainty;
   avoid interpreting a small pilot as a general reliability certificate.

No further grid expansion, new decoder run or reserved-parent trial was launched.
The numerical audit checks 372 outer evaluations, 36 separate sklearn target
fits, 12 arithmetic feature-selector summaries, and all 15 prior snapshots.
See [diagnostic_audit.json](diagnostic_audit.json). A complete new independent
supervisor review remains unfinished because of the reviewer usage limit.
