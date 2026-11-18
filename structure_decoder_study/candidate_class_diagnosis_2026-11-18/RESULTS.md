# Both residual failures contain the correct logical class

18 November 2026. Frozen offline diagnosis of the24 previously saved candidate
lists on the BB144/r24/p=.007/Z-check-only memory task. No decoder, noise,
candidate list, score, source selection or correction was changed.

**Both remaining failures are within-list selection losses: the saved list
already contains logically correct corrections, but the source winner belongs
to another class with a substantially better surrogate score. Neither is a
correct-class coverage miss in this particular list.**

| Case | Correct-class members in list | Best correct-class score | Best competing score | Correct-minus-competing gap |
| --- | ---: | ---: | ---: | ---: |
| 131 | 13 | 553.62914089 | 520.87671051 | +32.75243038 |
| 228 | 370 | 474.48544531 | 450.11581400 | +24.36963131 |

Lower score wins. These gaps are far above the declared numerical tolerance;
tie handling does not explain the two losses. All24 lists contain the observed
correct class, including the12 success controls and10 repaired failures. The
same22 source outputs are correct and the same2 are incorrect. No oracle-based
repair or new population-performance measurement follows from the diagnosis.

## What was computed and checked

The protocol and161 input files were frozen before real class computation,
SHA256 `e92d012a723ca89ac24ab0f3b54bd97d99f4602ad4472e6aa8a1cd05269cd211`.
Each list includes baseline index0 plus10446 existing ordered1FV candidates:
250728 members in total, including250704 nonbaseline candidates. Counts are
list multiplicities, not posterior masses. Absolute labels use the twelve
L rows in their authoritative order, rowi as biti.

Primary calculation used the saved affine candidate algebra. An independent
script imported no primary grouping or decoder helper: it rebuilt every full
vector, checked all1800 H equations and12 logical rows with int64 arithmetic,
recomputed direct scores and verified all class counts, minima, margins and
source winners. All4096 possible packed labels passed independent round-trip
checks. Baseline inclusion, zero-free-bit assumptions, positive/zero ties and
absent/no-competitor null semantics passed toy adapters.

The actual saved source selection remained authoritative, including its
strict-positive and first-maximum rules. Cached direct-score minima never
reselected a correction. The largest full-vector/cached-score disagreement was
1.7053e-12. For175 class minima, the identity of the raw minimum representative
changed under independent floating summation within tolerance; the prespecified
audit allows this and verified numeric minima rather than asserting a unique
representative. None altered the source winner or the two robust failure gaps.

The primary completed normally in4.666CPU/5.016wall seconds, peak490422272bytes
(467.70MiB). Independent verification completed normally in14.375CPU/14.733wall
seconds, peak218595328bytes (208.47MiB). Both stayed within their separate
600CPU/900wall-second/1GiB operational limits. All11 exit-classifier adapters
and three watchdog probes passed. No stop, abnormal exit or monitor failure
occurred. All22 previous result manifests remained unchanged.

## Mistakes caught before execution

The AI supervisor found two implementation issues before freeze: a handled
resource stop could be labelled only as an abnormal exit, and independent audit
iteration could silently truncate a malformed row list through zip. Resource
exceptions/status handling and an additional classifier case fixed the first;
explicit24-row/order/completion checks fixed the second. Reported selected
scores were also added to independent verification. These changes preceded
real diagnosis; no tolerance, case, score, code or budget changed after freeze.

The completed calculation and independent audit passed the supervisor postcheck.
This is internal AI review, not external human peer review.

## Meaning and limits

This establishes finite-list coverage versus selection for inspected observations,
using an existing diagnostic framework. It does NOT show that the scoring model
is wrong or that a different score would improve fresh-task performance. A
finite list can lack a competitive representative of a class it technically
covers, and stochastic ambiguity can make even optimal inference fail on an
individual observation. Full class optima and full class probabilities remain
unknown. No BP trajectories were observed here, so no oscillation, trapping set
or justification for Anderson acceleration follows.

The24 cases were selected development observations. The512 original observations
remain development data;488 originally successful observations have not undergone
the inspected1FV search. There is no new2/512 error rate or estimate of mechanism
prevalence. Coverage-versus-selection taxonomy is prior work, not our novelty.

A separate [post hoc bound](FINITE_LIST_BOUND.md) shows that summing exp(-S)
weights over these SAME lists also cannot make the correct class win for131/228.
It rules out one particular aggregation experiment, not full coset inference.

The next methodological choice must distinguish poor within-class representatives
from broader likelihood/degeneracy ambiguity; this diagnosis alone does not
justify changing BP, rescoring or expanding a search. Read the
[supervisor postcheck](SUPERVISOR_POSTCHECK.md) before proposing that next task.

Evidence: [frozen protocol](PROTOCOL.md), [preflight review](PREFLIGHT.md),
[independent audit](audit_result.json), [all24 summaries](case_summary.csv),
and per-case complete class tables under `cases/`.

Attribution: [Logical-Space Theory of OSD](https://arxiv.org/html/2610.24503v1)
already formalizes samplewise coverage versus selection; fixed-order distribution
formulas were not imported for our BP-dependent order. The
[Adaptive-qLDPC task and search](https://arxiv.org/html/2609.37629v1) remain the
close prior. No new method or publication claim is established by this audit.
