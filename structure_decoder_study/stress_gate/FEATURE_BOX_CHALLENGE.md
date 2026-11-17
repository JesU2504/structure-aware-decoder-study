# Adversarial challenge to a marginal feature-range warning

13 November 2026, after the selected noise-boundary study and before collecting
this phase. The observation that discovered failures were range-flagged is not a
safety guarantee. Challenge it with q4_P01 and q4_P03 at p=0.0024, d=5, four blocks,
ten rounds, spread placement. This fixed intermediate rate is chosen just below
the old prior-sum range limit, not by searching its timing outcomes.

Before timing, require all six B2 inputs to lie within old marginal minima/maxima,
H/L and the noise-free circuit to match the p=0.001 reference, and the unchanged
padded p95 prediction to admit the 5 ms budget. If these conditions fail, report
the failed setup rather than silently alter the rate. Although the scalar inputs
are within range, p itself differs from the old fixed 0.001 training condition.

Collect three fresh randomized serial sessions of 2,000 shots per task (12,000
total) using a distinct feature_box seed namespace and the existing 20-CPU-second
measured-service cap. This is a selected-task adversarial test. Use simultaneous
exact-binomial intervals over two pooled cases (alpha=0.05/2) and six sessions
(alpha=0.05/6), under the stated IID/context assumptions. Mask population intervals
if censored. Do not refit the predictor. A lower miss-probability bound above 5%
would refute the sufficiency of this simple range warning on the selected task;
it would not prove a topology omission, a useful FTQC regime, or a general error
rate. Retain logical-Z failure outcomes and all checkpoints.
