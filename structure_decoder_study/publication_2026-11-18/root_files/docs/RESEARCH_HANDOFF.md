# Research handoff: purpose, evidence and route toward publication

Prepared18 November2026. This is the current synthesis for a new collaborator.
It is a research-management document, not a manuscript or external preregistration.
AI expert/supervisor reports in this repository are internal AI reviews.
The scientific/runner baseline is commit
`b50ada1564336572c9aea1b95f835c66b8377408`; this handoff adds documentation,
not new experimental evidence.

## 1. What we are trying to achieve

The user wants an academically worthwhile, publishable result connecting
quantum error-correction decoding with practical computation constraints.
We began with compiler-facing cost prediction. The current working direction
is narrower: understand a specified decoder's failures on one accessible task,
then determine whether a mechanism-targeted intervention offers useful new
knowledge or an accuracy/cost improvement.

A specific-task paper can be legitimate. It does not need a universal decoder
or a demonstration across unrelated codes. It does need a clearly new finding,
strong relevant baselines, accurate accounting and evidence beyond the two
already inspected failures. Publication cannot be guaranteed.

We have a reproducible testbed and diagnostic findings. We do not have a
demonstrated new decoder improvement or an established novel paper claim.

## 2. Why the project changed direction

The original question was whether inexpensive structure predicts decoder cost
better than problem volume, dimensions, sparsity and expected activity. It was
motivated by an acknowledged volume-model approximation in PACE and the need
to distinguish the proposal from scheduling/latency work such as Triage.

The experiments found cost variation, but did not establish a useful, robust
incremental benefit from the tested additional graph summaries. Ordinary
decomposition was itself an important control. Follow-up reviews examined
training adequacy, held-out splits, stronger baselines and deployment overhead.
A compiler-facing decision benefit was not established.

Consequently, the positive structural-predictor/compiler framing is on hold.
Do not revive it merely because the repository retains that historical name.
See the original study README, findings and dated status/review files for the
restricted corpus and detailed negative/conditional evidence.
Relevant starting points are the
[learning-curve checks](../structure_decoder_study/learning_curves_2026-11-13/README.md),
[external-review perspective](../structure_decoder_study/reviewer_perspective_2026-11-13/README.md)
and [methods audit](../structure_decoder_study/experimental_design_review_2026-11-16/METHODS_AUDIT.md).

The user then proposed studying one concrete task and fixing a diagnosed failure
mechanism. This is the present research direction. Initial framework scouting
considered Anderson/DIIS acceleration of belief propagation, but generic related
methods already exist and our saved data do not contain the message trajectories
needed to diagnose oscillation or justify that intervention. It remains an
unimplemented conditional idea, not a contribution.

## 3. The current task and data

The task is source-matched BB[[144,12,12]] memory,24 rounds, circuit-level
depolarizing noise p=.007 and the existing **Z-check-only** schedule. It is not
a full-Pauli, both-sector memory benchmark, logical gate or compiler experiment.

- Generator source: UCL-CCS/Adaptive-qLDPC, pinned commit
  `8cc32014a6461bb8f241f47f62a7e74f63817738`.
- Decoder implementation used in this branch: ldpc2.4.1, with Stim1.16.0;
  relevant numerical environment includes NumPy2.4.1 and SciPy1.17.0.
- Detector matrix H:1800 rows by12240 fault columns, rank1794.
- Logical matrix L:12 observed logical rows.
- Natural development set:512 circuit-noise observations, two256-shot seeds
  2026111731 and2026111732.
- BP20+OSD0, BP30+LSD0 and BP100+LSD0 each returned500 correct outcomes and
  the same12 syndrome-valid logical failures.

For a correction x, Hx=s modulo2 checks detector consistency; Lx equals the
observed logical target only for a logically correct correction. A valid
syndrome does not prove logical success. BP nonconvergence also does not by
itself prove failure of the complete BP+postprocessing decoder.

The512 observations have been inspected and are development data. They cannot
become an untouched test set through a new random split or renamed seed group.

## 4. What the known search actually established

An initial Python search attempt stopped on a baseline-equality gate caused
by implementation-specific ordering ties. That run remains stopped. A separate
ordering diagnostic matched all24 selected cached native baselines. A separately
frozen adapted known1FV search then operated on the saved orders.

The selected panel contains all12 failures and12 fixed success controls.
The complete search used10446 free-variable candidates plus the baseline per
case. It rescued10/12 selected failures and regressed none of those12 controls.
K500/K1000 corrections matched full-search corrections on this panel, but their
latencies were not independently measured.

This uses an existing search method, not a new decoder. Do not report a new
2/512 error rate: the other488 originally successful observations were not
searched. Selected control behavior is not a population regression estimate.

Evidence: [known search](../structure_decoder_study/headroom_cached_order_2026-11-17/RESULTS.md).

## 5. The two remaining failures and the scientific unknown

Cases131 and228 remain logically wrong after that search. All24 saved lists
contain the observed correct logical class. For the residual failures:

| Case | Correct-class members | Best correct-class score | Wrong winner score | Gap |
|---|---:|---:|---:|---:|
|131|13|553.62914089|520.87671051|32.75243038|
|228|370|474.48544531|450.11581400|24.36963131|

Lower score wins. The source surrogate is S(x)=sum log(1/p_i)x_i with frozen
float64 channel-prior coefficients. It is not silently interchangeable with
Bernoulli log-odds, a full circuit posterior or logical-class probability.
The gaps are far above numerical tolerance; tie handling does not explain them.
Class counts are list multiplicities, not posterior probabilities or coset mass.

The diagnosis is **correct class present but not selected in this finite list**.
This does not prove the likelihood model is wrong. A class can be represented
without having a competitive representative in the list. Stochastic ambiguity
can also produce errors even under optimal inference.

The unresolved question is whether an outside-list correct-class representative
can beat the CURRENT full-1FV wrong winner under the SAME frozen score.
Improving the saved correct-class candidate while still losing to the wrong
winner does not answer that question.

A post-hoc finite-list bound also ruled out rescuing these cases by simply
aggregating exp(-S) over these same lists. It says nothing about complete coset
probabilities. Do not repeat that particular aggregation as an untested new idea.

Evidence: [class diagnosis](../structure_decoder_study/candidate_class_diagnosis_2026-11-18/RESULTS.md),
[finite-list bound](../structure_decoder_study/candidate_class_diagnosis_2026-11-18/FINITE_LIST_BOUND.md).

## 6. Why optimizer and runner work appeared

An oracle-assisted parity MILP was introduced as a diagnostic reference, not a
deployable decoder. It knows the observed correct logical target. The full
model has12240 binary fault variables and1812 integral parity slacks,14052
integer variables in total. It retains all H/L equations and the original score.

Only an independently checked competitive vector can provide one-sided
constructive evidence. No returned witness means INCONCLUSIVE. Numerical dual
bounds, optimal status or infeasible status do not establish exclusion here.
The known correct-class feasible vector makes real-model infeasibility a
backend/formulation error. A correct-class witness also would not prove that
the correct class globally beats every other wrong class.

Two real optimizer starts with a60-second solver limit returned no usable Python result; a raising
SIGXCPU handler interrupted the return path. Signal origin remains unknown.
Their recorded elapsed runs were about62 seconds, not exactly60.
Later engineering work repaired raw persistence but exposed resource/exit-
accounting assumptions. A subsequent native entry stopped after one valid toy
because ps emitted unsupported `?E`. That failure remains failed.

The latest stdlib runner now uses one exact-owned-PID wait4 reaper for final
status and per-child usage, with ps only interim telemetry. It passed32 fake-only
checks,12 physical process controls, independent audit and AI postreview.
It adds zero optimizer calls. This core has **not yet been integrated and
validated with the optimizer adapter**.

Do not spend indefinitely polishing infrastructure. The remaining integration
should have a bounded engineering exit criterion. The earlier native logs had
no incumbent around60 seconds on both real cases; repeating identical settings
has low expected new scientific value even with perfect result transport.

## 7. What could become a paper

Candidate framing, conditional on new evidence:

> On this declared circuit-derived memory task, identify a recurring decoder
> failure mechanism and demonstrate a distinct intervention or explanatory
> finding with a useful accuracy/computation tradeoff.

Three possible outcomes must remain open:

1. A justified intervention improves fresh same-task outcomes at a measured cost.
2. A new, well-supported mechanism or limitation is itself informative enough
   for an explanatory/measurement paper, with prior work and scope handled carefully.
3. The mechanism/method reduces to known work or has no useful effect: reject
   that framing rather than inflate the contribution.

Neither a runner fix, two repaired witnesses, known1FV recovery, nor the
coverage/selection taxonomy alone establishes novelty. Tentative venue-fit
planning can help scope the contribution and evidence early; do not promise
acceptance or treat a target venue as proof the result is sufficient.

## 8. Evidence required before a publication claim

- State the mechanism and a falsifiable prediction before choosing a complex
  method. Saved final outputs cannot establish BP oscillation or trapping dynamics.
- Check the proposed contribution against the closest current primary sources
  before substantial implementation. Record exactly what is already known.
- Separate development/oracle diagnosis from deployable inference: a practical
  method cannot require the true logical answer.
- Freeze a candidate method and tuning process before fresh confirmation.
  Use whole new natural-noise streams on the same declared task, not only
  successful rescue examples or cherry-picked hard cases.
- Use paired comparisons on identical observations. Count invalid corrections,
  logical failures, rescues and regressions. Prespecify uncertainty/precision
  needs and a finite resource/stopping plan; rare errors may require more shots
  than a small pilot can justify.
- Compare against strong applicable baselines, including relevant known search
  methods and meaningful extra-compute controls. A weaker iteration setting
  alone is not an adequate baseline.
- Include setup, feature extraction, routing, search and decoding costs where
  relevant. Distinguish amortized/offline work from online latency and report
  tail behavior only with adequate independent evidence.
- Run mechanistic controls/ablations and deliberate failure tests that can
  disprove the explanation. Treat undertraining, overfitting, selection leakage,
  representation choices, floating ties and platform effects as hypotheses to
  check, not automatic explanations.
- Use additional codes/noise/schedules only when making corresponding transfer
  claims. A narrow same-task claim can be valid without universal generality.

## 9. Prior-work leads, not a fresh novelty clearance

Historical reviews identified Adaptive-qLDPC as close task/search prior and
Logical-Space Theory of OSD as prior for coverage versus selection. Quimb
already exposes DIIS-related BP machinery; later feedback/acceleration work
also makes generic acceleration a high-risk novelty framing. A peer-reviewed
quantum trapping-set study motivates mechanism-led investigation.

Start with the citations and qualifications in
[task-specific decision](../structure_decoder_study/framework_search_2026-11-17/TASK_SPECIFIC_DECISION.md)
and the accompanying expert/supervisor notes. These are historical leads.
Recheck accessible primary publications, exact versions and current related
work before asserting novelty. Initial PACE/Triage references motivated the
old proposal; they are not proof of novelty for the current task-specific route.

## 10. How to use this repository

The public mirror is curated, not a complete portable archive of the original
host workspace. Installed binaries/environments, private publication state and
specified unlicensed upstream helper snapshots are omitted. PUBLIC_EXPORT.json
lists exported bytes/exclusions; THIRD_PARTY.md explains helper provenance and
the optional pinned-file restoration tool. Exported numerical arrays, including
the saved search data, are byte-preserved. The public progress verifier does
not repeat the full250,728-member audit; that does not imply its saved arrays
are missing. Check availability and provenance before promising
full raw reanalysis or fresh circuit generation. Some measurements, such as BP
message trajectories and separate prefix-search timings, were never captured.
Old host-specific freezes are not portable execution configurations.

The [ledger](EXPERIMENT_LEDGER.md) distinguishes evidence stages. The
[next task](NEXT_TASK.md) is the immediate bounded engineering handoff.
Use the public verifiers for sanitized archive integrity. Preserve original
failed protocols and create new versioned outputs. The source/testbed is useful
groundwork, but the scientific hypothesis and publication claim still need work.
