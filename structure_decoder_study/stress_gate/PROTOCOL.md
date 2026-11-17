# Frozen-model failure-boundary exploration

13 November 2026. This is an adversarial **discovery study**, not an unbiased
application benchmark or a confirmatory test of a newly fitted structural model.
Its purpose is to identify where the old simple model fails and to explain those
failures. All old observations and models are preserved.

## Predictors fixed before new timing

Train the old B2 log-linear ridge model (alpha=1) on all 78 archived instances,
separately for mean and p95 wall service time. Inputs remain distance, detector
count, mechanism count, nonzeros, prior sum, and expected detector activity.
Store the coefficients, training standardization, and source hashes before
sampling new timing data. Also fit the old volume/distance baseline.

Give B2 a historical safety factor: the maximum actual/predicted ratio from
leave-group-out predictions on the archived corpus, conservatively merging
single/repeated logical-CNOT motif labels. This factor is an empirical historical
margin, not a calibrated out-of-distribution risk bound. Test both raw and padded
predictions without updating them from stress-test outcomes.

## Corpus design and axes of stress

Generate 8 new four-block, six-CNOT programs and 4 new six-block, eight-CNOT
programs with fixed random seeds. Require connected logical interaction graphs,
no immediately repeated identical CNOT, and unique ideal binary linear maps up
to simultaneous block permutations. Exclude ideal-map classes of archived
programs. Store exact gate sequences and canonical map IDs. No model sees new
timings during program selection.

For the 8 four-block programs, use d=5, rounds=10, p=0.001, with spread and burst
placements. For the first four, additionally stress one axis at a time:

- Noise: p=0.0003 and 0.003 at d=5, rounds=10, spread.
- Temporal extent: rounds=5 and 15 at d=5, p=0.001, spread.
- Size: d=3/7/9 with rounds=2d, p=0.001, spread.

For the four six-block programs, use d=5, rounds=10, p=0.001, spread.
This defines 48 cases. Multiple gates may occur after one extraction round, in
their specified serial order. Each transversal gate retains the public builder's
TICK. A burst packs all gates at the middle boundary. Spread distributes them
between the initial and final extraction rounds. The compared placements
implement the same logical program; this study makes no duration-speedup claim.

Require connected detector graphs after conversion. If a logical program yields
a disconnected detector graph, preserve and report it as a scope failure; do not
silently replace it after inspecting timings. There is no new componentwise
optimization in this phase.

## Workload semantics and construction checks

Remain explicitly scoped to the pinned TMCBS logical-Z detector sector with
full-block preparation/readout boundaries. W=2d cases resemble a window extent,
but sliding-window commits and online boundary messages are not implemented.
No full Pauli-accuracy, memory-budget, or real-time response claim is made.

Use a source-fragment assembler to avoid repeatedly rebuilding identical
extraction rounds. It reuses unmodified public initialization, round, readout,
and transversal-gate fragments. Gates add no measurements, so measurement-record
references are preserved. Before new timing, require literal circuit equality
with **all 78 archived circuits**. Independently check new circuits' ideal
detectors, d=3 computational-basis truth tables for each new parent program,
and both X/Z logical-Pauli conjugations of the transversal gate sequence.
Check DEM-event parity reconstruction and retain source/configuration hashes.

## Measurement and resource boundary

Use unchanged ldpc 2.4.1 BP+LSD-0 settings, one configured thread, no zero-syndrome
bypass, and statistics disabled for measured service. Record both process CPU
and wall time around every API call. Extra CPU-clock reads have small overhead;
record clock-only control measurements, do not subtract them. Sampling,
conversion, feature extraction, setup, and correction checking are outside the
API interval. No concurrent benchmark workers are permitted.

Discovery: 3 independently sampled sessions, 256 shots/case/session, randomized
case order and 32 separate warmup shots. This is 36,864 planned physical shots.
Every correction must reproduce its syndrome. Record logical-Z failures without
asserting accuracy equivalence. A 20-CPU-second per-case/session cap stops a case
after the current call, saves its partial data, and labels it censored. Never
silently omit censored cases or treat their stopped estimates as unbiased.

Primary operational proxy: Delta=d milliseconds, with an illustrative 5% service
deadline-miss limit. This is a prespecified slow-cycle per-task budgeting example,
not a claim that 5% is an acceptable FTQC system failure probability. A padded
p95 prediction <=Delta admits a task. A measured miss-probability lower confidence
bound >5% identifies a counterexample to that admission rule under the sampled
conditions. Use exact binomial intervals, Bonferroni-adjusted across all 48 cases,
for this exploration; report per-session results and IID assumptions. CPU and
wall exceedances are reported separately.

Also mark p95 underpredictions of at least 1.5x, including quantile uncertainty.
Mean errors and bootstrap intervals are descriptive because rare work can be
poorly sampled. Do not call a high p95 prediction score a worst-case guarantee.

## Mechanism and inference

After uninstrumented data is saved, choose up to six complete cases with the
largest padded p95 underpredictions and at most 8,000 mechanism columns. Replay
the four slowest and four first shots per selected case on a separate
statistics-enabled decoder. Collect BP
convergence/iterations, LSD cluster sizes, growth/merging counts, and available
LSD elapsed-time statistics. Also replay BP and standalone LSD separately, checking
their combined correction against the integrated decoder. Instrumented times are
not headline service times. Record actual statistic field meanings; retain the
native elapsed counter as unit-unverified if its C++ timing definition is absent
from the installed package. Use explicit CPU/wall clocks for stage diagnostics.
Preserve correction/outcome consistency checks. Selection of slow shots cannot
estimate population cluster-size frequencies.

Compute stable, relabeling-invariant diagnostic descriptors: maximum arity,
degree moments, prior-weighted excess arity, and moments of expected detector
activation. Do not use realized syndromes or decoder statistics as compile-time
inputs. Keep all such descriptors out of the frozen predictor. Measure their
extraction cost. Explain residuals by axis, feature-range violations, training
support distance, BP work, and large LSD clusters. These relationships generate
hypotheses for fresh future test programs; they do not establish a new model.

## Fresh confirmation

After discovery, select at most six complete cases with the largest padded p95
underprediction ratios, prioritizing confident falsely admitted cases. Break
ties by canonical case name. Run 3 fresh sessions of 1,000 shots for each selected
case, with distinct seeds and the same CPU cap. Selection is adversarial and
reported. Use simultaneous binomial/quantile intervals over selected cases;
confirming selected failures does not estimate a population error rate.

Do not refit to make discovered failures disappear. Deliver a failure map,
confirmed counterexamples if any, explanations with explicit limits, and a
decision on whether added structure warrants a separate development/test study.
