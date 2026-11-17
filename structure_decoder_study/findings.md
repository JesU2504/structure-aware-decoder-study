# First experimental findings

12 November 2026. **The proposed added-topology contribution is not established
by this pilot.** The volume-only model misses material variation, but a simple
sparsity/activity model is substantially stronger. The selected extra structural
features do not improve held-out p95 prediction. This is a useful research gate,
not a publication-ready positive result and not a proof that topology is irrelevant.

## What was completed

- Pinned and preserved public TMCBS source, without modifying upstream code or
  installing new packages into earlier projects.
- Ran 39 upstream code/circuit tests successfully.
- Generated 78 physical circuit/DEM instances at distances 3, 5, 7 and 2/4 blocks,
  covering eight program families and three placements of nonempty programs.
- Checked noiseless behavior, custom logical-Z truth tables, CSS/logical pairing,
  exact DEM-event reconstruction, representative circuit/DEM marginals, and an
  independently implemented matrix conversion. The upstream converter and the
  independent converter agree on this corpus.
- Collected 468,000 physical shots in three separately sampled, shuffled timing
  sessions. No invalid correction was observed. Saved all per-shot timing,
  iterations, convergence, logical-Z failure flags, and correction checkpoints.
- Independently replayed all 468,000 physical samples and checked 7,445 stored
  corrections against their detector and observable parities. Input/source/code
  hashes passed the raw-file audit.

The corpus is explicitly restricted to the public generator's **logical-Z
detector sector** and full-block decoding. It does not measure full Pauli logical
failure, sliding-window response, memory feasibility, or hardware decoder timing.

## Primary held-out result

All distances and placements of a held-out program family are excluded from
training. The table reports exp(mean absolute log prediction error), averaging
families equally. **1.0 is ideal.** These factors are not MAPE, confidence bounds,
or an admission-risk guarantee.

| Inputs, fixed ridge alpha=1 | Mean latency error factor | p95 latency error factor |
|---|---:|---:|
| Volume and distance | 1.4315 | 1.2846 |
| Detector/fault counts and distance | 1.4226 | 1.2717 |
| Counts + nonzeros + prior sum + expected activity | **1.1815** | **1.0758** |
| Above + selected degree/arity/connectivity features | 1.1866 | 1.1437 |

The richer model's p95 result is worse in every independently timed session.
On the 54 single-component cases, the simple and richer p95 factors are 1.0996
and 1.1450, respectively. Training a larger feature model on this small corpus
does not establish useful structural prediction.

At equal distance/block count/round count, mean latency spans up to 6.11x and p95
spans up to 4.16x. These extremes compare different logical programs, not two
implementations of one program. They establish cost variation, not compiler speedup.

Median per-case session maximum/minimum ratios are 1.050 for mean and 1.029 for
p95. The 95th percentile of those ratios is 1.268 and 1.088, respectively. Mean
estimation is less stable because rare expensive shots contribute substantial work.

The simple model is **not yet safe for budget admission**. For
`d7_q4_cycle_late`, measured p95 is 10.788 ms while its held-out simple-model
prediction is 6.036 ms: an underprediction factor of 1.79. The richer model also
misses that case. Across the descriptive deadline grid, maximum misclassification
fractions are 20.5% (volume), 6.4% (sparsity/activity), and 9.0% (richer features).
Those curves use measured-range deadlines and uncalibrated predictions; they do
not demonstrate a controlled operational risk or real compiler benefit.

## Model sensitivity, explicitly post hoc

The fixed-ridge result was followed by nested family-held-out selection of alpha
from 0.01, 0.1, 1, 10, 100. All outer-family outcomes are excluded from parameter
selection. Local structural and component-only additions are reported separately.

| Inputs with nested regularization | Mean factor | p95 factor |
|---|---:|---:|
| Simple sparsity/activity | 1.1645 | **1.0572** |
| Plus local degree/arity features | **1.1329** | 1.0663 |
| Plus component features | 1.1897 | 1.0778 |
| Full structural feature set | 1.1860 | 1.1177 |

The small mean gain for local features does not survive the connected-only
sensitivity: there, simple/local factors are 1.1826/1.2184 for mean and
1.0761/1.1207 for p95. These exploratory controls identify limitations of the
present evidence; they do not authorize a new positive headline selected after
seeing results. The initial analysis also required a recorded metadata-merging
implementation correction before any fitting; the frozen original is preserved.

## Ordinary component decomposition is a mandatory baseline

The corpus contains nine fanout/repeated pairs with exactly equal detector count,
fault count, nonzeros, prior sum, and expected activity, but different components.
A fresh paired control ran both joint and sequential componentwise decoding on
54,000 physical shots, using the same BP/LSD settings and alternating execution
order. These are 108,000 execution-form observations, separate from the primary
468,000-shot campaign.

On disconnected repeated-gate cases, componentwise decoding gives a median
**1.57x mean service-time speedup**, ranging from 1.46x to 1.79x across nine pooled
cases. Median iteration-weighted nonzero work decreases by a factor of 1.81.
On single-component fanout controls the median speedup is 1.000x (range
0.983-1.004x). Whole-operation logical-Z failure indicators agree for both forms
on all 54,000 paired shots. This finite check is not a guarantee of identical
corrections, arbitrary Pauli accuracy, or population failure probability.

Independent replay/parity checks also passed for this control, including 2,810
stored correction checkpoints. Component setup cost is saved separately.
The decomposition method is established practice. It changes the granularity
of decoder tasks and must precede or accompany a fair compiler cost comparison.
Its speedup is not evidence that the proposed richer prediction model is novel.

An initially suggestive exact-size mean gap is also sensitive to new physical
samples. For d7 spread fanout/repeated, the primary mean ratio is 1.52; in the fresh
component-control joint runs it is 1.05. The p95 values are nearly equal in both
campaigns. Rare slow events require much more care than a single paired mean.

## Slow-shot replay: the extremes involve decoder CPU work

A separate, explicitly selected-extreme diagnostic replayed the ten largest
individual primary wall times, plus matched median shots, three times each.
All syndrome and logical-Z failure checks reproduced. The extreme shots
originally took 525-720 ms. Their median replay CPU/wall ratios were
0.992-0.996, and replay wall times remained close to the original times.
Thus these selected extremes involve substantial decoder CPU work; treating them
as ordinary operating-system scheduling noise would be unjustified.

In the d7 spread-fanout case, the ten slowest shots out of each 2,000-shot session
account for 25.6%, 40.7%, and 44.8% of measured decoding time. This helps explain
why mean cost is harder to estimate than p95. Selected-extreme replay does not
estimate their probability, validate a particular heavy-tail distribution, or
establish that static topology predicts the missing tail cost. Those questions
require fresh, larger samples and an adequate control corpus.

## Costs and scope before a larger campaign

Public Python circuit construction is slow in this harness: median 5.30 seconds
per case. Median DEM construction is 17.75 ms, matrix conversion 15.27 ms, and
feature extraction 3.08 ms. These are setup measurements, not service time.
Any compiler benefit must account for them and compare against direct profiling.
Feature construction from an already built DEM is not a free online oracle.

CPU: Apple M1 Pro, 10 heterogeneous cores, 16 GiB RAM, arm64 macOS. Decoder/library
versions and thread settings are recorded. There is no core affinity or dedicated
server isolation, and no FPGA/ASIC extrapolation. p99 remains diagnostic only;
current shots do not establish extreme tail probabilities or rare logical-error
equivalence. Current schedule variants have equal round counts, so no
quantum-duration improvement can be claimed.

## Decision

**Do not advance the original added-topology paper claim on this evidence.**
Preserve the artifact and the negative/qualified outcomes. The next useful gate
is an independent, realistic circuit/window corpus with full detector/observable
coverage, fixed detector-basis conventions, and task decomposition. Test the
strong simple baseline and an independently calibrated safety margin first.
Proceed to a larger structural model only if residual errors then cause useful
same-program schedule decisions and inexpensive added information corrects them.

If the simple decomposition-aware model remains sufficient in that setting,
retire the proposed topology contribution. A broader empirical paper would need
an independently valuable result and additional evidence; the present pilot
alone does not establish that alternative.

## Artifacts

- `PROTOCOL.md`, `frozen_config.json`, and `source_review.md`: initial scope and provenance.
- `validation.json`, `upstream_checks.json`: correctness gates.
- `results/analysis.json`, `results/predictions.csv`, `results/pilot_overview.png`:
  held-out results and figure.
- `ROBUSTNESS_PROTOCOL.md`, `results/robustness.json`: nested sensitivity check.
- `COMPONENT_CONTROL_PROTOCOL.md`, `results/component_control/`: paired control.
- `results/audit.json`, `results/component_control/audit.json`: independent replay/checks.
- `ANALYSIS_AMENDMENT.md`: versioned implementation correction.
- `results/slow_replay/`: selected-extreme CPU/wall replay diagnostic.
- `literature_matrix.md`, `PAPER_STATUS.md`: prior-work boundaries and outstanding claims.
