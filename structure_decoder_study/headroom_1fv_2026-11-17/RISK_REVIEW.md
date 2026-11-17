# Adversarial review before the 1FV experiment — 17 November 2026

This reviews the main identifiable ways the experiment could mislead us. It
cannot prove that every possible error has been anticipated. Each technical
check below has a concrete failure action; passing one check does not silently
validate a different claim. No real-case reconstruction or search preceded this
document. The AI supervisor independently reviewed the pinned source and raised
the pivot-equivalence and dependent-row concerns included here.

| Risk | Consequence | Check or restriction before interpreting results |
| --- | --- | --- |
| Wrong cached case/configuration or stale vectors | Compare a different decoder or observation | Verify prior snapshot, per-call array hashes, source commit and case/config IDs; copy arrays; freeze selection before reconstruction |
| Case selection follows new rescue outcomes | Cherry-picked apparent success | Use all twelve known primary failures and first six BP-nonconverged primary successes from each seed; no replacements |
| Cached LLRs lack precision or have nonfinite values | Different ordering or undefined search | Require stored float64, finite length 12240; do not reconstruct from reduced-precision features |
| Stable Python sorting differs from native tie order | A different baseline appears to be repaired | Require bit-identical e0 on every selected case, globally before any real search; record ties; halt on mismatch |
| Identical e0 is mistaken for proof of identical native pivots | Mislabel Python search as native OSD-CS | Target the pinned Python stable-order branch only; record pivot/free tie groups; native pivot equivalence remains unproven |
| Incorrect rank or six neglected dependent rows | Invalid candidates pass a partial solve | Verify rank1794; check H e0=s and every candidate against all 1800 rows |
| Packed-bit/endian/word-boundary error | Corrupt reconstructed constraints | Exact sparse-to-packed-to-bits comparison; toy word-boundary, duplicate-COO XOR and augmented-syndrome checks |
| Information-set reconstruction mutates shared input | Later cases inherit state | Hash packed input before/after; isolate one case at a time; verify permutation, distinct pivots, zero free bits and pivot identity |
| Wrong free-variable coverage or K convention | Call a partial search full | Require 10446 distinct free columns, all non-pivots in source order; include e0 as the no-change option |
| Candidate formed with unsafe scatter assignment | Wrong parity when flips overlap | Pivot and free sets must be disjoint; independently verify every candidate's full syndrome in bounded chunks |
| Fast delta formula or float cancellation is wrong | Wrong winning correction | Compare all source deltas with direct XOR-candidate weighted sums under frozen tolerance; verify selected full-vector scores |
| Nearly tied/zero improvements | Fragile apparent rescue | Preserve source argmax, first tie and strictly-positive rule; record margins/near-ties; do not use truth to break ties or claim a unique optimum |
| Wrong likelihood objective | Overclaim optimal decoding | Preserve source sum(log(1/p)) surrogate; no claim of exact Bernoulli likelihood, ML decoding or minimum physical fault weight |
| Actual logical labels leak into candidate selection | Oracle-guided rescue | Worker receives H, priors, syndrome, LLR and cached e0 only; actual labels and L are used by the later audit, not search selection |
| Stronger search introduces errors | Report rescues while hiding regressions | Retain all twelve success controls, all outputs and transitions; never select controls by stronger-search outcomes |
| Resource exhaustion or partial coverage | Treat censored runs as algorithmic failures | Child-process CPU/wall/RSS watchdogs and start/completion journal; record censoring separately; no adaptive budget increases |
| Memory metric units or scope are wrong | Claim a memory guarantee not measured | macOS maxrss is bytes; ps RSS is KiB. Report child process RSS only, not whole-machine or Python allocation size |
| Transient memory overshoot escapes polling | An operational ceiling is called hard containment | Conservative allocation estimate, watchdog polling and maxrss checkpoints; report any detected overshoot, not a guarantee of zero instantaneous overshoot |
| Cached fast path or K timing is counted incorrectly | Misleading latency/speedup | Measure reconstruction and full search directly; exclude cached BP/OSD cost explicitly; no prorated K latency or end-to-end claim |
| Selected 24-case panel is treated as natural sampling | Unsupported population improvement | Conditional diagnostics only; no new LER, net512-shot benefit, or population regression probability |
| Known-data reuse is called held-out validation | Overstate prediction/generalization | All cases are inspected development data; no model is fitted or evaluated here |
| One rescue becomes a distance, topology or compiler claim | False scientific contribution | No correction-radius, structural-causation, across-task or compiler-benefit claim; the source circuit extracts Z checks only |

The high-priority stop gates are input integrity, independent math adapters,
all-case native-e0 equality, candidate validity, score consistency and resource
coverage. An implementation or resource failure leaves repair headroom unresolved.
It is not evidence that the original logical errors are uncorrectable.
