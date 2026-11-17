# Bounded tuning-grid diagnostic

16 November 2026. Written after inspecting existing chosen parameters and before
running the expanded fits. User explicitly requested a methods/mistake audit and
then asked to continue. This is development analysis of inspected outcomes, not
a fresh test or a preregistration. Frozen studies will not be edited.

Confirmed trigger: all 31 saved RBF graph16 p95 fits select the minimum alpha
1e-4; 29 also select the minimum gamma multiplier 0.01. This does not prove a
reversed model ranking, but leaves search adequacy unresolved. These direct
linear/kernel solves do not have an epoch budget to extend.

Reproduce the 186 original model/domain/group fits with their original grids.
Then repeat the identical splits, feature definitions, log transformations,
training-fold scaling, centering, targets, equal-group inner loss and selection
rule with a wider symmetric grid for all six models:

- Alpha: powers of ten from 1e-8 through 1e6 inclusive (15 values).
- RBF gamma multipliers: powers of ten from 1e-4 through 1e2 inclusive (7 values).
- Retain original candidate ordering, target-specific selection and first-minimum
  tie breaking. Keep original configurations weighted equally within each fit;
  do not confound this diagnostic with a change of training weights.

No new features, decoder calls, physical samples, workloads, target estimates,
thresholds or hardware measurements. No inference timing benchmark. Report both
targets and all three domains, including negative results. Do not enlarge the
grid again automatically if boundaries persist.

Use the archived Fitter implementation as a numerical engine, without invoking
its main entry point or writing into its frozen directory. Verify original-grid
choices, losses and predictions against the saved checkpoints. Check selected
extended-grid solutions with separate sklearn Ridge/KernelCenterer/KernelRidge
fits; report numerical discrepancies explicitly.
For each domain/model verify the outer fold with the smallest selected p95
alpha, then smallest gamma, then held-group name (18 folds, both targets), using
sklearn. Compare full original-grid bridge predictions as an additional replay
check. Numerical predictions for new bridge feature vectors use the same stable
SVD/eigendecomposition as the fitting path, avoiding an additional conditioning
confound from solving normal equations at the newly small alpha values.

Also compute arithmetic predictions on the already-inspected bridge using its
same parent-excluded fit convention. This is exploratory reuse, not new
generalization evidence or a replacement of its frozen predictions. Keep
prediction accuracy distinct from useful decisions, label precision, quality,
cost and consumer feasibility.

Resource bound: one fitting pass for each grid, one thread, low priority, at most
five minutes of fit wall time checked between outer folds. Preserve partial
outputs and mark incomplete on reaching the cap. No outcome-dependent expansion.
This is a bounded analytical diagnostic, not a new training campaign.
