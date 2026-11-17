# Completed AI supervisor methods review

17 November 2026. Separate AI reviewer; not external human peer review. I read
the latest audit, diagnostic protocols/results, saved choices and critical code.
I ran no fits, decoder calls or physical samples and changed no frozen artifact.

**Judgment:** the new diagnostics substantially address the simple undertraining
concern and leave the restricted numerical results credible. They do not establish
optimal tuning, a general negative result about structural information, or a
publishable compiler method. A scoped empirical validation paper remains a
credible possibility, with unverified novelty. I recommend a manuscript prospectus
as the next bounded deliverable, rather than another model campaign.

## What the new diagnostics repair

The fitting path computes ridge via SVD and kernel ridge via a centered-kernel
eigendecomposition. Training-only scaling, target centering and held-parent
inner selection are implemented coherently in
[models.py:18](../validation_gate_2026-11-13/models.py#L18)
and [models.py:77](../validation_gate_2026-11-13/models.py#L77).
These solves have no epoch budget to extend. Optimization-time undertraining is
not a credible explanation for the reproduced fits. Data scarcity, model bias,
inappropriate representations and regularization remain different questions.

The grid expansion is symmetric across compared models, retains the old splits
and uses inner outcomes for selection. The implementation reproduces original
predictions and inner losses, then checks selected expanded solutions against
separate sklearn fits. The saved maximum discrepancy is about 1.27e-8 in log
prediction. I found no new obvious split, centering or candidate-ordering defect
in these inspected paths.

The result matters: fixed-noise graph p95 error factor improves from 1.05093 to
1.04275; density8 is 1.04002. The restriction therefore affected the comparison,
but the aggregate ranking did not reverse. Small differences at this scale
should not be described as statistically settled superiority.

The fallback calculation is also coherent: it compares saved inner losses,
breaks ties toward the base and evaluates the corresponding saved outer output
([feature_fallback.py:32](../experimental_design_review_2026-11-16/feature_fallback.py#L32)).
Choosing density8 for p95 in every outer fold under both grids is additional
evidence against a useful improvement from these particular summaries and
families. It is not a test of every structural representation or weighted kernel.

## What remains unresolved or needs narrower interpretation

1. **Tuning saturation remains open.** Twenty-two of 31 expanded augmented p95
   fits still select both new lower bounds. Widening once was a sensible bounded
   diagnostic; calling the model class fully optimized would still be incorrect.
   Further search is not automatically warranted without a scientific claim.
2. **The effective dataset is small and structured.** There are 125 task-level
   examples and 19 related groups, not half a million independent graphs.
   Added-program curves also change domain coverage. Their improvement does not
   uniquely prove underfitting, nor do overlapping fits create independent trials.
3. **Several earlier mistakes were genuine and appropriately scoped.** Original
   motif grouping was weaker than ideal-program holdout; one approximate feature
   depended on row identity. Later merging/stable descriptors repair those tests.
   The metadata-merge failure stopped before fitting and was versioned. None is
   evidence that all later measurements are invalid.
4. **Precision and context limit model-ranking claims.** Unequal target sample
   counts, rare expensive shots and session-sensitive quantiles remain relevant.
   Stable-context/IID reference intervals are not hardware-shift or system-level
   guarantees. The censored difficult case restricts complete-case scope.
5. **Current comparisons are development evidence.** Repeated feature, model,
   target and policy choices preclude treating this artifact as untouched final
   confirmation. The fallback and grid expansion are correctly labelled post hoc.
6. **The base contains structural information already.** Sparsity and expected
   activity depend on the incidence matrix and priors. The supported question is
   incremental value of selected summaries, not structure versus its absence.
7. **Scope is a publication constraint.** Single-sector CPU service and a
   retrospective quality screen do not establish full-Pauli FTQC feasibility.
   Equal-TICK candidates and the constant-burst baseline defeat the present
   learned quantum-scheduling-benefit story.

The consumer gate reasonably stops the **selective-profiling speedup proposal**.
It should not become a universal veto on empirical model validation. A paper
can contribute a meaningful benchmark or modeling-limit result without claiming
end-to-end compiler acceleration. Historical construction and training-label
cost arithmetic also does not prove all future implementations uneconomic.

## One bounded next deliverable

**Write a four-page results-first manuscript prospectus from the existing
artifact, within two working days and with zero new decoder shots.** Suggested
working title: *Generalization of CPU Decoder-Latency Models on Circuit-Derived
QEC Tasks*.

Its candidate contribution is an explicitly scoped comparison of out-of-program
transfer for volume, sparse/activity and selected graph-summary models, with
uncertainty and sensitivity to validation design. It must not advertise a new
decoder, structural necessity, calibrated deployment safety or quantum speedup.

Require three concrete research questions, three existing-data figures, a
claim-to-evidence table and a primary-source comparison. The natural questions
concern what cheap information predicts, what transfers across programs/noise,
and which apparent differences survive precision/tuning/context checks. Mark one
independent-program confirmation panel as **missing**, rather than filling it
with inspected data. Identify the smallest fresh validation needed for that
specific scoped claim; do not choose a large corpus or a universal reliability
target by habit.

The novelty paragraph must distinguish quantitative predictive-validation
knowledge from [PACE's acknowledged volume extrapolation](https://arxiv.org/html/2608.11719v1),
[LSD runtime characterization](https://arxiv.org/html/2406.18655v2), and
[Triage's stochastic calibration](https://arxiv.org/html/2605.04459v1).
Those precedents motivate the question but do not establish our priority.
A measurement/benchmark workshop paper is a plausible category, not an acceptance
prediction or evidence that the current draft is submission-ready.

**Abandon this paper path** if the prospectus reduces to known runtime variation,
generic noise shift, a practically unused dataset, or a negative graph-feature
ranking without a consequential model-validation question. If it forms a distinct,
useful scoped result and the missing confirmation is feasible, freeze one
confirmation protocol and evaluate it once on genuinely new programs. If that
does not support the prespecified claim, release the technical record and stop.
Human domain feedback can improve that draft, but is not a substitute for writing
the concrete argument now.
