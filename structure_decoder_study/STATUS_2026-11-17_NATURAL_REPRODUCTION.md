# Natural-noise reproduction completed and reviewed — 17 November 2026

See [results](natural_noise_reproduction_2026-11-17/RESULTS.md),
[independent audit](natural_noise_reproduction_2026-11-17/result_audit.json),
[failure packet](natural_noise_reproduction_2026-11-17/witness_packet/README.md)
and [AI supervisor review](publication_strategy_2026-11-17/supervisor_natural_noise_reproduction_review.md).

The pinned public BB144 24-round, p=0.007 Z-check-only memory setup passed all
24 construction/conversion checks and matched paper dimensions/rank. Source
H/L/priors equal the independent converter for this DEM. Eleven decoder
adapters passed after sample/job/source hashes were frozen.

512 natural circuit-noise shots were paired across native BP20+OSD0, BP+LSD30
and BP+LSD100. Each had twelve syndrome-valid logical failures and zero invalid
corrections, on the same twelve case IDs. Marginal Wilson 95% interval for each
observed fraction: 1.346%–4.052%. No comparative superiority or true-rate
equivalence claim is supported.

All 48 selected fresh-instance replay calls matched the original correction,
BP decision, flag, iteration count and classification. Forced LSD0/CS2 repaired
none of eight selected failures and damaged none of eight selected successes.
These are first-seed selected diagnostics with nearest available controls;
two matches have noticeable syndrome-weight differences. Broader repair
headroom remains unknown.

All 1,627 completed calls were independently checked using H/L and saved truth;
both 256-shot blocks regenerated bit for bit. No call was censored. Execution
used about 34.90 CPU seconds and 35.41 wall seconds. All eighteen earlier
manifests were verified unchanged. No new model, training sample, reserved
workload, installation or manuscript was involved.

The AI supervisor accepts the technical reproduction, finds no material
implementation defect and requests no more experiments for this milestone.
The failure-witness feasibility gate now passes. A novel publication question
and a consequential compiler decision remain unestablished.
