# Next experiment: information versus model flexibility

Recommendation after the incremental-training results, 13 November 2026.
This is a proposed sequence; the new model comparison and measurements below
have not been run. Earlier frozen artifacts and completed analyses are unchanged.

## Why this is the next gate

More program coverage improved the structural model, but the fixed-noise gain is
small, concentrated in six-block cases, and disappears when the row-sensitive
sampled statistic is omitted. Mixed-noise p95 results are more encouraging for
both graph variants. A better use of the existing base information could still
explain the apparent structural advantage. That alternative should be tested
before a larger timing campaign.

## 1. Low-cost control on existing development data

Use the 125 complete existing configurations and the same grouped holdouts as
the completed learning-curve study. Compare the following four cells, reporting
both fixed-noise and mixed-noise domains and both latency targets:

| Model form | Base information | Same base information plus stable graph summaries |
|---|---|---|
| Additive ridge | Fit and evaluate | Fit and evaluate |
| One modest nonlinear model | Fit and evaluate | Fit and evaluate |

Use an RBF kernel-ridge model as the single declared nonlinear control; it can
express nonlinear responses and interactions. Specify a bounded alpha/bandwidth
grid and target centering before launching it, with the same tuning procedure
for the two feature sets. Do not expand the grid or switch algorithms in response
to outer-test results. This control tests one alternative model class, not every
possible nonlinear predictor.

Before this run, include the same two inexpensive derived noise-density ratios
in both base and augmented inputs: prior_sum/n_faults and
expected_activity/n_detectors. These are functions of existing base inputs, so
they add no information. They give the base model a fair opportunity to use the
noise calibration signal already identified in the stress tests. Retain a
comparison to the six-input baseline for continuity, labeled as such.

Keep the eight stable graph additions and exclude two_step_mean from primary
conclusions. Check descriptor invariance under detector/mechanism relabeling
without treating that check as a decoder-ordering experiment. Fit scaling and
target centering only inside each training split. Select hyperparameters only
inside outer-training parent groups, independently for each feature set and
target. Preserve per-parent errors, training errors, block-count breakdowns,
and target-estimation uncertainty. Equal model classes and tuning procedures
matter more than equal wall-clock fitting times for these small direct fits.

The present data remain development evidence. A nonlinear baseline catching up
would weaken the need for extra graph information in this setting; it would not
prove graph information is universally unhelpful. A surviving stable-graph gain
would motivate prospective validation rather than establish the paper claim.

Primary method references:
- [Kernel ridge, pinned-version documentation](https://scikit-learn.org/1.8/modules/generated/sklearn.kernel_ridge.KernelRidge.html)
- [Nested validation and selection bias](https://scikit-learn.org/1.8/auto_examples/model_selection/plot_nested_cross_validation_iris.html)

## 2. Freeze candidates and collect a balanced prospective corpus

If Stage 1 leaves a plausible consequential structural gain, fix the candidate
pipelines before inspecting any new test timing. Generate new parent programs
outside all previously used ideal-map classes and reserve their test identities
in advance. Use balanced four-/six-block coverage and cross program, distance,
noise, and placement rather than allowing the six-block groups to have only one
configuration each. Keep all related schedules of a parent in the same split.

A bounded accuracy-only screening phase should determine a declared logical-Z
quality regime and sample-size/resource plan. Retain screening outcomes and keep
test timing unopened during those decisions. Do not call a convenient logical-Z
cutoff a full FTQC accuracy requirement. Any full-Pauli claim needs complementary
sector validation; a sector-scoped paper must state the limitation explicitly.
High-noise counterexamples with 7–12% logical-Z failure cannot establish a useful
compiler regime.

Give training and reserved test targets comparable measurement precision, repeat
sessions with randomized serial case order, retain service-time censoring, and
plan uncertainty around independent parent programs. Bootstrap repetitions of
overlapping training subsets are not extra independent programs. No precise
training-corpus size or hardware service budget is selected from the existing
prediction improvements alone.

## 3. Make the outcome a compiler decision

Within each new parent, compare valid implementations of the same logical action,
such as different placements of its fixed gate sequence. Measure prediction and
ranking error, selected-schedule cost/regret, and timing-budget admissions after
the logical-accuracy gate. Include base/noise-aware models, ordinary component
decomposition where applicable, and a small profiling baseline. Count feature,
DEM/model construction, and profiling overhead with the relevant amortization.

The old d5, four-block spread/burst pairs at p=0.001 have observed p95 ratios
of about 1.02–1.33. These are exploratory candidate evidence, not independent
replications or a demonstrated decision benefit. Both schedules' measured p95s
are below the old illustrative 5 ms budget, so those differences alone do not
change its p95 admission decision. Do not retrospectively move the deadline
between measured costs to manufacture a useful admission example. Use an
externally motivated budget, a predeclared budget sweep, or schedule regret.

## Go / no-go interpretation

- **Proceed with a structure-aware contribution** if stable graph additions beat
  well-calibrated base controls on fresh reserved parents and improve useful
  same-program decisions after accuracy and overhead are considered.
- **Refocus on calibration/domain validity** if the stronger base controls remove
  the structural advantage. The earlier frozen-model failure remains valid, but
  a publishable calibration contribution still requires novelty and utility.
- **Reject the compiler-benefit claim** if prediction gains do not affect useful
  decisions, occur only at poor accuracy, or are consumed by feature/profiling cost.

The immediate action is Stage 1 on existing data. It is the least expensive test
that can materially change which paper we should try to write.
