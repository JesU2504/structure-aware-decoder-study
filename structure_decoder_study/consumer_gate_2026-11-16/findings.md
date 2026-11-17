# Completed consumer and cost gate

16 November 2026. **Stage 0 is complete and does not pass. Do not advance the
current selective-profiling workflow to Stage 1 timings or fresh-parent tests.**
This is a decision about the present evidence and proposed workflow, not proof
that selective characterization can never be useful.

The [contract assessment](contract_assessment.json) records each requirement,
its evidence and the unresolved conditions. No new decoder calls, physical
samples or model fits were made. This is a post hoc development analysis, not
external peer review or prospective validation.

## 1. A related systems problem is not yet our consumer

The closest scheduling work returns a feasible schedule optimizing a quantum
objective, whereas our fixture evaluates a table of 19 tasks spanning several
programs and noise settings. It is not an observed planner invocation. We have
no supported unique-task arrival rate, cache-miss distribution, reuse horizon,
absolute value of a second saved, or tolerance for feasible rejections.

The [primary-source check](source_check.md) distinguishes scheduling, live
admission, calibration and offline decoder choice. These are real consumers of
decoder information, but none was connected here to our proposed measurement
purchase policy. Circuit-generator access is established; an integrated decision
trace and its characterization-cost burden are not.

[PACE](https://arxiv.org/html/2608.11719v1) supplies a window-arrival budget and
aggregates decoding costs along a layered critical path. Applying its timing
formula at our distance would give 5 ms, but this is only a sensitivity inference:
our CPU configuration, whole-task logical-Z scope and specified p95/5% miss
allowance do not reproduce its execution contract. Per-task p95 values also do
not by themselves certify a multi-task critical-path deadline.

The earlier 2 ms point therefore remains illustrative. We cannot declare it a
real compiler requirement because it produces an attractive replay.

## 2. Accuracy eligibility substantially changes the favorable replay

The designated simple control remains the previously chosen frozen linear
base6 filter. It profiles a task only when its raw predicted p95 fits the budget,
and admits it only when the stored profile upper bound also fits. No new model
was chosen. All six frozen predictors and all nine old budgets are retained in
[replay.json](replay.json), including unfavorable results.

| Existing-data condition | Uniform profiles | Linear-filter profiles | Uniform partial cost | Filter partial cost | Same admitted set? |
|---|---:|---:|---:|---:|---|
| All 19 tasks, 2 ms | 19 | 12 | 3.088 s | 1.250 s | Yes, 5 tasks |
| Ten pilot-quality-qualified tasks, 2 ms | 10 | 9 | 0.952 s | 0.750 s | Yes, 5 tasks |
| All 19 tasks, 5 ms | 19 | 19 | 3.088 s | 3.089 s | Yes, 17 tasks |
| Ten pilot-quality-qualified tasks, 5 ms | 10 | 10 | 0.952 s | 0.952 s | Yes, 10 tasks |

Removing tasks outside the retrospective pilot accuracy screen reduces the
recorded 2 ms saving from **1.838 seconds (59.5%)** to **0.201 seconds (21.2%)**.
At 5 ms the filter adds overhead while profiling everything. The nonlinear
alternatives also profile every task at that point.

The ten-task subset uses the existing evaluation-derived 1% logical-Z screen;
it is neither a production oracle nor a full application accuracy requirement.
We did not retune the bound for a ten-task family. This sensitivity demonstrates
that the reported opportunity depends strongly on eligibility and candidate mix.
It does not demonstrate a deployable quality-aware selector or prove that all
excluded tasks are useless under every application contract.

Where a real consumer must collect fresh logical-quality evidence, those same
physical decoding calls may provide timing observations. A legitimate baseline
can reuse them with valid joint statistical accounting. Our current replay does
not charge that qualification work or establish the marginal timing cost after
it. An assumed separation of quality and timing would overstate savings.

## 3. Recoverable construction cost is substantial

The original 78-task corpus records circuit creation, DEM creation and conversion
separately. Median circuit-build time is **5.297 seconds**; the aggregate is
406.639 seconds. DEM generation totals 1.411 seconds and matrix conversion
1.290 seconds in that historical preparation run. The three exact bridge
reference circuits alone have recorded circuit-build time totaling **13.257
seconds**. These are observed old costs, not new measurements.

For illustration, adding just those three historical build costs to both sides
of the 19-task 2 ms ledger changes its percentage saving to 11.24%, even before
adding any build costs for the other sixteen tasks. This is **cross-context
arithmetic**, not a measured end-to-end speedup, a bound for an optimized compiler,
or a reason to assume the other construction costs are zero. Template reuse,
caching and a different circuit builder can change the common preparation cost.

The important result is that our features require the prepared matrix/priors,
so skipping a timing profile does not recover construction already performed.
The prepared-DEM characterization percentage cannot stand in for a compiler
speedup. The original metadata additionally records 0.383 seconds of decoder
initialization and 0.919 seconds of measured sample generation across 234 runs;
warmup is outside those sampling measurements. Those older measurements do not
fill the missing bridge end-to-end ledger.

## 4. Learning cost includes obtaining labels

The 125 training examples represent **504,096 physical samples** and **630.720
seconds of recorded decoder service**: 471.319 seconds from the original 78
tasks and 159.402 seconds from 47 discovery tasks. These numbers were checked
against 375 raw timing files. They exclude preparation and other acquisition
overheads. They are not the minimal amount of data needed to train a useful
filter; the extensive experiment was not an optimized deployment training set.

If one charged only that historical label-service time against the old 1.838-
second partial batch saving, repayment would require 344 equivalent uncached
batches. This is an illustrative historical accounting scenario, not a measured
deployment break-even or a claim that every implementation needs those labels.
Warm-start use of genuinely reusable existing labels is a different scenario.
We have no measured consumer reuse horizon for either case.

The earlier 5.463-second model-job time is consequently insufficient as the
entire learning-cost ledger. It measures the fitting/evaluation job, not the
cost of producing suitable timing targets or recalibrating a new context.

## 5. Caching and search remain necessary controls

Three bridge circuits are byte-identical to circuits in the old corpus. This
identifies possible reuse; it does not prove that the old timing context remains
applicable. A real profile cache must specify its validity and invalidation.
Counting all repeated tasks as fresh characterization would be unjustified.

A planner needing one feasible schedule must also be compared against a simple
search that stops after finding one. A complete admission table is not automatically
its required output. We did not manufacture a new planner or treat unrelated
programs in this fixture as alternatives for a single quantum computation.

## Decision and next disposition

The negative gate follows from several missing or mismatched requirements,
not solely the provisional 20% screen. No consumer-derived absolute-value
threshold has been established. The existing favorable signal is small in
absolute terms, sensitive to quality and budget, and incomplete in cost scope.
These facts do not justify the next experiment specified in the staged plan.

**Close the current profiling expansion.** Preserve the data, negative results,
protocols and source positioning as a technical research record. Do not enlarge
the corpus, train a richer predictor, or begin reserved-parent timing to rescue
this branch. The original graph-p95 improvement claim remains unsupported.

Reopen only with a concrete decision trace or qualification workflow, sourced
service/accuracy requirements, and a credible material cost case after caching,
joint observations, preparation and model/label amortization. No external messages
were sent. This gate does not determine whether an entirely different, properly
supported decision problem could justify a paper.

## Work checked after analysis

[audit.json](audit.json) independently verifies 108 replay rows using raw profile
costs and bounds, reconstructs quality eligibility from independent evaluation
outcomes, traces training-label service through 504,096 samples, checks exact
circuit reuse, and verifies all nine previous snapshots unchanged. This establishes
numerical/provenance integrity, not generalization or the statistical assumptions.
The final claim check also preserves every important qualification: retrospective
quality selection, diagnostic budgets, partial costs, historical cost contexts,
unknown cache validity, and a scoped do-not-advance decision.
