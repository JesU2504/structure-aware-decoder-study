# Next-stage research design

16 November 2026. Design after the novelty/feasibility audit. This file does not
authorize a final statistical claim, describe completed experiments, or reopen
reserved test programs. No decoder measurements or model fits were made while
preparing it. Earlier protocols and snapshots remain unchanged.

## The question we should pursue conditionally

Can inexpensive task information reduce the **total cost of characterizing
decoder service time**, while retaining the decisions a specified compiler
actually needs?

The next step is to establish that this is a consequential problem. The current
partial saving is 1.838 seconds across 19 tasks; that alone is insufficient.
We will not make graph features, nonlinear learning, or unprofiled acceptance
part of the proposed contribution. An established method transferred carefully
to a new domain can contribute, but must demonstrate a useful result and its
failure boundary. The existing [novelty assessment](../novelty_feasibility_2026-11-16/assessment.md)
remains the source of the literature positioning.

The provisional consumer is an **offline compiler characterizing candidate
TCNOT schedules for a pinned CPU decoder**. This is a hypothesis about a useful
workflow, not an implemented PACE integration or demonstrated user demand.
[PACE](https://arxiv.org/html/2608.11719v1) motivates schedule-dependent decoding
and DEM preparation; it does not establish our characterization overhead or
require our proposed policy.

## Stage 0 — consumer and cost contract: the immediate work

**Bound: one or two working sessions, with existing files and public sources.
No new parents, fits, or decoder timings.** Complete the accompanying
[consumer_contract.json](consumer_contract.json). Record source evidence for
each real requirement and label hypothetical parameters explicitly.

1. Specify what the planner must return: one feasible schedule, the best feasible
   schedule for a quantum objective, or a useful table/frontier of candidates.
   These require different baselines. Do not choose a complete table merely
   because profiling every task makes our method look better.
2. Establish the number of **unique uncached** tasks per invocation, the frequency
   of new tasks, cache invalidation, and realistic model/calibration reuse.
   Repeated use of the identical DEM should not be charged a fresh profile.
3. Specify the input boundary. The primary compiler-facing cost should start at
   candidate schedules and include circuit/DEM/matrix preparation. A secondary
   prepared-DEM result may isolate characterization, but must be labelled as such.
   Our current features already require H and the priors: the filter cannot
   retroactively save their construction cost.
4. Derive the service budget and permitted miss probability from the consumer.
   Separately state logical quality and how the planner obtains it. Our old
   2 ms, 5% timing-tail and 1% logical-Z settings are diagnostics, not requirements.
5. State the value of avoiding characterization, and the cost of rejecting a
   feasible candidate. If only one feasible schedule is needed, establish how
   often a simple fixed-order search already finds it cheaply.
6. Define minimum worthwhile absolute and relative savings **before** new timing.
   A provisional research-management screen is 20% net saving, but the absolute
   requirement and reuse horizon must come from the consumer. Twenty percent
   is not a publication standard or a significance threshold.

The deliverable is a one-page contract with provenance and a missing-cost ledger.
We have recovered the following historical facts without new measurements:

- The complete six-model, 186-outer-fit job logged 5.463 seconds. This is neither
  a deployment linear-fit time nor the cost of obtaining its training labels.
- Its training set has 125 configurations from 19 groups. Label acquisition,
  target-context calibration and fitting/tuning must be distinguished.
- The earlier 19 bridge predictions came from different parent-held-out fits.
  They are not a single deployable model. A future model must be fitted and
  frozen explicitly rather than treating these predictions as that artifact.
- Preparation, sampling, warmup and deployment pipeline overhead are not
  separately recoverable from the existing profile totals. Whole-session
  elapsed time includes other decoder settings and evaluation; it cannot be
  assigned to characterization by assumption.

**Gate 0:** advance only with a concrete consumer, a justified decision contract,
and a plausible route to material net savings. If these cannot be established
within this bounded investigation, stop this publication direction and preserve
the current work as a technical record. Do not enlarge the workload until the
percentage looks attractive. Current status: **not ready to advance**.

## Stage 1 — measure the real cost on existing development tasks

This stage is conditional on Gate 0. Use existing inspected tasks; reserve fresh
parents. Freeze the instrumentation and task-selection rule before timing.
Choose at most six old tasks spanning low, middle and high recorded service
cost, with deterministic selection and ties, and include an already cached task.
Select within the consumer's admissible scope, not by a new favorable result.

Measure the actual pipeline from its stated boundary through the returned
decision. Record both total elapsed wall time and a non-overlapping ledger:
startup/imports; circuit and DEM preparation; matrix conversion; feature
extraction; inference; sampler creation and sampling; decoder initialization;
warmup; timed profiles; decision and required output/cache I/O. Audit-only
checks and research artifact storage are separate research costs unless required
in the intended deployment. Retain CPU time, memory diagnostics and all failures.

Count common work in both policies' total latency, even when it cancels in an
absolute difference. Report cold start, amortized reuse and cache hits separately.
Charge the data acquisition and calibration actually needed by the proposed
model. Do not charge all research exploration to one deployment, and do not
declare a pretrained model free without showing its provenance and transfer cost.

All policies receive the same legitimate caches and warm-service convention.
The uniform baseline should use an efficient implementation; it need not repeat
three decoder initializations merely because our old study had three processes.
Separate **profiling required by one invocation** from **repeat invocations used
to assess measurement variability**. Randomize policy order over three isolated
repeat sessions; do not run fitting and decoder profiling concurrently.

The minimal candidate learner is log-linear ridge with base6, trained on the
unchanged 125-row development dataset. Select its p95-target alpha with equal-
parent leave-group-out error using the existing nine-value grid; fit the final
scaler and coefficients on that development set. Freeze the payload and domain
before fresh data. This training recipe is proposed, not executed. No graph
model, new grid or architecture search is needed for this gate.

Evaluate these controls, with the same cost boundary and statistical rules:

| Control | Why it is necessary |
|---|---|
| Exact-task cache plus efficient fixed-size profiling on misses | Avoids treating repeated characterization as unavoidable. |
| Measurement-only classification with predeclared checkpoints | Tests whether obvious early stopping explains savings without a predictive model. |
| Joint timing/quality observations, when qualification requires decoding anyway | Prevents charging the baseline extra for timing data it obtains during required accuracy checks. |
| Frozen linear filter followed by that same profiler | Isolates the value of task information; every admission must be profiled or come from a valid cache entry. |
| Fixed-order profile-until-feasible search, when only one schedule is required | Avoids comparing a one-answer consumer against an unnecessarily complete table. |

For a best-feasible objective, include the appropriate cheap objective ordering
and search stopping rule; for a table, evaluate retained coverage. Keep the
historical fixed-192 profiler only as continuity evidence if the consumer requires
a different sampling plan. A cache key must include task/DEM and priors, ordering,
decoder configuration and binary, and the declared hardware/service context.
Changed contexts invalidate applicability according to a frozen rule; a matching
hash alone does not guarantee performance stationarity.

For a learned filter, a prediction above budget means **discarded by model**,
not statistically certified infeasible. It can save cost by losing useful tasks;
that loss is an endpoint. Unsupported contexts fall back to measurement or
abstain; marginal feature ranges are not a distribution-shift certificate.

**Gate 1:** require material savings after full accounting against the strongest
applicable simple control, with the agreed useful output retained and no hidden
reliance on unprofiled acceptance. Examine all declared consumer operating points,
including points where savings vanish. If caching, efficient profiling, or a
fixed search removes the advantage, retire the learned-selector claim. A useful
measurement-only result can be reconsidered separately; it is not an automatic
paper salvage. Recover missing costs by this bounded measurement, rather than
extrapolating the old partial ratio.

For recurring equivalent batches, report
`net_saved(R) = R * (baseline_batch_cost - proposed_batch_cost) - extra_upfront_cost`.
If the difference is nonpositive there is no break-even reuse. Use only a justified
R and the measured cost of the applicable cache-miss mix. Do not multiply an
uncached saving across identical cached invocations.

## Stage 2 — a small prospective feasibility pilot, only after both gates

Before opening new programs, write a separate immutable execution protocol with
all contract values, task-generation seed, group split, payload, policies,
sampling plan, resource cap, metrics and analysis script hashes. A local hash
is an integrity record, not external preregistration. The present design is
conditional and is not that execution freeze.

A reasonable *size illustration* is eight genuinely new program families with
two placements and two consumer-justified noise settings: 32 tasks. This is not
permission to generate them now or a requirement to manufacture that factorial
if it misrepresents the consumer. Check disjointness from all existing groups
under qubit relabeling and relevant program equivalences. All layouts, distances,
noise variants and relabelings of one family stay in the same split. A different
name or physical shot seed does not make a new program family.

Keep one pinned decoder and hardware context initially. Use three separated,
randomized sessions as descriptive context replicates. Do not count sessions,
layouts or millions of shots as additional independent program families.

Freeze proposed decisions before consulting independent evaluation streams.
Use explicit namespaces for warmup, acquired profiles, planner-available quality
evidence and final evaluation. Quality and timing may deliberately share the same
physical observations when the consumer permits joint measurement; record that
sharing and charge each call once. Any stopping rule must retain valid bounds
for both endpoints. Warmup and final evaluation remain disjoint from decision-making
observations. Every task receives independent
evaluation, including model-discarded tasks; otherwise feasible rejections cannot
be discovered. Report this evaluation as research cost rather than secretly
charging it to the deployment policy. Actual end-to-end runs must demonstrate
that skipped profiles really avoid construction/warmup work where claimed.

Report:

- Total characterization cost and absolute saving, cold and amortized, compared
  with the best applicable simple control. Use ratio of aggregate costs under
  the contract's weights, not the unweighted mean of favorable task ratios.
- Useful feasible output retained: certified admission coverage for a table,
  or feasibility/objective regret and search cost for a selected schedule.
- Timing violations among admitted tasks, unresolved timing labels, model
  discards, quality violations, and quality-unknown cases. Publish ambiguous
  cases separately; do not call them correct or erase them.
- Per-parent and per-session results, full cost components, cache behavior,
  and budget regions where the method offers no advantage.

For this diagnostic pilot, a gate can require the declared material saving in
each reference session and no observed loss of reference-certified useful
outputs. This is an engineering screen, not a proven population noninferiority
claim. Do not tune the filter after viewing a pilot family and then describe
subsequent analysis of that family as prospective.

## Statistical design: decide at the budget, expose uncertainty

If the consumer asks whether `P(T > B) <= rho`, measure that exceedance rate
directly. Estimating an entire runtime curve is unnecessary for this decision.
Logical failure and timing failure are distinct outcomes. If late decoding is
itself an application failure, also report their joint/union failure on the
appropriate physical shots; do not multiply separate marginals as if independent.

A simple measurement-only policy uses cumulative sample checkpoints, for example
64, 128, 256 and 512 per task/context. At each permitted look use an exact
binomial interval: accept if its upper endpoint is at most rho, reject if its
lower endpoint exceeds rho, otherwise continue. At the cap return **unresolved**.
Use a preallocated error budget across tasks, contexts and looks; do not repeatedly
apply an ordinary fixed-sample 95% interval without correction. Exact binomial
construction is documented by [NIST](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).
Time-uniform alternatives exist in [Howard et al.](https://arxiv.org/abs/1810.08240),
but a new sequential-inference method is unnecessary for this project.

One illustrative family allocation is alpha 0.02 for all profiling statements,
0.01 for logical quality, and 0.02 for independent timing evaluation. For K tasks,
H contexts and J profiling looks, use two-sided interval alpha `0.02/(K*H*J)`
per profiling cell; independent fixed evaluation uses `0.02/(K*H)`. Quality uses
`0.01/(K*H)` at its fixed endpoint. The two tails split each cell's alpha equally.
Policies reusing the exact same intervals do not create new interval families;
additional independently measured policies, budgets, endpoints or experiments
must be accounted for. A simultaneous quantile bound reused over thresholds
does not require pretending each threshold is an independent measurement.
These allocations cover the declared experimental family or bounded invocation,
not an indefinite lifetime of new tasks and contexts.

The exact calculations in [planning_calculations.json](planning_calculations.json)
show why blindly carrying over old sample counts would be a mistake. Under the
illustrative 32-task, three-context, four-look allocation and rho=5%:

- At least 206 zero-miss observations are needed for even a possible acceptance
  at a profiling checkpoint. A 192-shot profile would not suffice under this
  allocation, even with no misses.
- With 4,096 independent evaluation samples per task/context, the probability
  of resolving a true 3% miss rate as feasible is about 99.7%; resolving a true
  7% rate as infeasible is about 96.0%. At 512 samples these probabilities are
  only about 2.9% and 3.6% under the same family error allocation.
- A zero-failure quality bound below an illustrative 1% needs at least 982
  observations per task/context. A stricter actual FTQC requirement can make
  straightforward simulation infeasible; do not substitute 1% merely to pass.

These are conditional IID/stable-context planning calculations, not predictions
of observed behavior or a guarantee that a real workload lies 2 percentage points
from the boundary. Near rho, uncertainty may remain unavoidable. Within-process
correlation and changing machine load can invalidate simple binomial coverage;
inspect context/block behavior and narrow the claim if the assumptions are not
credible. Three repeat contexts do not establish arbitrary hardware robustness.

For the illustrative 32-task case, 4,096 evaluation samples in three contexts
mean 393,216 evaluation calls, plus at most 49,152 acquired-profile calls for one
four-look timing policy and its warmup/setup. If the planner needs a separate
fixed 1,024-shot quality qualification for each task/context, that adds 98,304
calls; if qualification and timing share calls, count them once and use a valid
joint/stopping design. Required quality evidence may dominate cost or provide
timing observations almost for free. This can remove the selective-timing use
case, and is a reason to stop rather than artificially separate the costs.
Independent policy timings can add more.
Choose the actual counts and a global CPU/wall cap only after the contract and
Stage 1 cost estimate. If the cap is reached, retain the data, mark the run
incomplete/censored, and do not claim the planned precision. Do not drop hard
tasks or continue collecting until a desired result becomes significant.

## Failure tests we must preserve

| Potential failure | Planned check and interpretation |
|---|---|
| Savings come from a weak baseline | Cache, efficient profiler, measurement-only stopping and consumer-appropriate search controls. |
| Features require most of the expensive preparation | End-to-end schedule boundary plus separately labelled prepared-DEM result. |
| Training/labels cost more than the saving | Cold-start and justified reuse calculation, including target calibration. |
| Favorable threshold or candidate mix was chosen after seeing results | Contract-derived primary operating points; preserve the full predeclared sensitivity range and empty-admission cases. |
| Model discards the best feasible schedule | Independent evaluation of discarded candidates; objective regret or table coverage, as appropriate. |
| Timing success occurs only at poor logical quality | Separate quality-qualified and quality-unknown output; never use final evaluation as an available planner oracle. |
| Required accuracy checks already supply timing data | Permit joint observations and valid shared bounds; charge each physical decode once. |
| Noise shift changes cost with unchanged H/L | Predeclare a supplementary noise-shift stress on already inspected parents; report separately from representative new-family validation. |
| Tail or host-context changes break profile interpretation | Context/block diagnostics, conservative unresolved labels and explicit fallback; no arbitrary-shift certificate. |
| Related circuits leak across groups | Program/canonical-equivalence audit and group-level splits before timing. |
| Repeated samples inflate generalization evidence | Program family is the unit for cross-program conclusions; sessions and shots answer different questions. |
| More training or architecture changes are used to rescue failures | Keep one frozen linear recipe; any later redesign starts a new development cycle and needs new confirmation data. |

Do not add every stress dimension to the primary factorial. Test mechanism
failures on development parents first, keep a small representative pilot, and
expand scope only for a concrete unresolved scientific question.

## Stage 3 — publication decision and possible confirmation

An eight-parent pilot can expose failures and estimate engineering costs. It
cannot establish a small unseen-parent failure probability. Even zero failures
in eight independent representative families gives a one-sided 95% upper bound
of about 31.2%. With zero failures, 59 families are needed to bring that simple
bound below 5% for **one** endpoint; simultaneous requirements or observed
failures can require more. This is illustrative binomial arithmetic, not a
universal sample-size prescription or proof that generated families represent
all quantum programs.

After a successful pilot, choose a confirmation size from the actual claim,
effect, uncertainty and resource estimate. If pilot outcomes influence the
method, they become development data and confirmation uses fresh families.
Use parent-level inference for program generalization and report hardware-context
limits. A finite case study may support a narrower empirical statement; it is
not broad calibrated reliability. Do not automatically launch a 59-parent run.

A paper becomes worth pursuing if the result shows a consequential cost/useful-
decision tradeoff beyond the simple controls, explains its domain and failures,
and survives independent confirmation with full costs. A defensible empirical
contribution does not need a new model architecture. If the learned model adds
nothing, the table is unnecessary, or true costs erase the benefit, stop this
direction rather than restating a weaker result as the original contribution.

## Concrete execution order

1. Finish the consumer contract and missing-cost ledger; issue a written Gate 0
   decision. This is the next work, not a request for a large experiment.
2. Only if it passes, instrument the existing-task pipeline and strong controls;
   measure their actual costs and issue Gate 1.
3. Only if that passes, freeze a new pilot execution protocol and payload before
   generating or inspecting new parents.
4. Run and audit that bounded pilot; decide whether its result and statistical
   requirements justify an independently sized confirmation study.

Success at a gate is the scientific condition for preparing the next stage,
not evidence of novelty, hardware safety or publication acceptance. These are
research decisions, not additional user-permission requirements.
