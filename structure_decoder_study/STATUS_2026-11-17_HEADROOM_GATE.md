# Headroom comparison stopped and audited — 17 November 2026

See [results](headroom_1fv_2026-11-17/RESULTS.md),
[risk review](headroom_1fv_2026-11-17/RISK_REVIEW.md),
[check status](headroom_1fv_2026-11-17/RISK_OUTCOME.md),
[independent audit](headroom_1fv_2026-11-17/result_audit.json) and
[AI supervisor review](publication_strategy_2026-11-17/supervisor_headroom_postcheck.md).

The planned pinned Python 1FV diagnostic used all twelve original failures and
twelve predetermined successes. Before search, its global native-baseline
equivalence gate passed eight cases, then stopped at case51: four correction
bits differ. Fifteen gates and all24real searches remain unattempted.

Independent audit confirms the mismatch, correct stop behavior, unchanged frozen
inputs and all nineteen previous manifests. All four differing columns have
identical LLRs/priors across Python pivots/free variables. Both corrections are
syndrome-valid, logically equivalent and still wrong in nine logical bits;
the scores agree up to roundoff. Tie handling is a plausible cause, not proven
without native ordering evidence. This is not a new rescue or a refutation of
the published study.

Pre-run review also caught and corrected a controller exit-status bug before
execution, preserving v1 and freezing v2. All resource/toy/exit adapters passed.
Real full-search parity/score validation was not reached. No resource cap was
hit; no new native decoder calls, physical shots, training or manuscript occurred.

Repair headroom remains unresolved. Do not relax the bit-match gate or infer
no repair is possible. Any next task should diagnose baseline ordering before
a separately justified comparison. The earlier 12/512 native reproduction is
unchanged.
