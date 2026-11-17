# Bounded validation gate

13 November 2026. Authorized after the skeptical internal review. This is a
development/calibration gate, not the final reserved-parent test or an external
preregistration. All earlier artifacts and predictors remain unchanged.

## Decision and scope

The concrete compiler primitive is choosing between burst and spread placements
of a fixed CNOT sequence, at fixed distance, block count, extraction rounds, and
physical noise, to reduce CPU decoder service p95. Quantum instruction/TICK counts
are matched within a pair. No quantum-duration speedup, queueing guarantee,
memory feasibility, full Pauli accuracy, or hardware deployment benefit is claimed.

Report p95 selection regret against the finite measured candidate set, and the
logical-Z accuracy/service-time frontier. A candidate is screen-qualified only
if its one-sided simultaneous logical-Z failure bound is at most 1% per whole
task. This is an explicit pilot screen selected using prior development knowledge,
not an acceptable full FTQC error requirement. The screen is measured during
calibration and is shared by every cost model; it is not a learned or deployable
accuracy predictor. If uncertainty excludes a useful choice, report that result.

For admission diagnostics use all service budgets
`[0.25, 0.5, 1, 2, 4, 5, 8, 16, 32]` milliseconds and a 5% service miss limit.
The 5 ms point preserves the previous illustrative budget; the other values are
a declared diagnostic sweep, not hardware requirements. Report the complete
sweep without choosing a favorable deadline after outcomes. Report unsafe and
conservative admissions together. Actual useful-system claims remain conditional
on an externally motivated resource model and accuracy requirement.

## A. Stronger baseline controls on existing data

Use the unchanged 125 complete development configurations. Retain original
seven-group holdout, original-data-plus-new-parent holdout at fixed p=0.001,
and the corresponding mixed-noise endpoint. All related configurations of a
held-out parent stay excluded from training and inner selection.

Feature sets:

- base6: the original six sparsity/activity inputs;
- density8: base6 plus prior_sum/n_faults and expected_activity/n_detectors;
- graph16: density8 plus the eight original stable graph statistics, omitting
  two_step_mean.

Compare additive ridge and RBF kernel ridge for each set. The primary four-way
comparison uses density8 and graph16; base6 is continuity evidence. Input
transformation is log1p, with StandardScaler fitted only on each training split.
Targets are log mean/p95 latency. Ridge fits an intercept. Kernel ridge centers
both its training kernel and targets, with all evaluation centering learned from
the training split. Its prediction is the centered-kernel prediction plus the
training log-target mean.

For every feature/model/outer fold choose parameters by equal-training-group
inner leave-group-out absolute log error, separately for the two targets.
Alpha grid: `[0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]`.
RBF gamma is multiplier / number_of_features, with multipliers
`[0.01, 0.1, 1, 10]`. Order candidates by multiplier then alpha; tie-break by
first minimum. No grid expansion or algorithm switching based on outer results.

Retain raw predictions and an empirical safety margin for each target/model:
the maximum inner out-of-fold underprediction at the selected parameters,
bounded below by one. This reuses inner selection outcomes and has no formal
coverage guarantee. It is a declared conservative comparator, not a certificate.
Neither predictions nor margins are updated after new bridge timing.

Generate bridge predictions with the corresponding parent excluded: original
motif outer fits for old bridge cases; new-parent mixed-noise fits for new cases.
Check stable descriptor invariance under detector/column permutations, separately
from any assertion about decoder-ordering sensitivity. Reproduce selected fits
using sklearn Ridge/KernelRidge and KernelCenterer.

## B. Small interleaved measurement bridge

Use d=5. Old exact circuits: two-block memory, four-block chain-spread, and
four-block cycle-late (all twelve rounds, p=0.001). New calibration parents:
q4_P00, q4_P03, q6_P00, q6_P03. Cross these four parents with burst/spread
placement and p in `[0.0003, 0.001]`, with ten rounds. This is 19 configurations:
three exact old references and sixteen balanced four-/six-block configurations.
Some placements/noise settings are new configurations of already inspected
parents; no new parent is a reserved final test.

Preserve circuit-derived physical syndrome sampling and observable outcomes.
Validate noiseless detectors and DEM event reconstruction before timing. All
configurations use pinned BP+LSD0 settings, changing only max_iter=30 versus 100.
Use exactly the same syndrome/observable stream for these two decoder settings.
For the disconnected memory reference also time ordinary component decomposition,
including per-call gather/merge overhead. All corrections must satisfy Hc=s.

Run three fresh Python processes with deterministic independent sampling namespaces.
Per configuration/process collect 512 evaluation shots in eight blocks of 64.
Randomize configuration order in every block and decoder-setting order within
each configuration/block. Reuse warm decoder instances, matching the original
warm service mode; use 32 common warmup shots. Record wall and process CPU time.
Construction, sampling, validation, and result checking are excluded from service
time but separately recorded where applicable. No concurrent model fitting or
other benchmark is launched by this agent during these runs.

The per-configuration/process resource cap sums measured service CPU across
settings and is checked after a whole block. Its value is 20 seconds; a block
can overshoot. Retain all complete paired blocks and mark the configuration
censored if fewer than eight blocks finish. Suppress population quantile and
accuracy intervals for stopped cases. This cap is not a native decoder timeout.

Before evaluation, collect a disjoint 64-shot-per-process profiling stream with
max_iter=30. This gives 192 profiling shots per configuration. The direct-profiling
baseline ranks schedules by its empirical p95; admission also uses a conservative
one-sided p95 order-statistic bound (alpha=0.05/19 across bridge configurations).
Report construction, feature, inference, and profiling costs; do not treat small
sample profiling as certain or free. Profile observations are not evaluation shots.

Record BP convergence/iteration diagnostics on nonzero syndromes only; zero-shot
native state flags are not a reliable mechanism diagnostic. These flags are not
compiler-facing input features.

## C. Interpretation and stopping

Use family-balanced prediction error, per-parent results, measured same-program
selection regret, and the entire budget sweep. Independent exact-binomial and
order-statistic intervals are conditional on stable-context/IID assumptions;
repeat-session checks are descriptive. Use alpha=0.05/19 for BP30 logical-quality
and p95 intervals, and alpha=0.05/(19*9) for its evaluation miss-rate sweep.
Treat BP100/decomposition comparisons as paired configuration diagnostics, with
accuracy disagreements retained. Comparisons are not a final hardware trial.

This gate proceeds to new reserved parents only if stable graph information
retains a consequential advantage over the declared controls and the measured
decision primitive has potential beyond accuracy/overhead uncertainty. A stronger
base model catching up, trivial decisions, or poor quality is a reason to narrow
or stop the compiler contribution. Do not launch a large corpus merely because
one exploratory error factor is smaller.
