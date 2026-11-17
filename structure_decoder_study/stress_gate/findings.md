# Frozen-model failure boundary: 13 November 2026

## Main result

The old sparsity/activity model survives substantial new-program and window
variation, but its noise transfer and large-size extrapolation can fail. A further
targeted challenge also defeats a simple marginal feature-range warning. Two selected timing-admission errors repeat
on fresh samples even after applying the historical safety margin. Expensive
selected replays are dominated by LSD work and large dynamically formed clusters.

This establishes a failure map for a particular CPU decoder cost model. It does
**not** establish that added static topology features are the right repair, that
the counterexamples are useful FTQC operating points, or that the original paper
claim is ready. The strongest counterexamples have poor logical-Z accuracy.

## What was frozen and tested

Before new timing, the archived B2 ridge predictor was fitted on all 78 old
instances. Its inputs are distance, detector/mechanism counts, nonzeros, prior
sum, and expected detector activity. The mean and p95 targets use separate fits.
No coefficient was updated from new observations. The historical p95 safety
factor, about 1.787, is the maximum old leave-group-out underprediction with
single/repeated logical-CNOT motif labels merged. This is an empirical historical
envelope, not a guarantee for new domains.

The discovery corpus contains 48 connected tasks from 12 new logical programs:
eight four-block/six-CNOT programs and four six-block/eight-CNOT programs. Ideal
maps are unique up to simultaneous block permutation and exclude the old map
classes. Axes vary noise, temporal extent, distance, blocks, and burst/spread
placement. The scope remains full-block TMCBS logical-Z decoding, not sliding
windows, full Pauli accuracy, or a hardware decoder.

A source-fragment assembler literally reproduced all 78 old circuits before
being used. All new parent programs passed d=3 computational-basis truth tables
and both logical-Pauli conjugation checks for their gate sequences. New circuits
passed ideal-detector and sampled DEM-parity checks. The public source was not
modified.

The service-budget example is Delta=d milliseconds with a 5% per-task miss limit.
This is an illustrative modeling target, not an acceptable FTQC logical-failure
rate, a deployment requirement, or a full-system latency guarantee.

## Case accounting and correctness checks

| Phase | Cases | Planned physical shots | Observed physical shots |
|---|---:|---:|---:|
| Discovery | 48 | 36,864 | 36,777 |
| Fresh selected confirmation | 6 | 18,000 | 16,191 |
| Intermediate-noise boundary tests | 6 | 18,000 | 18,000 |
| Targeted marginal-feature-box challenge | 2 | 12,000 | 12,000 |
| Total | 56 distinct new circuit configurations | 84,864 | **82,968** |

The confirmation cases reuse discovery circuits; they are not six additional
unique circuits. CPU caps censored one large case in discovery and one in
confirmation. Every observation is retained. Stopped estimates are descriptive;
their ordinary binomial/quantile claims are suppressed.

All measured corrections passed syndrome consistency checks. The separate audit
replays all 82,968 physical samples and verifies 2,938 stored correction checkpoints
across all 186 case/sessions; see `results/audit.json`. Frozen hashes pass. This is internal
checking using separate code, not external peer review or an independent simulator.

Miss-rate intervals use exact binomial calculations with the phase-specific
multiple-comparison adjustments declared in the protocols. Their interpretation
assumes independent shots and a stable measurement context. Repeated sessions
provide a reproducibility check on this machine, not coverage across hardware,
background workloads, or future deployment conditions.

## Where the frozen model remained robust

Thirty-six discovery cases have every B2 input within its old marginal range.
Across these cases:

- Largest p95 underprediction: 1.169x; largest p95 overprediction: 1.133x.
- Largest mean underprediction: 1.323x; largest mean overprediction: 1.377x.
- No multiplicity-adjusted confident padded timing-admission error was found.

Marginal ranges are not the same as joint-distribution support. These observations
do not prove safety for all within-range graphs. They do show that this particular
stress campaign did not reveal a large hidden structural failure in that group.
Changing programs, block count, or placement alone was not enough to make this
simple predictor fail materially in that initial group. This observation does
not survive as a claim that marginal feature ranges ensure validity: the later
targeted challenge below produces a counterexample.

The historical margin also produces six confident conservative rejections in
discovery. These are potential lost admissions under the illustrative timing
target, not demonstrated quantum-execution speedups or missed useful schedules.
The result illustrates the tradeoff between safety padding and resource use.

## Freshly confirmed counterexamples

Both cases below have d=5, four blocks, ten rounds, spread placement, p=0.003,
and a 5 ms illustrative deadline. Each has 3,000 fresh confirmation shots.

| Program | Raw predicted p95 | Padded predicted p95 | Measured p95 | Measured miss rate |
|---|---:|---:|---:|---:|
| q4_P01 | 2.691 ms | 4.810 ms | 7.705 ms | 8.9% |
| q4_P03 | 2.695 ms | 4.817 ms | 8.807 ms | 10.1% |

The simultaneous pooled miss-rate intervals over the six selected confirmation
cases are 7.58-10.36% and 8.70-11.64%, respectively. Both also exceed the 5% limit
in every session using the separately adjusted session intervals. The raw and
historically padded predictors admit both tasks; the measured service distributions
contradict that admission under the stated assumptions.

These are selected counterexamples, not an estimated population error rate.
Their logical-Z failure fractions are 11.63% and 10.87%. Consequently, they do
not demonstrate a useful FTQC schedule-selection benefit. Logical accuracy must
remain an explicit gate in any paper-level experiment.

## Locating the noise boundary without changing graph structure

For q4_P01 and q4_P03, additional p=0.0015/0.0020/0.0025 tests each collected 3,000
fresh shots. H, L, and the noise-free physical circuit match each p=0.001 reference
exactly. Only physical probabilities and DEM priors change. Model coefficients
remain fixed; all padded predictions at these rates remain below 5 ms.

| Program | p | Observed miss rate | Phase-adjusted interval | Relative to 5% target |
|---|---:|---:|---:|---|
| q4_P01 | 0.0015 | 1.60% | 1.06-2.31% | Below |
| q4_P01 | 0.0020 | 3.13% | 2.36-4.07% | Below |
| q4_P01 | 0.0025 | 5.33% | 4.31-6.51% | Unresolved |
| q4_P01 | 0.0030 | 8.90% | 7.58-10.36% | Above |
| q4_P03 | 0.0015 | 2.10% | 1.47-2.89% | Below |
| q4_P03 | 0.0020 | 4.57% | 3.62-5.67% | Unresolved |
| q4_P03 | 0.0025 | 6.97% | 5.80-8.28% | Above |
| q4_P03 | 0.0030 | 10.10% | 8.70-11.64% | Above |

Thus q4_P01 has tested below/above points at p=0.002/0.003, while q4_P03 has them
at p=0.0015/0.0025. Intermediate points are genuinely unresolved where indicated.
These are empirical selected-task brackets using phase-specific adjusted
intervals. No exact critical noise rate, monotone law, universal decoder threshold,
or joint 95% interval for a continuous transition is claimed.

At p=0.0025 the observed logical-Z failure fraction is about 7.33% in both tasks.
The quality limitation therefore remains even at an intermediate timing failure.

## A targeted failure inside all six raw feature ranges

The initial failures were range-flagged, so a further adversarial test challenged
that warning rule directly. Two selected tasks at p=0.0024 satisfy every old B2
marginal minimum/maximum, retain the same H/L and noise-free circuits, and are
admitted by the unchanged padded model. Their physical noise condition still
differs from the old p=0.001 training condition. Each collected 6,000 fresh shots.

| Task | Padded predicted p95 | Measured p95 | Miss rate | Adjusted miss interval |
|---|---:|---:|---:|---:|
| q4_P01 | 4.650 ms | 5.319 ms | 5.43% | 4.80-6.13% |
| q4_P03 | 4.656 ms | 6.006 ms | 6.37% | 5.68-7.11% |

The q4_P03 case contradicts the 5% timing admission rule despite passing the raw
feature-range check. q4_P01 is unresolved under that criterion. These are selected
counterexamples, not a general error-rate estimate. Logical-Z failure fractions
are 7.60% and 7.13%, respectively, so the usefulness limitation remains.

An input-only diagnostic was calculated during the challenge before inspecting
its outcomes. Although raw sums and counts are individually within range, their
ratios are not:

- Mean mechanism prior is 0.004146, versus an old maximum of 0.001960.
- Expected detector activation density is about 0.055, versus an old maximum of
  0.02787.

Thus a raw feature box can hide a substantial noise-density shift. These ratios
are derived from existing B2 inputs and add no new information. They identify a
joint-support/calibration issue; the study does not prove a static-topology
omission. A warning using these ratios would flag the selected examples, but its
general coverage, false-abstention rate, and decision value are unvalidated.

## Mechanism evidence

Forty-eight selected replay shots span six discovery tasks. Standalone BP
followed, when needed, by standalone LSD reproduces all integrated corrections.
A separate statistics-enabled decoder also reproduces every correction.

Among the 24 selected slow replays, the median standalone LSD fraction of combined
BP/LSD replay CPU is 96.25%. One d7 replay takes about 658 ms of standalone LSD
CPU versus 5.87 ms of BP CPU, with a recorded final cluster of 3,007 mechanism
bits. This is consistent with expensive cluster growth/factorization making
cost depend on more than bounded BP iteration work.

Selection deliberately overrepresents slow shots. These figures cannot estimate
population cluster frequencies. Standalone API/weight-copy boundaries differ
from the integrated call, so the fraction is a diagnostic proxy rather than an
exact partition. Instrumented timing is not headline service time. The native
elapsed counter's units are unverified and are not used as time measurements.

## What we infer about failure

1. **Noise response was weakly identified by the original training design.** All
   old data used p=0.001. Good predictions as size changed do not establish a
   valid response to an independent noise change. This was predicted before
   stress measurements and is directly challenged with H/L held fixed.
2. **An accurate-looking p95 model can miss expensive-work mixtures and means.**
   Rare large LSD clusters require explicit uncertainty assessment. Large-size
   extrapolations also hit CPU caps; their stopped estimates cannot be used as
   ordinary population quantile estimates.
3. **Historical padding and marginal ranges do not constitute domain validity.**
   Initial confident admission errors were range-flagged, but the targeted
   feature-box challenge produces an unflagged one. Derived noise-density inputs
   expose the hidden shift. This is evidence against the sufficiency of the
   simple range guard, not validation of a replacement guard.
4. **Static topology is not yet shown to be the missing predictive input.** The
   noise-localization graphs are unchanged. Noise/topology interaction remains
   possible, but insufficient training variation or a nonlinear response could
   explain failure without a richer graph model. Diagnose those alternatives first.

## Decision for the research direction

The next repair to test is broader, controlled calibration of noise/size response
and an abstention/profiling policy outside validated support. Use new reserved
parent programs for that test. Compare an interpretable nonlinear or two-part
BP/LSD model with the same simple inputs before attributing residuals to missing
topology. Test added graph descriptors only if a consequential residual remains.

The added-topology paper claim still has not earned support. The within-range
robustness, easily flagged extrapolation errors, standard decomposition baseline,
and poor accuracy of current counterexamples all argue against forcing that
headline. A useful publication needs a relevant accuracy regime, a real
same-program schedule decision, adequate uncertainty, and benefit beyond simple
calibration/padding/profiling after overhead is counted.

## Reproducibility qualifications

The extra clock-read wrapper has about 708 ns median wall overhead in the empty
control; it is not subtracted. CPU-clock quantization can give zero in that empty
control. Ordinary decoder observations remain separately checked.

See `ANALYSIS_QUALIFICATIONS.md` for masked censored logical-accuracy intervals,
`CONFIRMATION_AMENDMENT.md` for the secondary fixed-prefix safeguard, and
`CONFIRMATION_PROVENANCE_NOTE.md` for a dependency snapshot recorded after launch
following an import failure. The declarations/model/primary analysis are retained;
there is no external preregistration claim.

Key outputs: `results/failure_map.png`, reviewed discovery/confirmation summaries,
`results/boundary_summaries.json`, `results/mechanisms/replays.json`, and
`results/feature_box_summaries.json`, `results/density_diagnostic.json`, and
`results/audit.json`. Raw data, frozen predictions, programs, circuit/DEM files,
source-fragment validation, hypotheses, and all protocols are retained.
