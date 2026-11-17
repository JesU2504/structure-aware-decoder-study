# Validation-gate findings

Prepared on 13 November; model audit, bridge measurements, and analysis completed
15 November 2026 (Asia/Tokyo client date). This is internal development/calibration
evidence, not a final reserved-parent test or external peer review.

## Decision

The gate does **not** justify expanding a topology-focused p95/admission paper
automatically. A modest nonlinear model using the original base information
outperforms graph-augmented models on held-out p95 prediction. In the bridge's
quality-screened schedule choices, the graph features add no demonstrated
selection benefit over that stronger base control.

This changes the interpretation of the earlier learning-curve result: extra
training helped the structural model, but that alone did not establish that it
needed extra graph information rather than a more suitable use of existing
inputs. Underfitting and overfitting are not uniquely diagnosed, and topology is
not proved universally unnecessary.

There is a separate **exploratory mean-latency signal** favoring nonlinear graph
features in some comparisons. It is preserved below. Switching the headline to
throughput would be a new hypothesis requiring a prospective decision experiment,
not successful completion of the prespecified p95 gate.

## What was completed

- Six model variants: linear/RBF-kernel ridge crossed with base6, density8, and
  graph16. The primary four-way comparison uses density8 and graph16. Density
  ratios are functions of base6 and add no new information.
- Nested parent/motif holdouts, training-only scaling and kernel/target centering,
  fixed parameter grids, and equal procedures across feature sets. There are
  186 outer model fits. The sampled row-sensitive graph feature is excluded.
- Nineteen bridge configurations, balanced across four-/six-block calibration
  parents, two noise rates, and burst/spread placement, plus three exact old
  references. Stable features passed 57 relabeling checks.
- Three fresh timing processes, randomized 64-shot blocks, paired BP30/BP100
  physical streams, and ordinary component decomposition for the disconnected
  memory reference.
- **29,184 new physical evaluation shots** and
  **59,904 evaluation decoder calls**; a disjoint
  **3,648-shot profiling stream**; and
  3,648 separate physical warmup shots. No resource
  cap stopped a configuration. Warmups are not evaluation observations.

No new final-test parents were opened. The new configurations use previously
inspected parents, so the bridge is calibration rather than unseen-program
confirmation. Old frozen predictions and measurement files remain unchanged.

## Stronger controls on existing development data

All table values are exp(mean absolute log prediction error), equally weighted
over held-out groups. One is perfect; lower is better. Models use log1p inputs
and log targets. The three columns are distinct declared evaluation domains.

### Primary p95 target

| Model | Original groups | Fixed-noise new parents | Mixed-noise new parents |
|---|---:|---:|---:|
| linear_base6 | 1.05553 | 1.06242 | 1.13135 |
| linear_density8 | 1.06465 | 1.06179 | 1.08065 |
| linear_graph16 | 1.13189 | 1.05997 | 1.06742 |
| rbf_base6 | 1.02942 | 1.04165 | 1.04518 |
| rbf_density8 | 1.03077 | 1.03970 | 1.04216 |
| rbf_graph16 | 1.07649 | 1.05093 | 1.05755 |

The primary nonlinear base-versus-graph comparison is 1.03970 versus 1.05093 at
fixed noise, and 1.04216 versus 1.05755 with mixed noise. Even the nonlinear model
with the original six inputs beats the graph-augmented controls in p95 here.
The very large improvement from the old mixed-noise linear base6 to linear
density8 also shows how a change of representation can help without new
information. This is a bounded model-class comparison, not an exhaustive proof.

### Secondary mean target

| Model | Original groups | Fixed-noise new parents | Mixed-noise new parents |
|---|---:|---:|---:|
| linear_base6 | 1.16960 | 1.17101 | 1.13565 |
| linear_density8 | 1.16721 | 1.14453 | 1.14355 |
| linear_graph16 | 1.13082 | 1.15814 | 1.24507 |
| rbf_base6 | 1.12812 | 1.11793 | 1.11339 |
| rbf_density8 | 1.13591 | 1.12021 | 1.11476 |
| rbf_graph16 | 1.12373 | 1.11758 | 1.09400 |

Nonlinear graph16 improves mixed-noise mean prediction relative to nonlinear
base controls, while its fixed-noise mean improvement over nonlinear base6 is
negligible. Linear graph16 is worse on the mixed-noise mean target. Thus neither
the feature set nor one chosen target should be declared a universal winner.

## Frozen-prediction bridge performance

Bridge predictions were recorded before new timing. Each calibration parent's
configurations are excluded from its fitted model and inner selection. Exact
old references use the corresponding original-motif outer fit; new calibration
parents use the corresponding mixed-noise new-parent fit. Both sides of a feature
comparison use the same data. The following aggregate gives equal weight to the
three old and four new parent groups; it is a calibration mixture, not a random
application-population estimate.

| Model | Mean error factor | p95 error factor |
|---|---:|---:|
| linear_base6 | 1.10204 | 1.23630 |
| linear_density8 | 1.11687 | 1.18655 |
| linear_graph16 | 1.14835 | 1.18292 |
| rbf_base6 | 1.07351 | 1.15565 |
| rbf_density8 | 1.09155 | 1.09400 |
| rbf_graph16 | 1.05270 | 1.13334 |

Restricting descriptively to the four new bridge parents retains the same
direction: nonlinear density8 versus graph16 p95 factors are
1.10502 versus 1.16272; mean factors are
1.08366 versus 1.07192.
The observed mean benefit is a development signal; heavy-tail mean uncertainty
and changed measurement context still need prospective treatment.

## Concrete same-program choices

The objective was CPU service p95 at matched logical action, distance, rounds,
and instruction/TICK counts. No quantum-duration improvement is asserted.
Candidate quality is shared across all policies using a retrospective one-sided
logical-Z upper-bound screen of 1% per whole task. This is a declared pilot screen,
not a full FTQC accuracy target or a deployable learned accuracy policy.

Four pairs have both alternatives screen-qualified; one further pair has only
one qualified alternative and three have none. The four nontrivial pairs are
all at p=0.0003, one for each calibration parent. Burst is the point-estimate
lowest-p95 variant in all four. Three cost orders have disjoint declared p95
intervals; the q4_P00 order is unresolved.

| Policy | Point-oracle matches (of 4) | Parent-balanced point regret factor |
|---|---:|---:|
| linear_base6 | 4 | 1.00000 |
| linear_density8 | 3 | 1.01345 |
| linear_graph16 | 2 | 1.06486 |
| rbf_base6 | 4 | 1.00000 |
| rbf_density8 | 4 | 1.00000 |
| rbf_graph16 | 3 | 1.01345 |
| profile_point | 4 | 1.00000 |
| profile_upper | 4 | 1.00000 |

The nonlinear graph model's wrong point choice is q6_P03, whose cost order is
interval-resolved; its selected spread variant has about 5.49% larger measured
p95 than burst. The nonlinear density8 base and direct profiling match all four
point oracles, including the unresolved one. This is four calibration choices,
not a population success rate or a proof of oracle equality. Uncertainty in the
finite measured oracle is retained.

## Admission is a tradeoff, not just prediction MAE

The full prespecified budget sweep is retained. Each cell below is **confident
false admissions / confident conservative rejections / total admitted**, among
the ten BP30 screen-qualified configurations. Miss-rate truth is unresolved where
its adjusted interval crosses 5%; unresolved cases are not counted as either
confirmed error. All nineteen-configuration counts and raw model variants are
in `bridge_analysis.json`.

| Budget ms | Nonlinear base, raw | Nonlinear graph, raw | Nonlinear base, padded | Nonlinear graph, padded | Profile upper |
|---:|---:|---:|---:|---:|---:|
| 0.25 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 0.5 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 1 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| 2 | 1 / 0 / 7 | 0 / 1 / 5 | 0 / 5 / 1 | 0 / 5 / 1 | 0 / 1 / 5 |
| 4 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 3 / 7 | 0 / 4 / 6 | 0 / 0 / 10 |
| 5 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 |
| 8 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 |
| 16 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 |
| 32 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 | 0 / 0 / 10 |

The 2 ms row must not be hidden: raw nonlinear graph16 has zero confident false
admissions versus one for raw nonlinear density8, but it admits fewer candidates
and has one confident conservative rejection versus zero. The graph model can
therefore look better on a selected risk metric while being more conservative.
This is not a matched-risk superiority result. Historical safety margins remove
that observed false admission but reject many feasible cases; the profile upper
bound has a different cost/conservatism tradeoff.

At the inherited illustrative 5 ms budget there is again no confident false
admission difference between the base and graph predictors. None of these
diagnostic budgets has been established as a deployment requirement. No useful
system-wide risk guarantee follows from service-time intervals.

## Decoder configuration alternative

Increasing max BP iterations from 30 to 100 increases measured p95 in all 19
configurations: the ratio ranges from 1.022 to
3.077, with median 2.964.
Median mean-CPU ratio is 1.990.
Across paired evaluation shots, 26 logical-Z outcomes improve and
25 worsen. Those pooled counts mix workloads; they do not certify
equal accuracy, noninferiority, or a globally optimal BP cap. This one alternative
does not support the concern that simply giving BP more iterations repairs the
observed cost behavior on the bridge.

Ordinary component decomposition on the memory reference gives p95 ratio
0.506 and mean-CPU ratio 0.709, with
0 improved and 0 worsened logical-Z outcomes. Its per-call timing includes
gather/merge work. This confirms a standard baseline's value for that case; it
is not a new decoder algorithm or a full-system speedup.

## Context and overhead

Across the eleven exact historical references, current/historical p95 ratios
range from 0.940 to
1.151, with median
1.009.
The interleaved bridge thus does not reveal a large uniform cohort multiplier.
Individual shifts and mean changes remain, and this does not isolate frequency,
thermal state, implementation ordering, syndrome uncertainty, or background load.

The optimized feature implementation's median recorded base-density time is
0.0391 ms and full stable-feature time 0.5786 ms. For comparison, median
timed service cost of the 192 profiling calls per configuration is
127.18 ms. These are different scopes: profiling initialization and
warmup, shared circuit/DEM generation, validation, and amortization must be counted
for an end-to-end comparison. Inference timings and construction metadata are
retained; these numbers alone are not an overhead-adjusted compiler speedup.

## Confidence and integrity qualifications

All 29,184 evaluation and 3,648 profiling physical streams were replayed. Every
one of 63,552 stored correction vectors was checked against the syndrome and
logical-observable outcome. All 186 outer-model split/metric records were checked;
18 nested fits and their margins were reproduced using separate sklearn code.
The audits passed and all earlier artifact manifests still match. This is internal
checking by the same assistant, not independent peer review or another simulator.

Intervals assume IID shots within a stable context. Repeated-process variation
is not proof of deployment coverage. Logical-quality and timing intervals are
separate adjusted families and do not form a joint 95% safety certificate.
Retrospective calibration eligibility and previously inspected parent identities
prevent calling the decision exercise a fresh compiler validation.

The original frozen-model noise-transfer failures remain intact; these newer
fits do not retroactively repair them. The work continues to cover a logical-Z
sector, full-block CPU decoding, and the specified implementations only.

See `RESUMPTION_2026-11-15.md` and `ANALYSIS_IMPLEMENTATION_NOTE.md`: the model work
predates bridge measurement, while analysis implementation was written after
measurement launch and before case-level outcome inspection. No external
pre-registration or external timestamp is claimed.

## Research disposition

Do not launch a large reserved-parent p95/topology campaign on the strength of
the earlier learning curves. The stronger base control and the concrete choices
remove its present justification. Preserve the raw admission tradeoff and the
mean-cost signal rather than selecting only a favorable metric.

If the project continues, choose explicitly between (a) decision-calibrated
transfer/profiling with strong base controls and matched risk, or (b) a new
mean-service/throughput hypothesis using the stable graph features. Either
requires a novelty check and a separately declared prospective utility test with
new reserved parents; neither is established as a publishable contribution by
this gate. Current data remain development evidence and the reserved test remains
unused. The original compiler headline has not passed its entry condition.
