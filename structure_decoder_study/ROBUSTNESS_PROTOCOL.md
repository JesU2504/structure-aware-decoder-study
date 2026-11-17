# Post-analysis regularization sensitivity

This is an explicitly **post hoc exploratory** diagnostic, motivated by Stage 1's
failure of structural features to improve the frozen ridge model. It does not
replace the primary analysis, rescue a confirmatory claim, or authorize choosing
a winning result for a paper without fresh validation.

Question: does the negative structural-feature result depend on fixing ridge
alpha at 1.0 or on including unhelpful structural features together?

Use the existing pooled mean/p95 targets and the same leave-program-family-out
outer folds. Within each outer training set, select alpha from
`[0.01, 0.1, 1, 10, 100]` using leave-family-out inner folds, minimizing equal-family
mean absolute log prediction error. Standardize features within each individual
training fold. All outer test-family outcomes are excluded from selection.

Compare the frozen B2 input set with three prespecified additions:

- Local degrees/arity: row/column variance and p95, hyperedge fraction.
- Components: component count, largest detector-component fraction, second moment.
- Full frozen B3 feature set.

Report all additions. Apply the same nested selection to the connected-task
subset as a sensitivity check. No neural networks, broad feature search, test-set
tuning, additional samples, or changes to the original timing data.

Recompute selected fits from independently measured session targets as needed
only if a structural gain appears and requires confirmation. This diagnostic
can identify model-class sensitivity, but the corpus remains small, related,
one-sector, and equal-duration. A negative result does not prove structural
information is useless for other decoders or workloads.
