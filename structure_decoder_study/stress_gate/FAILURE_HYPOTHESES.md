# Predictions about model failure, before stress timings

13 November 2026. These are falsifiable qualitative expectations, not fitted
failure probabilities. No new timing results have been observed when writing
this file. Predictors and the complete 48-case corpus are frozen.

1. **Noise transfer is weakly identified.** The old data varies distance, blocks,
   and programs at one physical noise rate. Prior sum/activity are highly tied to
   size in that training set. Their fitted coefficients therefore need not predict
   an independent change in noise correctly. Expect the high-noise cases to be
   candidates for underprediction through more expensive LSD work. Low-noise
   cases may be overpredicted. Equal marginal feature ranges do not remove this
   identifiability issue.
2. **Large-size transfer can change the expensive-work mixture.** d=9 and some
   d=7/2d-window tasks exceed the training support. More rows/nonzeros may increase
   both per-iteration work and the incidence/cost of large LSD clusters. Historical
   padding need not cover this. The sign of overall regression error is not
   assumed: size extrapolation may also overpredict.
3. **Typical latency can look accurate while mean work fails.** Most calls may
   remain dominated by bounded BP iterations, while a small number of large LSD
   events change mean resource consumption. Look for disagreement between p95
   error and mean error, with independently measured fallback/cluster diagnostics.
4. **Burst placement is a structural stress, not an assumed slowdown.** Moving
   all serial CNOTs to one boundary preserves the ideal map but changes propagation
   and the DEM. Conditional on nonzeros and activity, the direction of cost change
   is uncertain. Compare burst/spread per parent program before claiming an effect.
5. **Within-range new programs are the strongest challenge to the abstraction.**
   Thirty-six cases have every B2 input within its old marginal training range.
   A failure there cannot be dismissed merely by pointing to an out-of-range
   detector count. It can still reflect joint-support shift, missing nonlinearity,
   implementation behavior, or missing structural information. Distinguish these.

The historical p95 margin is about 1.787. For example, q4_P00 at d=5/w=10 has a
frozen raw p95 prediction of about 1.931 ms at p=0.001 and 2.383 ms at p=0.003.
The latter remains admitted under the historical margin at the illustrative
5 ms service budget. Whether its true deadline-miss probability exceeds 5% is a
fresh test, not a result already known.

If failure occurs only at noise levels with poor logical accuracy or far outside
training support, label that limitation. Such a case alone does not establish a
useful compiler contribution. If simple padding works throughout the relevant
regime, record that robustness rather than searching for a favorable headline.
