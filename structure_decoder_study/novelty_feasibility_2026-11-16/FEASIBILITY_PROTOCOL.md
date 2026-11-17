# Existing-data feasibility check

16 November 2026. This is a post hoc engineering/novelty screen, using only
previously inspected development outputs. No decoder calls, model fitting,
new hyperparameter choices, or new physical samples are performed.

Evaluate the inherited nine-budget sweep and frozen RBF density8 predictions
on all nineteen bridge configurations. Preserve whole-task logical-Z eligibility
as the existing retrospective diagnostic, not a deployable accuracy oracle.

Compare uniform profiling, the previously proposed raw/padded deadband gate,
and a mandatory simple model-as-filter control: reject if the raw estimate
exceeds the budget; otherwise profile and accept only if the stored profiling
p95 upper bound fits. The latter never accepts without a profile, but may reject
feasible tasks. It inherits only the profiling procedure's explicitly conditional
reference confidence interpretation, not arbitrary noise/hardware-shift safety.

Report the admitted sets, confirmed false admissions, confirmed conservative
rejections, unresolved truths, profiling counts, and quality-screened counts.
Use the same saved evaluation intervals for every policy. No policy is selected
as a fresh-test winner from these data.

Cost scopes are distinct: recorded profiling decode wall service; recorded
profile-initialization wall time; and recorded median density-feature/inference
time. The latter is one computation per task, not three. Their sum is a partial
replay cost, not full compilation latency. Shared circuit/DEM/matrix preparation,
warmup, model-training amortization, and differences in artifact demand remain
unmeasured. Calculate the additional exclusive-overhead allowance before savings
disappear, conditional on the same prepared-DEM input batch. Do not replace
unmeasured costs by a claim of zero cost.

Also calculate the minimum fixed sample count for a finite one-sided upper
order-statistic bound on p95 under the stated IID/stable-context model. This is
not a sample-size guarantee of useful precision or a deployment certificate.

The purpose is to decide whether an independent experiment is technically
worth designing, and whether simple controls remove any rationale for a more
complex profiling gate. The nineteen configurations and repeated contexts
remain development evidence.

## Development-only amendment: simpler frozen predictors

After inspecting the RBF-density replay, also replay the same filter-and-validate
rule with all six already frozen linear/RBF predictors. This asks whether a
cheaper linear predictor already explains the opportunity. Report all models
and budgets; do not select a model or tune a cutoff for a future test using this
comparison. No additional features are timed, models fitted, or decoder calls
made. Graph-feature timings use their previously recorded full-stable timing.
