# Skeptical assessment of the decoder-cost study

13 November 2026. Prepared in response to the request for an external point of
view. This is an internal reviewer-perspective assessment by the same assistant,
with separate numerical checks and a primary-source literature check. It is not
independent external peer review.

## Verdict and decision

The study has a defensible model-specific failure result, a useful measurement
artifact, and an exploratory signal that extra program/noise coverage can help
the structural model. It does not yet support a general topology-necessity claim
or a demonstrated compiler benefit. I would not recommend submission with the
current evidence. I would recommend one bounded validation gate before investing
in a larger training campaign or a more elaborate model.

The earlier recommendation to compare a nonlinear baseline remains necessary,
but was too narrow as a complete next step. Measurement precision, dataset
composition, decoder configuration, and an actual useful decision all deserve
explicit controls. More model fitting on the current corpus alone will not
resolve them.

We should also be precise about the learning-curve interpretation: underfitting
has not been established. Improvement after adding programs is compatible with
more data, new domain coverage, and changed regularization; the larger model's
training/held-out gaps are compatible with overfitting or distribution shift.
Model bias and variance can coexist. We should have separated these alternatives
before putting substantial interpretive weight on the negative feature result.

## New checks performed for this review

The checks reused existing raw physical-circuit timing samples; they collected
no new decoder timings and did not update the original frozen predictors.

- Reproduced all 125 complete configuration-level mean/p95 labels from raw files.
- Reproduced the pooled learning-curve endpoints, then refitted endpoints using
  each of three sessions separately and ten deterministic equal-precision draws.
  The latter use 256 old shots per session rather than 2,000, matching the
  discovery precision of 768 pooled shots. All original data remain preserved.
- Checked 434 sensitivity jobs' outer metrics and reproduced 36 nested fits with
  separate sklearn/Cholesky pipelines. Maximum log-prediction discrepancy was
  1.93e-12. All earlier manifests still match, including the original 905 entries.
- Screened 134 saved detector matrices for undetected single mechanisms and
  equal-detector-support pairs with different logical signatures. No cases
  were found. This is a restricted projected-DEM screen, not a proof of circuit
  distance, full Pauli accuracy, or fault tolerance.
- Inspected all eight existing d5/four-block spread/burst schedule pairs and
  recorded their primitive instruction counts and illustrative budget outcomes.

See `precision_and_context.json`, `sensitivity_summary.json`,
`sensitivity_checkpoints.json`, `checks.json`, and `compiler_candidate_screen.json`.

## Main threats to interpretation

### 1. More training also changed what the model had seen

**Observed design limitation.** The original data use one physical noise setting,
two/four blocks, and twelve rounds. New data introduce other parent maps, six
blocks, other temporal extents, and independent noise variation. Adding those
examples improves coverage as well as sample count. The mixed-noise learning
curve therefore does not isolate a generic effect of training quantity.

The fixed-noise analysis removes one confound, but at its endpoint the base model
wins on four-block programs on average (1.05776 versus 1.07081 for the full graph
model); the full graph model wins on the six-block subset (1.02668 versus 1.07181).
Each six-block parent has only one measured configuration. Equal weighting of
parents is a declared valid aggregation choice, not evidence that the advantage
is uniform across workload types.

**Required control:** balanced configurations across block counts, noise, size,
and parents; distinguish within-domain learning from transfer to new domains.

### 2. Tail targets have uncertainty, sometimes substantial

**Observed measurement limitation.** Under the stated IID/stable-context reference
model, the median ordinary 95% p95 interval's full width is 1.26% of the estimate
for the 6,000-shot old labels and 8.95% for the 768-shot discovery labels. The
median largest/smallest session p95 ratio is 1.029 and 1.047 respectively. One
complete large discovery case has a session p95 ratio of 5.68. Rare expensive
shots also make the mean unstable: the top 1% account for as much as 67.6% of
total recorded time in one complete discovery case.

An individual label interval wider than an aggregate model difference does not
prove the aggregate difference is absent. It does mean that comparing small
point-estimate gains without propagating uncertainty is insufficient.

**What the new sensitivities show:** all ten equal-precision draws preserve the
fixed-noise pattern (full graph slightly better; sampled-feature-omitted graph
slightly worse) and the mixed-noise advantage of both augmented models. Unequal
precision alone did not remove these patterns in the declared checks. These
draws overlap heavily and are not independent experiments or a confidence bound.

Session-wise p95 endpoint factors illustrate the remaining sensitivity:

| Domain / target session | Base | Full graph | Graph, sampled feature omitted |
|---|---:|---:|---:|
| Fixed noise / 0 | 1.09144 | 1.09144 | 1.09400 |
| Fixed noise / 1 | 1.06190 | 1.05288 | 1.05575 |
| Fixed noise / 2 | 1.06041 | 1.05258 | 1.06087 |
| Mixed noise / 0 | 1.14269 | 1.10896 | 1.14229 |
| Mixed noise / 1 | 1.12437 | 1.10070 | 1.09611 |
| Mixed noise / 2 | 1.12765 | 1.11151 | 1.10691 |

**Required control:** comparable target precision, repeated randomized timing
blocks, and uncertainty that includes parents and timing contexts. Use resource
caps and explicit censoring rather than pretending every expensive task has a
well-estimated quantile.

### 3. Measurement cohort and operational mode are not fully isolated

**Plausible, untested alternative.** Old and new targets come from different
campaigns. Case randomization within each campaign helps, but is not an
interleaved old/new bridge experiment. The wrappers also differ: the stress
wrapper reads CPU time as well as wall time. Its empty-control overhead is
about 0.7 microseconds, too small to explain millisecond-scale misses by itself,
but hardware frequency, thermal state, and background activity were not fully
controlled across cohorts.

Shot timing is warm, serial, and reuses a decoder. This is a legitimate service
measurement, but not a cold start, concurrent shared decoder pool, accelerator
implementation, or online end-to-end controller. The lag-one log-timing screen
showed no large adjacent correlation (maximum absolute value about 0.15), which
neither proves IID nor excludes slower contextual drift.

**Required control:** a small randomized bridge remeasuring representative old
and new tasks in the same sessions; clearly define the operational mode the
compiler is predicting. Do not attribute cohort effects to topology without it.

### 4. The selected graph statistics are not all of topology

**Observed representation limitation.** The inputs are selected summaries, not
the full graph. The sampled two-step statistic depends on row numbering and the
fixed-noise result is sensitive to omitting it. Conversely, a decoder can itself
be sensitive to row/column order, so a descriptor-invariance check alone cannot
establish runtime invariance. A permutation experiment would need to transform
H/L, priors, syndromes, and correction interpretation together.

Base features are also highly correlated in the old fixed-noise design: log1p
detector and mechanism counts correlate at about 0.9991, and nonzeros with expected
activity at about 0.9967. Predictive fits can remain accurate in that domain while
their separate noise/size responses are poorly identified.

**Required control:** invariant descriptors for primary structure claims, an
equally tuned nonlinear base model, and the same cheap density transformations
for both feature sets. Improvement from a correlated proxy need not demonstrate
that base information is fundamentally insufficient. No single alternative
model class can establish universal information sufficiency either.

### 5. The decoder configuration may be part of the explanation

**Plausible, untested alternative.** The experiments fix BP at at most 30
iterations before LSD. That is appropriate for a configuration-specific cost
study. It does not establish that this setting gives a competitive cost/accuracy
tradeoff on every transversal workload. A larger BP budget could avoid some
expensive postprocessing, or simply add cost; we have not tested which occurs.
This is a decoder-iteration question, distinct from cost-model fitting time.

The LSD paper already studies runtime changes with physical noise and BP iteration
count, and reports long runtime tails. Expensive clusters and noise-sensitive
runtime are therefore mechanism context, not new discoveries of this study.
[LSD, discussion and Appendix C.4](https://arxiv.org/html/2406.18655v2).

**Required control:** a bounded configuration sensitivity on a representative
subset, with accuracy tracked, plus ordinary component decomposition where
applicable. A model-aware compiler should be compared with simple decoder-policy
choices, not only a fixed underperforming setting. A single-configuration paper
can remain valid if its scope and practical motivation are explicit.

### 6. There is still no demonstrated useful compiler choice

**Observed gap, central to the proposed paper.** All eight existing d5/four-block
spread/burst pairs have both measured p95s below the illustrative 5 ms budget.
The unchanged padded base model admits both members of every pair. Their
primitive instruction-target counts and 64-TICK counts also match. Tick counts
are not a physical duration model, but there is no demonstrated quantum-duration
speedup from choosing between these pairs.

Other confirmed timing-admission errors are real for the frozen predictor, but
their approximately 7–12% logical-Z failure fractions do not establish a useful
FTQC regime. Smaller p95 prediction error may therefore leave the compiler's
useful action unchanged. Ranking CPU service time alone is a narrower objective.

**Required control:** specify the actual decision, candidate semantics, accuracy
constraint, resource policy, and budget source before the next main experiment.
Use a predeclared budget sweep or an independently motivated budget. Do not place
a deadline between measured costs retrospectively to manufacture usefulness.

### 7. Per-task p95 is not a system deadline guarantee

**Scope and policy limitation.** A full-block service-time quantile excludes queue
waiting, data transfer, controller reaction time, correlations between overlapping
windows, and the number of tasks in a computation. Symmetric log prediction loss
also does not directly optimize the asymmetry between unsafe admissions and
conservative rejections. The historical maximum-error multiplier is an empirical
padding rule, not a distribution-shift guarantee.

**Required control:** keep the claim at service-time prediction until a stated
resource/queue/window model is evaluated. Independently calibrate every admission
policy on training/validation data and compare false admissions and rejections
together. Full two-sector accuracy and memory feasibility remain unvalidated.

The distinction between decoder service and system reaction time is established
in [Khalid et al., reaction-time architecture analysis](https://arxiv.org/html/2511.10633).

### 8. Prediction overhead and simple profiling can change the conclusion

**Observed cost; untested competitive comparison.** The archived full feature
computation has median cost 3.08 ms, or median 2.15 times a single corresponding
p95 decode call. DEM generation has median 17.75 ms and conversion 15.27 ms.
The initial unoptimized circuit builder has median cost about 5.30 seconds.
These are recorded total costs, not incremental costs of graph additions.
The later fragment assembler changes the construction situation.

These numbers do not invalidate an offline compiler: costs may be amortized over
many future decodes, and the base model also needs some of them. They do invalidate
an assumption that extra structural information is automatically free. A small
profiling sample, caching, or a calibrated conservative rule may be a better
decision method at comparable total cost. Heavy tails can also make small-sample
profiling unreliable; that tradeoff must be measured rather than assumed.

**Required control:** measure incremental feature and inference costs, count any
extra DEM generation, specify amortization, and include a bounded direct-profiling
baseline. Memory budgets need actual memory measurements if retained in the claim.

### 9. Repeatedly inspecting the same test corpus creates another overfitting risk

**Observed process limitation.** Nested validation protects each declared
hyperparameter selection from its own outer-test labels. It does not make the
outer data fresh again after we use their results to choose the next feature,
algorithm, noise point, or story. The current stress and learning-curve corpora
are development data. Thousands of fits and heavily overlapping orders do not
increase the number of independent parent programs.

The general risk of selection overfitting is documented by
[Cawley and Talbot](https://jmlr.org/papers/v11/cawley10a.html).

**Required control:** retain the full exploration record, freeze the final model
comparison, and reserve genuinely new parent programs for the final test. Label
all current gains and sensitivities as exploratory. Do not overwrite earlier
negative results or interpret a single favorable target as a general victory.

### 10. Novelty has not been established

**Literature boundary.** PACE explicitly identifies a volume-only extrapolation
that omits additional hyperedge-density/topology dependence; this justifies a
question, not a positive result. We have not reproduced its exact numerical cost
fits or scheduler, so our own volume baseline is not a direct PACE reproduction.
[PACE, section 7.6](https://arxiv.org/html/2608.11719v1).

Triage already considers resource scheduling, structural slice-degree costs, and
stochastic decoding latency. Slice-constraint-graph degree is not our detector-
hypergraph feature set, but generic graph-dependent costs or variable latency
cannot be claimed as new merely by changing terminology.
[Triage](https://arxiv.org/html/2605.04459v1).

Shared/elastic decoder capacity is also studied in
[Maurya et al.](https://arxiv.org/html/2406.17995), and LSD already supplies
noise/cluster-runtime mechanisms. A regression trained at one noise level failing
at another is not, by itself, a strong novel algorithmic contribution. A valuable
domain-specific systems result could still combine careful generalization,
inexpensive prediction, and consequential decisions; that combination is unproven.
The focused source review does not establish the absence of another relevant paper.

## What remains credible

The physical circuit sampling, stored correction checks, numerical fits, and
artifact preservation pass the tests performed. The frozen predictor's selected
admission counterexamples remain observed failures under the stated measurement
assumptions. Their existence does not depend on a newer structural model winning.
None of the new sensitivity diagnostics removes those measurements.

No obvious numerical or low-weight projected-DEM failure was found. This is not
certification of every assumption, an independent hardware reproduction, or a
proof that the projected circuit has its named fault-tolerant distance.

## Revised next step: one validation gate

1. **Define a useful decision first.** Specify same-program candidates, the
   logical-quality metric, what is optimized, the service/queue scope, and the
   budget source. Verify that the candidate set can plausibly change a useful
   action. If no such regime exists for these workloads, stop the compiler-benefit
   headline rather than search for a favorable arbitrary deadline.
2. **Use existing data for a bounded baseline control.** Run the proposed four-way
   linear/nonlinear and base/stable-graph comparison, with equal cheap noise
   information and fixed tuning procedures. Treat it as development only. Do not
   begin a broad search over architectures or add more inspected test cases as
   though they were fresh validation.
3. **Before a large campaign, run a small bridge/precision/configuration check.**
   Interleave representative old/new and four-/six-block tasks, repeat timing
   contexts, and test one alternative BP budget while tracking accuracy. Choose
   sample counts from precision around the actual decision, retain censoring,
   and measure incremental modeling versus profiling cost. This is calibration,
   not the reserved final test.
4. **Freeze and evaluate on balanced new reserved parents only if the gate is
   promising.** Equalize intended precision, vary noise independently, preserve
   program groups, and measure decision outcomes and overhead. Do not inspect
   test results while changing candidates, models, or thresholds.

Continue toward a structure-aware paper only if stable graph additions beat
strong calibration/profiling controls and improve useful fresh decisions. If the
better base model suffices, investigate a calibration/domain-validity contribution
only if novelty and utility are demonstrated. If neither affects decisions at
relevant quality and cost, reject this compiler contribution. That stopping rule
protects the research objective better than indefinitely improving a benchmark
score.
