# Response to the underfitting / overfitting concern

13 November 2026. This is a post hoc diagnostic of the unchanged 78-case pilot,
not a new confirmatory model comparison. No decoder measurements or deployment
predictor updates were made. See `diagnose.py` and `results.json`.

## What the concern gets right

Adding features can increase the data needed to estimate a useful predictor.
A failure to improve held-out predictions does not establish that the added
information is useless. The predictor may overfit a small set of programs, use
an unsuitable functional form, have unsuitable regularization, or receive weak
summaries of the relevant connections. These explanations are not mutually
exclusive. In particular, an additive model can miss a real interaction while
fitting incidental variation elsewhere.

We tested six base features against those features plus nine selected graph
statistics (15 total), not a learner with the complete adjacency structure as
input. The approximate two-step statistic also has a previously documented
row-numbering sensitivity. The 468,000 old timed shots improve the precision of
78 configuration-level target estimates; they are not 468,000 independent graph
examples. The original eight motif groups are related, and two implement the
same ideal logical operation. Merging those two labels leaves seven groups,
without turning the remaining groups into independent applications.

## Fitting time is not the present limitation

Every checked dense ridge fit used the Cholesky solver, a direct linear solve.
Refitting using the SVD solver changes predicted log latencies by at most
1.066e-14. There is no epoch budget whose extension would improve these fits.
This rules out inadequate optimization time as the explanation for this specific
ridge comparison. It does not rule out insufficient data or model flexibility.

The numerical solver behavior is consistent with the pinned-version
[scikit-learn Ridge documentation](https://scikit-learn.org/1.8/modules/generated/sklearn.linear_model.Ridge.html).

## Training versus held-out behavior

The table uses alpha=1 and the conservative single/repeated-merged grouping.
Scaling is fitted separately within each outer training fold. Error factors
are exp(mean absolute log error), averaged equally over outer folds before
exponentiation. Training factors are resubstitution descriptions, not
generalization estimates. One is perfect; smaller values are better.

| Target | Inputs | Training error factor | Held-out-group error factor |
|---|---|---:|---:|
| p95 latency | Base sparsity/activity | 1.05965 | 1.07739 |
| p95 latency | Base plus graph statistics | 1.05800 | 1.14173 |
| Mean latency | Base sparsity/activity | 1.14617 | 1.18572 |
| Mean latency | Base plus graph statistics | 1.11024 | 1.19702 |

The larger model fits the training configurations better but transfers less well
on average, particularly for p95. This is compatible with overfitting / limited
data and distribution differences among held-out groups. It is not a proof that
overfitting is the unique cause. It also does not rule out underfitting of
specific interactions or problems in the selected graph representation.

The original eight-label grouping gives the same qualitative pattern. The
archived nested regularization diagnostic already tested alpha values
0.01, 0.1, 1, 10, and 100, separately for each feature set using only outer-training
outcomes for inner selection. On all 78 configurations, tuned p95 error factors
were 1.05721 for base inputs, 1.06635 for the local graph additions, 1.07782 for
component additions, and 1.11772 for the full graph additions. Thus changing the
single fixed alpha did not reveal a p95 advantage in those tests. The grid and
model class were limited; this is not an exhaustive exclusion.

For mean latency, the tuned local additions did improve the full-corpus factor
(1.13293 versus 1.16448), while they worsened it on the connected subset
(1.21845 versus 1.18261). Any blanket statement that graph information never
helped would therefore also be too strong.

## Consequence for the research claim

The supported statement is: **the tested graph summaries did not improve p95
generalization under the tested ridge protocols and limited corpus.** A general
claim that topology adds no predictive value is unsupported.

The frozen-model noise-transfer counterexample remains a valid model-specific
result. A demonstration of overfitting in one model comparison would not erase
the observed admission error of another frozen predictor. It would constrain
the proposed explanation and the choice of repair.

## Follow-up needed before attributing a failure to missing information

1. Use paired learning curves that increase the number of distinct parent
   programs, keeping test parents fixed and all related schedules within a group.
   More shots of the same configurations are a separate target-precision study.
2. Tune regularization inside each training subset for each feature set, including
   each learning-curve size. Give both feature sets the same declared search
   procedure. Do not select settings from outer-test performance.
3. Compare base and augmented inputs within both an additive model and one
   predeclared, modest model that can express interactions. Fit all preprocessing
   within training folds. Assess graph descriptors' stability before this test.
4. Vary noise independently from size and program. Report interpolation and
   extrapolation separately. Both current models can be poorly calibrated to an
   independent noise shift because the original training corpus used p=0.001.
5. Freeze the resulting comparison and evaluate on fresh reserved programs at
   relevant logical accuracy, including admission errors and feature/profiling
   overhead. The stress results already inspected are development evidence.

Learning curves can help distinguish persistent model bias from data-sensitive
generalization, but cannot uniquely identify the cause on a small shifted corpus;
see the [scikit-learn validation and learning-curve guide](https://scikit-learn.org/1.8/modules/learning_curve.html).
No such learning-curve or nonlinear-model experiment was executed in this
diagnostic, and no fresh-test structural benefit is claimed.

## Integrity

The script verified all 905 original manifest entries without a mismatch before
the diagnostic. Inputs, model columns, folds, solver checks, and all fold-level
errors are retained in `results.json`. The original artifact and the completed
stress-phase snapshots remain unchanged. This is internal analysis by the same
assistant, not external peer review.
