# Bounded failure pilot completed — 17 November 2026

See [results](failure_pilot_2026-11-17/RESULTS.md),
[frozen protocol](failure_pilot_2026-11-17/PROTOCOL.md) and
[independent result audit](failure_pilot_2026-11-17/result_audit.json).

We followed the supervisor's bounded recommendation using the existing pinned
BP+LSD backend. The fixed 128 merged-weight-four patterns (64 connected, 64
uniform) were all decoded correctly at BP30/BP100 with both exact/additive priors.
There were 512 panel calls plus 13 adapters, 525 total, with no incomplete calls.
The search stopped without expanding the panel or changing settings.

BP failed to converge in 185 panel calls; LSD produced correct complete results
on every such call. This is fallback working, not full-decoder logical failure.
No failed cases triggered the repair phase. Verified forced-LSD order-zero and
combination-sweep order-two adapters establish path operation only, not repair
headroom or novelty. No new decoder or predictor was built.

Independent recomputation checked all saved outputs. Deterministic Stim replay
checked the labels of all 128 injections; 123 have nonzero true logical flips.
Exact/additive priors and iteration caps changed some corrections but no logical
classifications. All 17 earlier manifests were verified unchanged. No random
physical-noise samples, model fits, training samples or reserved programs were
used. The execution process used approximately 7.77 CPU seconds.

The full-decoder failure-witness feasibility gate remains unmet. This small
enriched panel neither rules out rare failures nor estimates natural LER/p95.
Stop this local search; it does not justify a failure-predictor training campaign
or a new compiler/publication claim.
