# Research scoping brief: decoder-cost modeling

16 November 2026. For discussion with a human researcher working on QEC decoder
performance or fault-tolerant compilation. This is an evidence brief, not a
submission abstract, claim of novelty, or request for endorsement.

## Objective

Identify one consequential, accessible research question before collecting more
data. The project initially asked whether inexpensive graph summaries improve
compiler-facing decoder-cost predictions beyond problem size. A subsequent
selective-profiling proposal did not pass its consumer/cost gate.

## Evidence we currently have

- In pinned CPU BP+LSD experiments, the tested graph summaries did not improve
  p95 prediction over strong nonlinear size/sparsity/noise/activity controls.
  This does not establish that all structural representations are unhelpful.
- Some mean-runtime prediction results improved, but a constant burst-placement
  rule matches the point-best choice in all eight inspected bridge pairs.
  We have not demonstrated a useful learned scheduling decision.
- Fixed-noise predictors and historical padding can fail under changes in noise
  priors even with unchanged H/L. Derived activity/prior densities explain an
  important confound. Noise dependence itself is not a novelty claim.
- At a diagnostic 2 ms budget, selective profiling's recorded partial saving
  is 1.838 s over 19 tasks. On the ten tasks passing the retrospective pilot
  quality screen it is 0.201 s. At 5 ms every frozen filter profiles all tasks.
  Costs are incomplete and these are development sensitivities.
- Original circuit-build costs are substantial, while required accuracy checks
  and valid caching may already supply timing information. No matched real
  planner trace, workload horizon or application-derived contract was established.

The numerical/provenance checks passed. See the [completed gate report](../consumer_gate_2026-11-16/findings.md).

## Limits that matter

Current inputs are public circuit-derived tasks using a single detector sector
and logical-Z output. They are not a full Pauli FTQC accuracy evaluation.
Timing is warm single-thread CPU service on one host. All measured programs are
development data; there is no final independent-program result or measured
quantum-execution benefit. No external human researcher has reviewed the work.

Prior art includes [PACE](https://arxiv.org/html/2608.11719v1) for decoder-aware
scheduling and volume-model limitations, and the [LSD paper](https://arxiv.org/html/2406.18655v2)
for decoding mechanisms and runtime characterization. Generic noise dependence,
runtime variability, scheduling, calibration and selective information acquisition
cannot be presented as new contributions. The [novelty audit](../novelty_feasibility_2026-11-16/assessment.md)
documents additional overlaps.

## Three questions for the discussion

1. **Which real decision needs better evidence?** Can you identify a compiler or
   decoder-qualification workflow where an existing cost approximation makes a
   consequential wrong choice? What output, workload unit, hardware context,
   service/accuracy requirement and alternative baseline define that choice?
2. **Can we obtain a representative reproducible workload?** Is there a public
   circuit generator or trace with appropriate detector/observable scope and
   pinned decoder settings? Which assumptions in our current corpus would make
   conclusions irrelevant to that workflow?
3. **What specific result would add knowledge?** Would a controlled transfer/
   failure-boundary study of existing cost models answer an unanswered question,
   or does the literature already cover the meaningful effect? What simplest
   experiment could distinguish those possibilities?

## Decision after feedback

Continue only with a written problem statement, an accessible workload, a strong
baseline and an observable meaningful consequence. A model-validation benchmark
is a candidate question, not an established salvage paper. A new ML architecture
is not required if an established method addresses the identified problem.

If no such question emerges from this bounded scoping cycle, select a different
main paper project and retain this work as a technical record. Further training
or a larger corpus is not the next deliverable. No outreach or new measurements
were performed in preparing this brief.
