# Noise-boundary localization on selected counterexample tasks

13 November 2026. This is a post-discovery, selected-task exploration. It does not
estimate performance on a random application population and does not refit the
predictors. It follows fresh confirmation of failures at p=0.003 for q4_P01/P03.

Hold each selected task's d=5, four blocks, ten extraction rounds, spread placement,
gate sequence, detector basis, and decoder parameters fixed. Test p=0.0015,
0.0020, and 0.0025: six cases, three fresh randomized sessions of 1,000 physical
shots each, distinct boundary seed namespace, and the same 20-CPU-second service
cap. Retain partial/censored cases and exclude them from binomial claims.

Before timing, require exact equality of H and L with each task's p=0.001
reference, and equality of noise-free physical circuits. Only physical channel
probabilities and resulting DEM priors may change. Validate ideal behavior and
record all model predictions in advance. Coefficients and the historical p95
safety factor remain frozen.

Use the illustrative 5 ms deadline and 5% miss-probability limit. Report simultaneous
exact-binomial intervals at alpha=0.05/6 (pooled cases) and alpha=0.05/18
(session checks), with the same conditional IID assumptions. A tested rate is
clearly below the illustrative limit if its upper interval bound is <0.05 and
clearly above if its lower bound is >0.05. Otherwise label it unresolved.

Combine these selected-task observations with the existing p=0.001 discovery
reference and the fresh p=0.003 confirmation, identifying their different phases
and sample sizes. Do not fit or assume a monotone curve, claim an exact critical
rate, or silently interpolate unresolved intervals. Report brackets only where
the measured evidence supports them. Logical-Z error fractions remain a separate
quality diagnostic and may make a timing failure irrelevant to useful FTQC.
