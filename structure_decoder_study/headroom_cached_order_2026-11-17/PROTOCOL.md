# New cached-order 1FV headroom diagnostic — 17 November 2026

## Question and fixed scope

Can the pinned known Python one-free-variable search, adapted to the saved
implementation-derived column orders, repair any of the twelve observed native
BP20+OSD0 failures? This is a feasibility diagnostic, not a new decoder or a
replication of the published stable-order branch. The previous stopped experiment
remains unchanged. Matching e0 does not expose hidden native pivot sets.

Use exactly the previous 24 selected cases: all twelve failures plus the first
six BP-nonconverged successes in each original seed block. Preserve ascending
case-ID order, all cached priors, raw LLRs, syndromes and native corrections.
These inspected development data are neither held out nor a random estimate of
regression probability. The controls are not causally matched to failures.

No new physical samples, native decoder/BP calls, training, changed noise,
replacement cases or expanded budgets. Import only the reviewed reconstruction
and score/pick functions from Adaptive-qLDPC commit
8cc32014a6461bb8f241f47f62a7e74f63817738. Do not execute its experiment runner.

## Freeze and preflight

Review implementation and audit before freezing and before real reconstruction.
Freeze this protocol, risk review, runner, independent audit, original case
selection, pinned source and cached inputs. Verify the original result manifests
and ordering diagnostic. Prepare separate worker inputs with only syndrome,
LLRs, native correction and saved order. True observables and L are reserved
for the separate postselection audit. Case roles never influence search.

The ordering arrays come from the completed ordering diagnostic; do not call
ctypes/qsort again. Require 12240-element permutations ascending in raw LLR.
Assign unique float64 rank priorities at these indices only to the sorting
argument of the unchanged reconstruction helper. Score candidates with the
original sum(log(1/p)) channel-prior surrogate, never those priorities.

Retain the previous algebra adapters (dependent rows, packed XOR and word
boundaries, positive and zero ties, zero syndrome), ten controller exit-status
checks and tiny wall/RSS/CPU watchdog probes. Adapters must pass before real work.

## Global gate and full search

Before ANY real candidate search, all 24 reconstructed e0 vectors must equal
their cached native corrections bit for bit. Verify rank1794, 1794 independent
pivots, identity pivot submatrix in reduced rows, zero free bits, unchanged
packed input, all 1800 syndrome equations and exact cached order. On any failure
stop the whole comparison; never omit a case or relax the gate.

Only after all gates pass, enumerate all 10446 distinct free columns in source
order plus the baseline no-change option. Preserve source strict-positive
improvement and first-argmax tie rules. Check every candidate's full syndrome
using Hpiv*rf=Hfree and independently score XOR-flipped pivot bits plus the
selected free bit. Use chunks <=256; no full ncols-by-nfree allocation.
Frozen score tolerances are atol=1e-8 and rtol=1e-12. Save the complete delta,
free-column, pivot-reconstruction and direct-score arrays, all three outputs
(full primary; K500/K1000 secondary) and near-tie diagnostics. Record even
unfavorable results. K500/K1000 are derived prefixes, not separately timed runs.
Require surrogate scores to be nonincreasing as the candidate budget grows;
logical correctness need not be monotone in that budget.

## Resource and measurement rules

One child worker, 600 CPU seconds, 900 wall seconds and a 1GiB child RSS
operational ceiling. Retain CPU limits, external ps wall/RSS monitoring, peak
RSS checkpoints, atomic result JSON and the corrected nonzero-exit handling.
macOS maxrss is bytes; ps RSS is KiB. Polling does not guarantee instantaneous
hard memory containment. A stop is unresolved/censored, never a failed rescue.

Measure reconstruction, full source score/pick, validation and derived-prefix
selection separately. I/O and imported-library overhead are in total worker
cost. Cached BP/OSD cost is excluded. No end-to-end latency/speedup claim.

## Independent post-run audit and decisions

Before logical classification, a separate script must inspect saved evidence,
not import the experiment or source helpers. Recreate explicit full candidate
vectors in chunks <=128, use int64 H arithmetic for all 1800 rows, and compute
scores by weighted sums of those full vectors. Check complete ordered coverage,
baseline/gate integrity, first-argmax/strict-positive choice, every saved output,
journal sequencing, successful exit, resources and all frozen input hashes.
Use a separately declared 600CPU/900wall/1GiB audit budget with the same monitor;
this verification cost is not decoder time. Audit failure prevents a scientific
conclusion and does not authorize budget expansion.

Only after saved choices are fixed, apply L and cached true observables to
classify rescues/regressions. Report the logical-class sensitivity of candidates
within the frozen score tolerance of the minimum, without changing selections.
Verify all prior manifests remain unchanged. Ask the AI supervisor to review
design, execution evidence and interpretation after this independent audit.

A rescue proves an observed recoverable example, not novelty, a population
gain, optimal decoding or a distance guarantee. Zero rescues after all twelve
failures finish closes only this particular search route. Any failed check or
resource stop leaves headroom unresolved. This single H/L cannot support a
structural compiler claim. Finish with an explicit research go/no-go decision;
do not automatically start a larger dataset, router or manuscript.
