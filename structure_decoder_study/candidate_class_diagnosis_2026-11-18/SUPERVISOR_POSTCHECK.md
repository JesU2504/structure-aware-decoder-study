# Independent AI supervisor postcheck

18 November 2026. Review of the preflighted code, protocol, primary results, process records, adapter outputs and completed independent audit. This is internal AI review, not human peer review. The reviewer ran no decoder, reconstruction, candidate calculation or new experiment. This new report leaves frozen artifacts unchanged.

**PASS for the declared offline diagnostic.** No material remaining design or execution error is apparent within its scope. The two operational weaknesses identified before freezing were fixed and documented in `PREFLIGHT.md`; they did not affect a completed scientific run. This result narrows the failure classification but establishes no new decoder or publishable mechanism.

## What the evidence establishes

All 24 saved lists contain at least one candidate in the observation's correct logical class. The preserved source selection succeeds on the same 22 cases as before: ten previously rescued failures and twelve controls. The remaining two are correct-class-present-but-not-selected cases, with robust score gaps:

| Case | Correct-class members | Best correct-class score | Best competing-class score | Correct minus competing |
| --- | ---: | ---: | ---: | ---: |
| 131 | 13 | 553.6291408940 | 520.8767105141 | +32.7524303799 |
| 228 | 370 | 474.4854453120 | 450.1158139978 | +24.3696313142 |

Lower score is preferred. These gaps are much larger than the frozen numerical tolerance. Neither residual failure is a cross-class numerical tie. The two cases therefore do not fail because this particular candidate list omits every correct-class correction.

This is a samplewise classification under the unchanged source surrogate and list, using a known coverage/selection framework. It is not a discovery of that framework or evidence that all failures on the task share this classification.

## Design and execution review

- The frozen plan SHA256 is `e92d012a723ca89ac24ab0f3b54bd97d99f4602ad4472e6aa8a1cd05269cd211`; primary and audit process records agree. The audit verified frozen inputs and 22 earlier result manifests.
- Both processes completed normally with exit 0, no watchdog cause and no monitor error. Primary used 4.666 CPU seconds and 5.016 child-wall seconds, peak child RSS 490,422,272 bytes. Audit used 14.375 CPU seconds and 14.733 child-wall seconds, peak 218,595,328 bytes. Controller-wall measurements differ slightly because they include process supervision. No limit censored the results.
- Algebra, logical-code round-trip and source-choice adapters passed, as did the three watchdog probes and eleven exit-classifier cases. No model was trained; undertraining is not a variable in this diagnosis.
- The independent audit checked all 250,728 list members, including 24 baselines, against all 1,800 H rows and 12 L rows, complete weighted-vector scores, per-class summaries, source selection and reported margins. The source winners remain unchanged.
- Maximum direct-score discrepancy was approximately 1.71e-12. The audit found 175 within-class minimum-representative index differences under an alternative floating summation order. The protocol explicitly allowed these when saved-score representative identity and independent numeric minima agree within tolerance. These are not new source winners or evidence of logical-class ambiguity. No case has a numerically sensitive true-versus-competing class margin.
- No new decoder call, physical sample, search candidate, score intervention or fit was performed. Offline use of true observables classified existing outputs; it did not select a repair.

The primary and audit use different class calculations: cached affine algebra versus explicit full vectors and independent packing. They share the declared inputs and numeric conventions, so this is a substantial implementation crosscheck rather than independent physical validation.

## What does not follow

A present correct class can still have a poor available representative. These results do not establish incorrect likelihoods, missing physical noise correlations, a defect in the code, intrinsic uncorrectability or a dynamical BP failure. An optimal probabilistic decoder can also be wrong on an individual stochastic observation. Counts of constructed candidates are not posterior probabilities.

Additional representatives might improve the correct class or its competitors. Merely covering more logical classes is not the observed missing resource in these two lists. AA, deeper search, changing priors or a class-probability method is not automatically justified by this diagnosis. There is no new 2/512 error rate or population improvement estimate; this remains an inspected, selected development panel.

## Optional post hoc algebraic implication

The root proposed a useful narrow deduction after seeing the results. If one simply aggregates the UNCHANGED finite-list surrogate weights `exp(-S(c))`, the true-class weight divided by the largest competing-class weight is at most

`n_true * exp(-(S_true_min - S_comp_min))`.

Each true-class summand is bounded by its minimum-score weight, while a competing class contains at least its best representative. For both cases the observed positive score gap exceeds `log(n_true)`, so the bound is below one. Simple aggregation of these existing surrogate list weights therefore cannot rescue either case.

I support reporting this only as a **post hoc mathematical addendum**, not a preregistered test, a performed decoder experiment or a new contribution. The source score is the declared `sum(log(1/p))` surrogate. This bound says nothing about unenumerated representatives, exact Bernoulli-weight rescoring, full logical-coset probabilities or the physical circuit posterior. No aggregation or rescoring experiment is needed to establish the stated inequality.

## Research decision

The authorized diagnosis is complete and suitable to report. It identifies a finite-list selection limitation, but no distinct actionable repair mechanism has yet been established. Keep the task-specific research possibility open while holding method/performance expansion.

One later bounded strong-reference diagnostic is scientifically reasonable before choosing an intervention. Its precise question is whether a correct-class correction OUTSIDE this list can beat the already selected wrong correction under the SAME score. This is different from claiming that existing candidates were misranked or changing their weights.

The smallest formulation minimizes the unchanged S subject to the observed H syndrome and the observed correct L class, separately for cases 131/228. It need not optimize every class. Given a validated upper/lower bound interval `[LB, UB]` for this constrained minimum and the existing wrong winner's score `S_w`:

- A feasible, independently parity/class/score-checked witness with `UB < S_w` beyond tolerance proves that a competitive correct-class representative is missing from the present list. It does not prove that the globally best correction, or a practical decoder, selects the correct class; another wrong class might improve too.
- A trustworthy lower bound with `LB > S_w` beyond tolerance proves that no correct-class representative can beat this known wrong candidate under S. This would expose a limitation of minimum-individual-error scoring on that observation, but still not diagnose physical model mismatch or the full logical-coset posterior.
- A straddling interval, unavailable valid bounds or a resource stop leaves the distinction unresolved.

**Entry condition:** use an already accessible, validated public optimization/certification framework with a finite predeclared case/resource budget, independently checked feasible vectors and an explicit guarantee for any lower-bound claim. A floating solver status alone must not be relabeled a rigorous certificate. This reviewer has not established such backend access or runtime feasibility. First check those prerequisites; if absent, pause rather than build a new certifier or start unbounded MILP. This is a known-method diagnostic, not the proposed publication novelty, and no such optimization is executed or approved by this report.

Before a larger performance campaign, require a specific implementable, label-blind intervention that differs materially from existing approaches, a fair strong baseline and a failure condition. If only known search or known finite-list selection remains, stop that proposed paper argument. Do not choose AA, generic rescoring or a larger benchmark automatically.

A later claim confined to this BB144 task could use fresh same-task confirmation; cross-family transfer and compiler benefit remain optional claims. This successful diagnosis does not establish the novelty or useful effect needed for that later paper.
