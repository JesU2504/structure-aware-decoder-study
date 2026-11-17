# Skeptical internal review and sensitivity diagnostics

13 November 2026. Requested after inspecting the completed learning curves.
This is a post hoc internal audit by the same assistant, taking a reviewer
perspective. No independent external reviewer, external preregistration, or
new decoder timing evidence is implied.

Review the scientific claim before running the proposed nonlinear comparison.
Check data precision, workload/cohort confounding, feature representation,
grouping, adaptive model selection, execution policy, decoder scope, logical
accuracy, useful decisions, overhead, and literature differentiation. Distinguish
observed defects, plausible untested alternatives, and scope qualifications.

For existing-data numerical diagnostics:

1. Verify all earlier manifest entries. Recover the 125 complete learning-curve
   configurations' raw latency arrays. Reproduce pooled mean/p95 labels.
2. Describe session-to-session target variation and ordinary distribution-free
   p95 order-statistic intervals, explicitly conditional on IID/stable-context
   assumptions. Individual label intervals wider than a mean model gain do not
   prove that the aggregate gain is absent.
3. Refit the declared learning-curve endpoint models with each session's own
   mean/p95 labels. These are sensitivity checks, not independent test datasets
   or nominal generalization confidence intervals. Old sessions have 2,000 shots
   per case and discovery sessions 256.
4. Repeat endpoint fits for ten predetermined equal-precision draws: randomly
   select 256 old shots without replacement from each of its three sessions,
   retaining all 256 per discovery session. Use deterministic seeds, unchanged
   feature sets and the same nested nine-alpha selection procedure. Existing
   data are reused and there is no claim that this removes hardware/cohort
   differences or creates independent training corpora.
5. Retain all three declared feature variants and both targets. Examine original
   seven-group holdout and the fixed-/mixed-noise additional-parent endpoints.
   First reproduce the pooled saved endpoint values. Do not choose a scenario
   to replace the prior analysis or select new hyperparameters from its outcomes.
6. Quantify collinearity of old base features, recorded feature/DEM/setup costs,
   and a descriptive lag-one timing correlation diagnostic. None of these alone
   establishes a causal mechanism, IID validity, or an overhead-adjusted speedup.

The review's final decision should prioritize unresolved threats to the claim,
not seek the model with the most favorable observed score. Preserve the earlier
next-experiment recommendation and explicitly explain any change in priority.
