# Incremental training experiment

13 November 2026. Written before running this learning-curve analysis, after
examining the original pilot and stress results. This is explicitly post hoc
development analysis, not external preregistration or a new blind test.

## Question

Does increasing the number of distinct training program groups improve the
generalization of the base and structural ridge models? Does it reduce their
training/held-out gap? Extra optimization time is not varied: the ridge solution
is computed directly. No new decoder shots will be collected in this experiment.

## Data and scopes

Use the unchanged original 78-case pilot and the complete discovery cases from
the 48-case stress corpus. Exclude the single censored discovery case from all
population mean/p95 targets. Do not add selected confirmation, noise-boundary,
or feature-box outcomes. Recompute missing static graph features using the
archived feature function and saved DEMs, without measuring decoding again.

1. **Original-pilot learning curve:** merge the equivalent single/repeated
   logical-CNOT motif labels, giving seven related groups. For each fixed held-out
   group, enumerate every subset of 2, 3, 4, 5, and 6 other groups. All configurations
   from a group remain together. Report both train and held-out errors.
2. **Additional-program learning curve, fixed noise (primary expansion):** use
   all 78 original cases as an initial training set. Hold each of the 12 new
   parent programs out in turn. Add 0, 2, 4, 6, 8, or all 11 other new parents,
   using only complete p=0.001 discovery configurations. For each held-out parent,
   use 10 seeded random nested orders of the other parents; the same orders and
   configurations are used for every model. Exact duplicate subsets may be cached.
   The test configurations are fixed along each curve.
3. **Mixed-noise expansion (secondary):** repeat the preceding expansion with
   all complete discovery configurations, including the deliberately varied
   p=0.0003 and p=0.003 cases. This tests additional coverage as well as quantity,
   so do not attribute a change exclusively to sample count or topology.

New parent maps were previously checked to be distinct up to simultaneous block
permutation and different from the old maps. Check again that no ideal-map class
crosses the declared outer groups. The original seven groups are related small
motifs, not seven independent applications. Parent groups have unequal numbers
and kinds of configurations; report these counts.

## Models and selection

Use the original base inputs (B2, six columns), the original augmented inputs
(B3, 15 columns), and a declared sensitivity B3_stable (14 columns, omitting the
row-number-sensitive sampled two_step_mean). No other descriptor selection.
All inputs use log1p, and targets use log mean/p95 wall latency. Report both
targets, with p95 primary.

For every training subset and feature set, fit scaling inside each inner
training split. Select alpha independently for each target from
`[0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]`, using leave-training-group-out
inner validation and equal-group mean absolute log error. Break ties by the
declared grid order. Refit scaling and ridge on that whole training subset.
No outer-test values enter selection. The same search procedure is used for
all feature sets, including at every learning-curve size. Evaluate all declared
models; do not choose a winning model from the outer results.

Use one computational thread and low process priority, retaining progress and
checkpoint files. Preserve all original predictor coefficients, measurements,
analyses, protocols, and existing manifests.

## Reporting and interpretation

Primary error is exp(mean absolute log error). Within a held-out parent, average
over its configurations and then over training orders/subsets. Aggregate equally
over held-out groups, in log-error space before exponentiating. Training error
uses equal-group resubstitution MAE and is descriptive. Also retain case-weighted
training errors, inner-validation losses, selected alphas, and every outer
prediction. Record actual training configuration counts at each size.

Show variation across held-out groups descriptively; overlapping subsets and
orders are not independent samples and must not generate nominal confidence
intervals or inflated significance. The largest original-pilot endpoint must
reproduce a separate implementation of nested leave-group-out ridge. Check
selected fits against sklearn ridge and verify all earlier manifest entries.

Improving held-out error as more programs are added would support a data/support
limitation for the tested model. A persistent train/test gap is compatible with
overfitting or distribution shift. Large errors on both sides can suggest an
inadequate model/representation, but these patterns do not uniquely identify a
cause. There are no asymptotic sufficiency, static-topology necessity, deployment
guarantee, or useful-FTQC operating-point claims. Unequal target precision
(6,000 old shots versus 768 complete discovery shots), hardware-session context,
one-sector scope, and low logical accuracy in some configurations remain limits.
