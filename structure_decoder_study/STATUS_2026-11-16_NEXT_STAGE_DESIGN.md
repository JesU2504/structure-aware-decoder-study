# Next-stage design — 16 November 2026

See [the detailed plan](next_stage_design_2026-11-16/PLAN.md) and
[the draft consumer contract](next_stage_design_2026-11-16/consumer_contract.json).

The immediate next stage is a bounded consumer/full-cost investigation using
existing evidence. No new parents, model fitting or decoder timing is needed
until that establishes a consequential use case. Current Gate 0 is not passed.

New design controls: exact-task caching, an efficient profiler, measurement-only
early stopping, and fixed-order search if the consumer needs just one feasible
schedule. The learned filter must retain useful outputs, not merely reduce the
number of profiles. Every admission requires applicable profiling/cache evidence;
model discards are not certified infeasibility.

A conditional existing-task cost experiment precedes any fresh-program pilot.
The pilot and a possible confirmation study are distinct: eight families cannot
establish a low unseen-family failure rate. Sample sizes must reflect uncertainty,
multiplicity, context and logical quality. Unresolved labels remain unresolved.

Recovered records: the historical 186-fit job took 5.463 seconds and used 125
examples from 19 groups; this does not measure deployment fitting or label
acquisition. No previous cost claims or manifests were changed.

The design's deterministic calculations are in
[planning_calculations.json](next_stage_design_2026-11-16/planning_calculations.json).
They are illustrative sample-planning arithmetic, not empirical power or a
frozen consumer contract. This work made zero new decoder calls and zero fits.
