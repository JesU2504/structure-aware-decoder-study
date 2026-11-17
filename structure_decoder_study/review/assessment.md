# Second-pass assessment and recommendation

Review date: 12 November 2026. This assessment separates numerical correctness,
experimental scope, and readiness to support a research claim. It is an internal
review by the same research assistant, not external peer review.

## Verdict

The saved measurements and reported regression calculations pass the additional
checks below. No fatal numerical error was found. It would nevertheless be
incorrect to certify that every scientific assumption is validated or that the
paper hypothesis has been resolved. The experiment is a useful restricted pilot.

The narrow supported conclusion is: on this corpus, with these fixed decoder
settings and selected features/models, the richer structural model did not
improve held-out p95 prediction beyond sparsity and expected activity. This does
not establish that topology is generally uninformative or that the simple model
is sufficiently reliable for compiler admission.

## Additional checks completed

`review_audit.py` does not import the measurement or fitting implementation. Its
output is `review/numerical_review.json`.

- Verified all 905 files in the completed artifact manifest: zero hash mismatches.
- Recounted 468,000 primary timing observations, zero invalid-correction flags,
  and 4,020 logical-Z failure flags from raw files.
- Recomputed means and linearly interpolated p95 values from raw latencies.
- Recomputed all primary and connected-subset ridge predictions using a direct
  linear-algebra solution instead of the sklearn fitting pipeline. The maximum
  relative difference from saved primary predictions was 1.61e-14.
- Independently recomputed component counts with union-find and expected detector
  activity using a sparse log-product expression. Maximum activity discrepancy
  was 7.46e-14. Matrix dimensions, nonzeros, and prior sums also matched.
- Checked the installed decoder's actual settings on a direct public circuit:
  per-mechanism channel probabilities match, max_iter=30, minimum_sum BP, scaling
  0.625, parallel message schedule, LSD order 0, and one configured thread.

These checks complement earlier sample replay and syndrome/observable checkpoint
tests. Reusing Stim is not an independent physical simulator implementation.
Hashes establish artifact consistency, not the truth of a scientific assumption.

## Corrections and methodological weaknesses

### 1. Motif holdout is weaker than ideal-program holdout

The original folds group by named motifs. A single CNOT and three repeated CNOTs
on the same pair implement the same noiseless logical action. The original
`single` and `repeated` labels therefore do not keep every implementation of that
logical map in the same fold. The source circuits and noisy tasks are distinct,
so this is not literal duplicate-shot leakage, but earlier language about holding
out all implementations of one logical program was too strong.

A conservative sensitivity merging both motif labels across sizes gives:

| Inputs | Mean error factor | p95 error factor |
|---|---:|---:|
| Sparsity/activity | 1.1857 | 1.0774 |
| Selected structural additions | 1.1970 | 1.1417 |

The model ranking remains unchanged. Future splits must use explicit parent
program identity and documented equivalence/symmetry relationships. The eight
original labels are related small motifs, not eight independent applications.

### 2. One approximate graph feature depends on row numbering

The sampled two-step neighborhood feature inspects 32 selected detector IDs.
On the same d7 cycle-late graph, its value is 31.25 in the original ordering and
ranges from 18.1875 to 44.875 under 20 row permutations. The other size/activity
features in that comparison are unchanged by relabeling.

This is a noisy approximation, not an intrinsically invariant graph descriptor.
It needs a more stable estimator, explicit sampling uncertainty, or a numbering
robustness check. This does not change the arithmetic of the reported model test,
but it weakens any broad interpretation of a negative result for structural
information. No decoder timings were rerun under these permutations, and no
claim about decoder ordering sensitivity follows from this descriptor test alone.

### 3. Internal audit terminology needs care

The earlier independent checks were separate code paths written by the same
assistant. They were not an external review or reproduction by another researcher.
The analysis metadata-merging bug was preserved and corrected before fitting;
its versioned amendment is recorded. The new numerical checks reproduce the
corrected results, but neither the checks nor the amendment make this a
confirmatory, externally preregistered study.

## Important limits that do not invalidate the restricted measurements

- A logical-Z sector is a legitimate explicitly scoped decoding experiment.
  It does not validate full Pauli logical accuracy or arbitrary-state compilation.
- Computational-basis truth tables do not alone prove arbitrary coherent quantum
  program equivalence. A later full-computation claim needs the appropriate
  logical-frame, complementary-basis, or channel-level checks.
- We measured warm decoder API calls. The 1.57x decomposition result sums those
  calls and excludes splitting/assembly and cold setup. It is not an end-to-end
  control-loop speedup or a parallel-hardware result.
- The volume proxy is our fitted baseline. We have not reproduced PACE's numerical
  performance case study, exact calibration settings, or scheduler.
- The large equal-volume spread compares distinct programs, with different
  sparsity and activity. It does not by itself demonstrate topology dependence
  after controlling these quantities or improved choices for one computation.
- A 468,000-shot corpus still has only 78 circuit instances. Repeated timing
  sessions improve measurement assessment, not the diversity of logical programs.
- Quantile/mean uncertainty and rare-event probability need stronger assessment.
  The few-family bootstrap is exploratory. Nearby deadline classifications can
  change with measurement uncertainty. A p95 error factor is not an admission-risk
  guarantee, a worst-case error, or a percentage accuracy score.
- Extreme-shot CPU replay supports genuine expensive decoder work. Selected
  extremes cannot establish its incidence, distribution family, or predictability.
- Mac heterogeneous cores, absent affinity, one decoder, one noise setting, and
  full-block tasks limit transfer to dedicated real-time implementations.

## Best next step

Run one small mechanism-and-decision study before expanding models or benchmarks.
Keep the original question, but give it an operational target: can inexpensive
pre-execution information correct practically important errors in a strong
decoder-budget model?

1. **Validate the intended decoding unit.** Select connected tasks after ordinary
   decomposition, fix detector basis and window boundaries, and check the chosen
   sector/full-decoder semantics against a reproducible reference. Complete
   two-sector validation is necessary for broad full-QEC claims, not a blanket
   requirement for a clearly restricted sector cost experiment.
2. **Explain expensive work first.** Separately measure BP work, LSD entry,
   cluster growth/factorization, process CPU, and wall time on a small, controlled
   set. Use execution statistics only as diagnostics. Prespecify the operational
   deadline/throughput target and collect enough fresh samples for its uncertainty,
   rather than merely choosing a large shot count. Determine whether residual
   cost persists on connected, relevant tasks after size/sparsity/noise controls.
3. **Test added information on new programs.** Use exact/stable cheap structural
   descriptors, true parent-program holdout, a separately reserved test corpus,
   and independently calibrated conservative baselines. Freeze features and model
   selection before evaluating those test programs. Include a competitive simple
   nonlinear or mechanism-derived baseline if linearity is an unresolved concern.
4. **Require a useful compilation decision.** Compare legal schedules of the
   same computation using a fixed candidate-generation/scheduling policy. Account
   for logical accuracy, model/feature/DEM construction, ordinary decomposition,
   conservative padding, and direct profiling at comparable total cost.

Continue toward the original paper claim only if structural information produces
a reproducible decision benefit over those baselines. If the simple calibrated
model suffices, retire the added-topology contribution. A different paper angle
would need a separately justified contribution and evidence; changing the title
or emphasizing known latency tails would not establish novelty.

A QEC researcher should review the circuit/decoder assumptions and another person
should reproduce the artifact before submission. No such external review has yet
been obtained, and no messages to other people have been sent.
