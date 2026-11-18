# Post hoc implication: unchanged-list score aggregation cannot rescue these cases

18 November 2026. This is an analytical consequence of the completed diagnosis,
not a prespecified diagnostic metric, new decoder test or method contribution.
No additional candidates, scores, corrections or samples were evaluated.

Consider only the already saved list and weights w(c)=exp(-S(c)), where S is
the unchanged source sum(log(1/p)) surrogate. This is a defined finite-list
weighting, not a claim of calibrated posterior probabilities or full coset mass.

Let T be the minimum score in the observed correct logical class, n its number
of list members, and C the minimum score in a competing represented class.
Every correct-class term is at most exp(-T), while the competing class contains
at least one term exp(-C). Therefore

    W_true / W_competing <= n * exp(-(T-C)).

| Case | n | T-C | log ratio upper bound | Ratio upper bound |
| --- | ---: | ---: | ---: | ---: |
| 131 | 13 | 32.75243038 | -30.18748102 | 7.76e-14 |
| 228 | 370 | 24.36963131 | -18.45612831 | 9.65e-9 |

Both bounds are below1. Simply replacing minimum-score selection with a sum of
these same surrogate weights over each class in the SAME saved list cannot
make the observed correct class win in either case. Numerical discrepancies
of order1e-12 cannot affect this conclusion.

This rules out that specific unchanged-list aggregation as a rescue for these
two inspected observations. It says nothing about candidates outside the list,
a different weighting/model, exact Bernoulli likelihood, full degenerate ML,
other syndromes or a population error rate. Class counts alone are not physical
probability masses. The bound is useful for avoiding a redundant experiment;
it does not identify a new mechanism or justify a new decoder.

Inputs and unrounded values are in [finite_list_bound.json](finite_list_bound.json).
