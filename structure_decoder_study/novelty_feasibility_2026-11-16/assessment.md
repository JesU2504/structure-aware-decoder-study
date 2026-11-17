# Novelty and feasibility assessment

16 November 2026. This assessment combines a primary-source literature check,
a separate AI review, and a replay of existing development measurements. The
reviewer is not an external human supervisor. No new decoder calls or model
fits were made. This is not an exhaustive priority search.

## Judgment

**The engineering is feasible; a publishable contribution is still uncertain.**
The generic method of acquiring measurements only when they improve a decision
is established. A carefully evaluated transfer to decoder characterization could
still contribute useful new knowledge. The narrow QEC application has not been
verified as novel, and our present measurements do not establish material value
or prospective reliability.

The original claim that connection-pattern summaries improve p95 prediction
beyond strong size/noise/nonlinear controls remains unsupported by the frozen
validation results. Selective characterization is a different research question,
not confirmation of that hypothesis. More training alone does not settle either
novelty or usefulness.

| Question | Current assessment |
|---|---|
| Is selective information acquisition a new method? | No. There is explicit database precedent. |
| Is decoder timing/accuracy calibration before resource decisions new? | No. There is direct QEC precedent. |
| Is the precise offline selective timing-profile/admission workflow already demonstrated in the inspected QEC methods? | Not identified in this focused search; novelty remains unverified. |
| Can we implement a simple prototype with the existing tools? | Yes; a replay already runs without new dependencies or hardware. |
| Have we shown worthwhile total savings and reliable decisions on new programs? | No. |
| Should we start a large paper experiment now? | No; first establish a consequential consumer and full cost case. |

## What is already known

The proposed transfer should be attributed explicitly. The following sources
constrain the claim; the separate [QEC audit](qec_prior_art.md) gives a fuller
input/target/measurement/decision comparison.

| Primary source | Established idea and relevance |
|---|---|
| [Seppi, Barnes and Morris, 1993](https://pubsonline.informs.org/doi/10.1287/ijoc.5.4.410) | Bayesian query optimization buys additional samples when their expected decision benefit exceeds their cost. The generic measurement-value idea is old. This conclusion follows from the publisher abstract; we do not claim to have reproduced the full algorithm. |
| [Wu et al., 2014](https://arxiv.org/abs/1408.6589) | Query-time prediction includes uncertainty in estimated selectivities and machine costs. Prediction uncertainty is an established performance-modeling concern. |
| [Progressive optimization, 2004](https://research.ibm.com/publications/robust-query-processing-through-progressive-optimization) | Execution checkpoints test estimates and can trigger reoptimization. This is an analogy for checking assumptions, rather than the same offline acquisition policy. |
| [SATzilla component study, 2012](https://www.cs.ubc.ca/labs/algorithms/Projects/SATzilla/SAT12-EvaluatingSolverContributions.pdf) | Instance features, their acquisition costs, and portfolio decisions have longstanding precedent. A graph-feature selector alone would need stronger justification. |
| [PACE](https://arxiv.org/html/2608.11719v1) | Compiler-facing decoder cost modeling and feasibility already exist. Its acknowledged extrapolation boundary motivates investigation, but does not establish our improvement. |
| [Delfosse et al., 2023](https://arxiv.org/html/2310.15313) | Measured runtime and logical-failure distributions inform offline decoder, distance, and stopping-time decisions. Merely measuring timing and accuracy is insufficient differentiation. |
| [DART-Q](https://arxiv.org/html/2605.09142v1) | Decoder admission is studied using a live queue/backlog cap. This limits broad admission novelty; the inspected methods do not optimize offline purchases of candidate timing profiles. |
| [Scalable testing of QEC](https://arxiv.org/html/2602.04921) | Adaptive QEC simulation allocation already exists for logical-error estimation. Its target differs from service-time characterization. |

A combination of established components can support a paper. The contribution
would need to be a demonstrated QEC-specific result: when measurement selection
reduces meaningful characterization cost, what it preserves, and where it fails.
Renaming a known technique or applying it once is weak evidence. We found no
inspected method demonstrating precisely the proposed loop, but cannot claim
that none exists or that we would be first.

A candidate hypothesis is:

> For a specified task family and pinned CPU decoder, cheap task information can
> reduce pre-execution timing-characterization cost while preserving useful
> service-budget admissions at a stated statistical risk and logical quality.

This remains a hypothesis. It does not require a new ML method or structural
features. It concerns offline task characterization, distinct from selecting a
decoder for an already observed syndrome or controlling a live queue.

## Feasibility replay and its strongest counterexample

We reused all 19 inspected bridge configurations from seven parent groups,
their frozen predictions, and disjoint stored profiling/evaluation streams.
Each complete profile contains 192 timing observations over three processes.
The admission test uses the saved one-sided upper bound for p95. The inherited
2 ms budget is a diagnostic, not a hardware-derived requirement.

| Policy at 2 ms | Tasks profiled | Admissions | Recorded partial cost |
|---|---:|---:|---:|
| Profile all tasks | 19 | 5 | 3,087.996 ms |
| Linear base6 filter, then profile every proposed admission | 12 | Same 5 | 1,249.990 ms |
| RBF density8 filter, then profile every proposed admission | 11 | Same 5 | 1,266.322 ms |
| Earlier raw/padded deadband gate | 10 | Same 5 | 1,231.079 ms |

The linear filter rejects a task when its frozen predicted p95 exceeds the
budget; otherwise it buys a profile and accepts only if that profile's upper
bound fits. It achieves the same admissions here with slightly less recorded
cost than RBF density8, despite profiling an additional task. This undermines
any current need for a nonlinear selector. These six-feature inputs include
noise/activity information; this is not a size-only baseline.

The deadband saves only 18.911 ms beyond the linear filter in this comparison,
while accepting one task without a profile. Its historical padding is not a
valid prediction interval. There is no current evidence justifying that extra
acceptance mechanism.

The linear filter's partial saving is about 59.5%, but only **1.838 seconds** for
the entire batch. Profiling everything is already cheap at this scale. A large
percentage alone does not establish a problem worth solving. We cannot multiply
these numbers into an unmeasured large-distance or production speedup.

The full nine-budget sweep is retained in [feasibility.json](feasibility.json).
At 4 ms and every larger tested budget, the RBF-density filter profiles all 19
tasks, adds its own overhead, and saves nothing. At 0.25 and 0.5 ms it profiles
nothing and admits nothing. At 1 ms it profiles/admits only the memory task.
The favorable region is therefore strongly dependent on the budget and candidate
mix. These observations are development diagnostics, not a fresh-test success.

At 2 ms the policies in the table have no confidently identified timing false
admissions. Their common admitted set consists of five cases passing the
retrospective logical-Z screen. Uniform profiling still rejects four cases
confidently within the timing target, including one passing that quality screen;
one other case has unresolved evaluation timing truth. Thus matching uniform
profiling does not mean achieving all useful admissions. The screen is based on
evaluation data and is not an available production quality oracle.

## Costs, statistics, and operating domain

The table adds saved timing-call wall service, saved profiling initialization,
and previously recorded median feature/inference time once per task. It replays
the actual three-process profiling arrangement; it does not measure a newly
optimized single-process profiler. Feature/inference measurements also come
from their earlier timing context. Circuit/DEM/matrix preparation, warmup,
training/calibration amortization, and policy-specific artifact demand remain
unaccounted for. These are partial costs, not compilation speedups.
For the base6 control we conservatively charge the available base/density
feature timing, rather than invent a smaller unmeasured base6 extraction cost.

Under a common prepared-DEM input assumption, the linear filter's recorded
advantage would disappear after 1.838 seconds of additional exclusive overhead
for this batch. Shared preparation may cancel in the absolute difference while
reducing the percentage saving. For a learned method with initial extra cost
T, a conditional reuse calculation is T divided by the net saving per future
batch, provided that future saving is positive and actually reproduced. Reuse
over changing hardware/noise contexts can require recalibration. We have not
measured a favorable break-even point.

Two uncertainties must be separated: the variation of runtime across physical
syndromes, and uncertainty in our estimate of its tail. Model error and
hardware/noise shifts add further uncertainty. A 192-shot profile is not an
exact p95; a conservative upper bound can be much higher than its point
estimate. Under an IID, stable-context model, at least 59 fixed samples are
needed for even the maximum observation to give a finite 95% one-sided p95
upper bound for one task; a Bonferroni family of 19 requires 116. These minima
ensure a finite bound, not useful precision. The additional sample-count rows
in the JSON illustrate larger families; multiplying by nine budgets is only a
conservative illustration for separately covered statements, and is unnecessary
when one simultaneously valid quantile bound per task is reused across budgets.

Timing observations within a process can be dependent, and three processes do
not establish robustness to machine contention, drift, or a different decoder.
Any future fixed-sample confidence claim must justify its context model.
Adaptive stopping requires an appropriate sequential procedure or a frozen
error-spending scheme. We have not implemented or validated one here.

Profiling every proposed admission avoids unprofiled model acceptance, but does
not certify arbitrary shift, logical accuracy, queueing deadlines, or FTQC
execution. A p95 service target permits a 5% tail; that is not a quantum logical
error requirement. Our present scope is CPU BP+LSD whole-task logical-Z service,
not full Pauli decoding, accelerator behavior, or a deployable quantum reaction
time. A concrete consumer must justify its actual service contract separately.

## Recommendation and bounded next gate

**Continue the inexpensive use-case/cost check; do not start a large experiment
or write a positive paper claim yet.** The separate AI review agrees that the
prototype is feasible but current publication evidence is weak.

Spend one bounded working session defining a concrete planner: its candidate
counts, real budgets, characterization frequency, reuse horizon, cost of a
feasible rejection, and required logical quality. Recover existing cost data
where available and list any remaining measurement requirements. Compare
uniform profiling with the frozen linear filter plus validation, retaining
budgets where filtering has no value. Do not make graph features or a complex
acquisition rule prerequisites.

Proceed to a small prospective experiment only if this identifies a consequential
workload and credible net savings. Before opening new parents, freeze the task
distribution, budgets, cost accounting, useful-admission requirement, risk
criterion, and stopping rule. Use independent evaluation streams, contextual
replicates, and program-level splits; all current cases are development data.
Any richer method must improve on the linear filter, and reported savings must
include characterization/setup and training amortization. Matched statistical
risk and useful admissions matter alongside cost; rejecting everything cannot
count as success.

Stop this publication direction if complete accounting removes the advantage,
the consumer cannot justify the contract, or simple baselines already provide
the intended benefit without a new domain result. Preserve the benchmark and
negative findings as a technical record. A successful transfer paper remains
possible; neither the literature search nor this replay establishes one.

## Verification

[audit.json](audit.json) verifies all seven prior manifests unchanged, the
profiling cost and upper bound against 57 raw stored files, all nine budgets,
and 54 frozen-model filter controls. This checks replay integrity, not the
statistical assumptions or future generalization. Earlier artifacts were not
edited. The QEC audit and this report are local research notes, not peer review.
