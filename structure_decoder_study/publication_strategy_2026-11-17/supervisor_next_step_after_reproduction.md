# AI supervisor: next step after the reproduction

17 November 2026. Advisory review only; no new decoding, sampling, fitting, or installation. This is internal AI supervision, not external human peer review.

**My first-ranked recommendation is one small repair-headroom experiment: apply the existing published full one-free-variable search to our frozen failures.** We now know the decoder fails; we do not yet know whether these failures are repaired by the actual stronger branch studied in the close prior. That is the most useful remaining feasibility question before investing in a repair-oriented project. Do not enlarge the dataset or train a predictor now.

## The concrete task

Use all **12 verified BP20+OSD0 failures**, plus **12 predetermined primary-success controls**: the first six BP-nonconverged successes by case ID from each seed block. Freeze those IDs before any stronger-search results. These are diagnostic controls, not a representative sample or matched causal comparison. All 24 cases already have cached BP20 LLRs, native OSD0 corrections, syndromes, and actual logical labels. Reuse them; no new natural-noise shots or BP calls are needed.

Use the pinned `osd_internals.py` and `adaptive_v1.py` primitives from commit `8cc32014a6461bb8f241f47f62a7e74f63817738`. Reconstruct the information set, score the full **10,446 free-variable candidates** using the source's `sum(log(1/p))` surrogate, and retain the source-selected full-search correction. K500 and K1000 outputs can be extracted from the same enumeration as secondary descriptive results. This is a free-variable search with pivot re-solving, not a single-physical-qubit search or an exhaustive maximum-likelihood decoder.

**The entry gate is exact reconstruction of the original baseline.** On every selected case, the reconstructed order-zero correction must match its cached native OSD0 correction bit for bit. The source uses stable NumPy sorting and explicitly notes potential ties with native C sorting; its `evaluate_shot` does not enforce this check itself. If any case mismatches, stop the comparative analysis and report the adapter discrepancy. Do not discard that case, silently replace the baseline, or continue treating it as the same search. All selected cases are BP-nonconverged, so the source's BP-convergence early return does not suppress this test.

Preserve source candidate selection without access to actual logical labels; use those labels only for independent final H/L scoring. Save selected candidate identities, scores, correction vectors, syndrome residuals, and all rescues/regressions. Measure full reconstruction/search wall and CPU time directly. The source estimates K-prefix timings from a full sweep; do not report those estimates as measured truncated-search latency.

Process one case at a time. A **10 CPU-minute / 15 wall-minute management cap** and **1 GiB working-memory ceiling** are reasonable conservative design choices, not validated power or runtime guarantees. Record incomplete cases and stop at the cap; do not expand budgets based on whether a rescue appears.

## Decision rules

- **At least one independently verified full-search rescue:** the testbed contains an observed recoverable failure pair. That passes this narrow feasibility gate. A repair on one observation is not a bounded-distance guarantee, and any regressions must remain visible. Do not automatically launch a 512-shot sweep or fitting campaign.
- **No rescue after all 12 failures pass reconstruction and finish:** stop pursuing this specific baseline/1FV repair route for now. Do not infer that the shots are uncorrectable or keep escalating search orders until something works.
- **Reconstruction mismatch, invalid correction, or resource stop:** the headroom comparison is unresolved. Resolve the implementation/access issue without interpreting it as algorithmic failure.

The 12-failure/12-success selection cannot estimate the new natural logical-error rate, net benefit across all 512 shots, or population regression probability.

## What this does—and does not—advance

This is a bounded replication/feasibility experiment. [Adaptive decoding through decoder disagreement](https://arxiv.org/html/2609.37629v1) already studies this stronger branch, selective search, and correctness/cost tradeoffs. Reproducing a rescue, substituting LSD, or adding a predictor would not establish novelty. A publishable continuation would still need a distinct mechanism or systems claim and independent validation; we do not yet have that claim.

The original compiler question also remains open. These cases share one static H/L graph, so they cannot establish structural generalization across compiled tasks. BP state and syndrome features are runtime information. Compiler relevance would additionally require varied valid circuit-derived tasks, features available when the compiler makes its decision, and an actual decoder-budget decision that changes usefully. Keep that boundary explicit rather than presenting this repair diagnostic as a compiler result.
