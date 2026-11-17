# Stage 1: public-workload and cost-variation pilot

Protocol established 12 November 2026 before the timing campaign. This is an
exploratory entry study, not the confirmatory paper experiment.

## Question and scope

Do valid public circuit-derived decoder tasks exhibit reproducible service-time
variation that remains useful to predict after dimensions, sparsity, and expected
activity are included?

Use TMCBS commit `c0490fa63965d8984cca89deb8826c19c46e8a3c`, unmodified.
Its surface builder declares Z-stabilizer detectors and final logical-Z
observables. X-stabilizer measurements are present but do not have their own
detectors. Thus this pilot characterizes **one detector sector and the supplied
logical-Z output metric**, not full Pauli logical failure or a full two-sector
online FTQC decoder. Full-window block decoding is used; sliding-window commit
and boundary handling remain later work. These limitations must accompany results.

Use the existing workspace Python environment read-only. Record the complete
package freeze and machine information. Do not install or modify prior projects.

## Circuit corpus

Use the pinned public `make_builder` and its syndrome-extraction circuit.
Distances 3, 5, 7; 2 and 4 code blocks; 12 extraction rounds. Initialize and measure
all blocks. All preparations are logical zero for timed experiments. Apply each
listed logical CNOT in its listed order; retain that order across timing variants.

For 2 blocks: memory, a single CNOT, and three repeated CNOTs on the same pair.
For 4 blocks: memory, two disjoint CNOTs, a directed chain, fanout, fanin, a directed
cycle, and three repeated CNOTs on one pair. Unused blocks are intentionally
retained, and component structure is measured. Test both full joint matrices and
connectivity controls before attributing a benefit to topology.

Nonempty programs have three event placements: early compact, spread, late
compact. Their total extraction-round count is identical. Duplicate memory
variants are omitted. This produces 78 cases. Their schedule variants implement
the same noiseless logical program, but have equal modeled duration in this
pilot. Consequently no quantum-duration speedup can be claimed from this corpus.
Unused components and one-sector restrictions limit its application relevance.

Physical noise p=0.001 at the builder's existing reset, measurement, gate, and
per-round locations. No erasure, distributed-link noise, or added idle channel.
The circuit files are the authoritative channel specification. Custom calls use
the builder's default gate noise. Full detector and observable sampling comes
from the physical Stim circuit, outside all decoder timing intervals.

## Independent matrix conversion

Use an independently implemented conversion of flattened, undecomposed DEMs.
Each error instruction is one Bernoulli mechanism. Detector and logical targets
combine modulo 2, including across separator hints. Mechanisms with equal complete
detector/observable support merge with p_xor=p1+p2-2*p1*p2. Different logical
supports stay distinct. Logical-only events are retained; null-support events
may be discarded. Conversion must be checked against sampled DEM error vectors.
Do not change the physical sampling model to match the decoder approximation.

The upstream converter adds duplicate probabilities rather than XOR-combining
them. Report whether this affects any circuit in the actual corpus; do not infer
an upstream paper error from a synthetic edge case.

## Correctness gates before timing

- Run the upstream code/circuit tests, including its logical-basis checks.
- Check the custom circuits' noiseless detector determinism and full logical-Z
  computational-basis truth tables at d=3. These are sector checks, not a proof
  of arbitrary quantum-program equivalence.
- Check CSS commutation and logical anticommutation on all three code distances.
- Check synthetic converter cases: duplicate probabilities, repeated targets,
  separator correlation, logical-only events, and repeat/shift flattening.
- Reconstruct sampled detector/observable vectors exactly from independent DEM
  error-event samples on all corpus circuits.
- Compare circuit and DEM detector/observable marginals on representative cases.
  Use a prespecified conservative six-standard-error tolerance with a small
  finite-sample floor. This is a consistency diagnostic, not a distribution proof.
- Require returned decoder corrections to reproduce input syndromes on all timed
  shots. Report any invalid correction and exclude no unfavorable valid case.

## Decoder configuration

`ldpc` 2.4.1 BP+LSD, minimum-sum BP, parallel update schedule (the CPU implementation
is serial execution of that message schedule), maximum 30 iterations, scaling
factor 0.625, LSD order 0 / LSD_0, one thread, no randomized serial order, and
statistics disabled for headline timing. Pass the DEM's per-mechanism priors.
These are explicit research settings motivated by LSD's documented example,
not a reproduction of TMCBS's default 10,000-iteration high-order settings or
PACE's benchmark.

Zero-syndrome shots call the same decoder API and remain in the distribution.
Report Python-to-C++ call overhead; do not subtract an estimated overhead from
the recorded latency. Time each `decode` call with `perf_counter_ns`; sampling,
matrix operations, feature extraction, initialization, and result checking are
outside that interval and separately accounted for.

## Sampling and repeatability

Use SHA-256-derived seeds with distinct namespaces for validation, warmup, timed
sampling, and run ordering. Three sessions, independently sampled 2,000 shots per
case per session, 32 separate warmup shots per constructed decoder. Run sessions
serially, shuffling case order independently each time; do not run multiple timing
workers. A small timing calibration may precede the campaign and must be marked
as excluded from fitting. Timed observations are fresh across sessions. Save
per-shot latency, BP iterations/convergence, logical-Z mismatch, syndrome weight,
and invalid-correction flags. Last three items are evaluation/diagnostic data,
not compile-time predictors.
Retain correction/syndrome/observable checkpoints for the first 16 and slowest
16 shots of each case/session, enabling independent sample replay and parity
checks without retaining every dense correction vector.

This initial 6,000-shot-per-case campaign screens mean and p95. p99 is diagnostic
only. Increase samples in a separately documented follow-up before claiming tail
calibration. Do not decide logical-error equivalence from small failure counts.
Memory profiling is deferred; no memory feasibility claim is authorized by Stage 1.

## Features and comparisons fixed before timing

B0: volume (blocks * rounds, with distance as a separate size setting).
B1: detector/fault counts and distance.
B2: B1 plus nonzeros, sum of mechanism probabilities, and expected detector
activation under the DEM's independent mechanism model.
B3: B2 plus row/column degree variance, hyperedge fraction, upper degree quantiles,
static component summaries, and a bounded two-step neighborhood statistic.

Fit log-target ridge models with standardized transformed features and fixed
alpha=1.0. Do not tune a large search on this small exploratory corpus. Report
leave-program-family-out results with all distances, block counts, and placements
of a held-out family excluded from training. This provides an exploratory family
transfer test; related chain/fanout/fanin and sector symmetry limit independence.
Include a connected-component-restricted sensitivity check before claiming
topology rather than simple decomposition. A later confirmatory study must add
independent programs and candidate sets.

Primary prediction errors: multiplicative error on mean and p95, with per-family
and per-session breakdowns. Descriptive admission decisions sweep deadlines across
the observed latency range with all models evaluated on the same grid. Raw
predictions are not claimed to be risk-calibrated. Compare validation-calibrated
padding only in a nested split large enough to support it. Stage 1 is insufficient
to establish controlled false-admission risk or an end-to-end deadline guarantee.

## Interpretation and next decision

Continue only if public-workload validation passes and residual cost variation is
reproducible enough to justify a larger, full-accuracy, realistic-window study.
Beyond-sparsity feature gains must survive family exclusion and timing repetition;
training fit alone is insufficient. If gains vanish after ordinary connected
component decomposition or a better simple baseline, record that outcome and
revise or reject the topology claim. No publication claim or chosen venue follows
from passing this entry gate.

Preserve source archive, source hashes, protocol/config hashes, full circuits,
DEMs, canonical matrices, split assignments, raw observations, and analysis code.
Record any protocol amendment before running affected new data.
