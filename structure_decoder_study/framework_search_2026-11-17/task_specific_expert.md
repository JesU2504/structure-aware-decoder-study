# Expert assessment: a focused task-specific decoder study

18 November 2026. Internal AI research review, not external human expert review.
Read-only review of existing artifacts and primary literature. No decoder call,
candidate enumeration, model fit, new sample or manuscript was produced.
This new advisory addendum does not modify the prior frozen proposal or manifest.

**Yes: studying one legitimate decoding task, identifying a failure mechanism,
and improving that task can be a valid research contribution. A cross-family
claim is not required. The claim must generalize to unseen observations of the
specified task, rather than merely repair two inspected witnesses.**

## Academic positioning

Mechanism-guided decoder work is an established research category. In the
peer-reviewed [Trapping Sets of Quantum LDPC Codes, Quantum5,562(2021)](https://quantum-journal.org/papers/q-2021-10-14-562/),
the authors classify harmful graph configurations and use that understanding
to improve finite-length decoding. This supports the proposed scientific
workflow; it does not establish novelty of our particular mechanism.

Specific-code decoding is also a recognized systems topic: IBM's official
[Decoding the gross code](https://research.ibm.com/publications/decoding-the-gross-code)
is listed as a QCE2024 workshop paper. The [gross-code FPGA prototype](https://arxiv.org/html/2510.21600v1)
specifically targets BB144 memory. The latter is a preprint in this source,
not an acceptance guarantee for a software-only study.

A narrow noise mechanism can supply the contribution: [Maximally-Matched Mixture
Decoding for Correlated Atom Loss](https://arxiv.org/html/2610.38283v1) focuses on
Gross-code circuits and exploits loss correlations. This is another preprint,
and its noise channel is not our present depolarizing benchmark. It illustrates
mechanism-specific scope, not evidence that arbitrary tuning is publishable.

The distinction is therefore contribution and evidence, not simply number of
codes. A strong narrow study may explain a new failure mechanism, introduce a
useful task-specific algorithm, establish a meaningful accuracy-cost advance,
or reveal a consequential modeling limitation. A renamed existing technique
or a lookup repair for two known syndromes supplies none of those by itself.

## One concrete task

Use the already accessible source-matched **BB[[144,12,12]],24-round,
p=0.007 circuit-level depolarizing-noise Z-check-only memory task**. Pin the
existing public generator commit8cc32014a6461bb8f241f47f62a7e74f63817738,
the exact schedule/noise assumptions, detector/logical matrices and priors, and
the single-threaded BP20+OSD0 reference configuration. Score whether any of the
twelve true logical-Z observables is wrong for the entire observation window.

This task is legitimate, reproducible on available CPU resources, and already
has verified failures. The source extracts only Z checks; do not present the
task as a full two-sector memory experiment, logical gate or compiler workload.
p=0.007 is the declared operating point, not evidence for lower-noise teraquop
performance or an error-floor claim. We have not established access to a
corresponding logical-gate workload and do not need to invent one for this scope.

There is a particularly close prior: [Adaptive decoding through decoder
disagreement](https://arxiv.org/html/2609.37629v1) already uses BB144,24rounds
and p=0.007, with BP20+OSD0 and one-free-variable search. It already demonstrates
repair headroom and risk-guided search on this task. Our ten observed rescues
therefore remain reproduction/feasibility evidence. Narrowing to this task
does not remove that prior or establish a new contribution.

## Diagnose first; choose the intervention second

Do not commit to Anderson acceleration. The present two residual failures do
not establish a dynamical defect. Use a neutral hierarchy:

| Question | Diagnostic meaning | Possible next direction, conditional on evidence |
| --- | --- | --- |
| Are inputs, conventions and outputs consistent? | Stale priors, tie order, precision or adapter errors can mimic a decoder mechanism | Correct and freeze the implementation before scientific interpretation |
| Does the saved candidate list contain any member of the true logical class? | Absence means the inspected list lacks that class | Investigate candidate generation/coverage; does not imply AA is useful |
| If the class is present, why is its best representative not selected? | Compare within-class minima, declared score, margins and deterministic tie rules | Investigate ranking/representation or objective, with all-outcome controls |
| Does BP stall, oscillate or converge to a valid wrong class? | Requires coherent per-edge trajectories; cached final LLRs alone cannot diagnose it | Only supported dynamical evidence motivates damping/DIIS/AA or other feedback |
| Is the noise model adequate? | Requires a separate factorization/calibration test; a failed sampled shot is insufficient | Investigate model mismatch only if independently demonstrated |

Coverage versus selection is already formalized in [Logical-Space Theory of
OSD](https://arxiv.org/html/2610.24503v1). Use and credit that framework rather
than claim its taxonomy as our invention. A true-class candidate losing the
score comparison does not prove that the score is statistically wrong: even
an optimal decoder can fail on an individual stochastic observation.
The finite list may also contain that class without a competitive representative.
Absence from1FV establishes absence only from that candidate family. If a later
intervention changes scores, compare the source log(1/p) surrogate against exact
Bernoulli log-odds log((1-p)/p) for the DECLARED independent DEM. That comparison
would not establish maximum likelihood for the full physical circuit or assume
a uniquely known physical fault support.

The logical matrix L is legitimate known decoder information. True sampled
observables and true fault supports are diagnostic/evaluation-only; they must
not choose candidate sets, perturbations or per-shot parameters at runtime.

## The smallest justified next task

Freeze one **offline audit of the already saved24 candidate sets**, covering
all twelve baseline failures and all twelve predetermined controls. Reuse the
existing baseline plus10446 candidates per case. Do not run a new decoder,
enlarge the search, change scores or try a proposed repair yet.

For each saved case, report candidate logical-class coverage, best declared
score per class, the true class's best score when present, selected-class margin
and tie sensitivity. Ask specifically whether131/228 lack any true-class
candidate or contain one that loses under the declared selection. Retain all
cases and distinguish genuine absence from incomplete/censored inspection.

This would classify an unknown mechanism in inspected development evidence;
it would not estimate the population prevalence of that mechanism or create
publication novelty. If the result merely recovers a known prior mechanism
without a distinct intervention or useful domain finding, stop that proposed
paper argument. Do not treat the result as an instruction to search until the
two cases become correct.

## Minimum design for a later task-specific improvement claim

1. **Development and confirmation:** use the current512 observations as
   development data. Choose the mechanism/intervention and freeze its parameters,
   baseline, candidate policy, cost metric and success criterion before opening
   a fresh natural-noise confirmation stream. Independent seeds of the SAME
   fixed task can test within-task generalization. New code families are needed
   only for a claim about transfer across families. New noise rates or schedules
   are required only to support the corresponding robustness claims.
2. **Natural outcomes:** evaluate every observation in each declared stream,
   including baseline successes and any new regressions. Do not select only
   failures, remove difficult shots, or deduplicate naturally repeated syndromes.
   Report paired rescue/regression counts, total logical failures and appropriate
   uncertainty. The selected24-case result is not a new2/512 error rate.
3. **Matched computation:** include the strongest same-task accessible baseline
   appropriate to the intervention, not only OSD0. Existing one-free-variable
   search and the published disagreement policy are especially relevant. Compare
   actual total CPU cost and accuracy, counting rejected work and fallback. For
   a dynamics intervention include fixed damping and extra-work controls; DIIS,
   TEMPO/Relay or other close methods become necessary according to the claim.
4. **Mechanistic attribution:** change one justified ingredient, preserve the
   noise and scoring model where appropriate, and use a same-budget ablation.
   Successful witness repair cannot substitute for improved population outcomes.
   Declare the mechanism's expected scope and concrete conditions under which
   it should fail.
5. **Precision and stopping:** select a finite sample/resource plan from the
   desired effect and paired discordance uncertainty, rather than assume512 or
   an arbitrary round number is sufficient. Insufficient evidence remains
   inconclusive. Do not keep sampling after every unfavorable result without a
   valid sequential rule. Freeze numerical adapters and retain all failed gates.

There is no neural training process in the existing solver. Finite iteration
and search budgets, model bias and hyperparameter selection still matter; a
matched-extra-work control addresses premature stopping more directly than
calling it undertraining. If learning is introduced later, separate training,
calibration and untouched evaluation and charge their acquisition costs.

## Verdict

**Go for one task-specific mechanism investigation.** The task is accessible
and the scope can be academically defensible. Revise the earlier blanket
untouched-program requirement: it applies to transfer claims, not every possible
narrow decoder improvement. Keep AA and other frameworks as conditional tools.

**No publication claim yet.** An exact-task prior already establishes known
search headroom, and the cause of our two residual failures remains unknown.
The next evidence should decide which mechanism, if any, merits an intervention.
