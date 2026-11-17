# Frozen headroom diagnostic — 17 November 2026

## Question, data and target

Does the pinned published Python full one-free-variable branch repair any of
the twelve verified BP20+OSD0 logical failures? This is a replication/feasibility
experiment, not a new decoding method. No new shots, BP calls, native decoder
calls, noise settings, training or manuscript are authorized by this protocol.

Reuse the complete frozen `natural_noise_reproduction_2026-11-17` artifact,
including H (1800x12240, rank1794), priors and full-precision BP20 LLRs. Use
unmodified `osd_internals.py` and `adaptive_v1.py` primitives at public commit
`8cc32014a6461bb8f241f47f62a7e74f63817738`. Do not call their experiment runner,
`evaluate_shot` or `verify_against_decoder`: these would run BP again and/or
fail to enforce our gate. Import only reviewed pure-NumPy helper functions.

Freeze 24 case IDs before any real-case helper execution: all twelve primary
logical failures, plus the first six primary-correct, BP-nonconverged cases by
ID from each original 256-shot seed block. These are predetermined diagnostic
controls, not matched causal controls or new independent physical samples.
Process the union in ascending case-ID order. Save selection and all hashes
in `frozen.json`, including this protocol, risk review, runner, source and cached
inputs. No outcome-dependent replacements, seed search or added configurations.

The target is the **published Python stable-order 1FV branch anchored to a
matching native baseline**, not a claimed reconstruction of hidden native
OSD-CS pivot internals. Exact e0 agreement cannot prove pivot-set equivalence.

## Pre-experiment adapters and global reconstruction gate

Before real cases, independently verify packed matrix XOR semantics, word
boundaries and augmented columns. Use small dependent-row synthetic matrices
to enumerate syndrome-valid one-free-variable candidates directly and check
the source baseline, scores, positive-improvement rule, first-argmax tie rule
and zero-syndrome behavior. These are algebra adapters, not decoder trials.

For the actual H, verify packed bits exactly against the sparse matrix and
the prior independent GF(2) rank. For **all 24** selected cases, before **any**
real-case candidate search:

- Require finite float64 LLRs, correct array/configuration hashes, nonconverged
  cached BP, and valid cached native correction.
- Run source `osd0_information_set` using stable ascending raw-LPR order.
- Verify the order is a permutation, pivots distinct, reconstructed free bits
  zero, rank1794, all 1800 syndrome equations, and pivot columns forming the
  identity in the reduced rows. Verify the packed input is unchanged.
- Require reconstructed e0 to equal cached native OSD0 **bit for bit**.
- Record tie fraction and groups spanning the pivot/free boundary. Do not
  equate same e0 with same hidden native pivot set.

On **any** mismatch, stop the entire headroom comparison with an adapter-failure
report. Do not drop a case, change sorting, substitute a new baseline or run
comparative real-case searches for the others. Partial gate coverage is visible.
Save each completed gate result and algebra, allowing inspection without reruns.

## Full search and independent numerical checks

Only after every gate passes, use the source score/pick primitives to evaluate
all 10446 distinct nonpivot columns in their source order, plus the baseline
no-change option. Preserve the source `sum(log(1/p))` score surrogate and its
strict delta>0/first-argmax rules. No actual labels or logical matrix enter the
search worker or its selection functions.

Validate in chunks of at most 256 candidates, using independent H arithmetic
on all 1800 detector rows. Check every candidate's parity, including dependent
rows. Independently compute each candidate score from its XOR-flipped pivot
bits and selected free bit. Compare source deltas to direct scores with frozen
absolute tolerance 1e-8 plus relative tolerance 1e-12. No tolerance is chosen
from the observed outcomes. Selected full-vector scores must also agree and
be within that tolerance of the minimum direct candidate score including e0.

Preserve the source choice even for exact/near ties. Record best improvement,
second-best margin, candidate count near the best, and whether any decision is
within tolerance of zero. Numerical disagreement outside tolerance halts the
comparison; near ties are reported as sensitivity limits, not silently resolved
using truth. Exact candidate identities and delta arrays are saved.

K500 and K1000 outputs derived from the same enumeration are secondary descriptive
results. They are not separately timed truncated runs and are not used to pick
a winning search depth. Save corrections, chosen free-column IDs, scores and
directly measured reconstruction/full-search CPU/wall time. Independent checks
and I/O overhead are separately labelled. Cached BP/OSD time is not remeasured,
and no end-to-end latency or hardware-deadline claim follows.

## Resource containment and failures

One child worker processes one case at a time. Cap the run at 600 child CPU
seconds and 900 wall seconds, with a 1GiB child-process RSS operational ceiling.
Use a CPU resource limit, external wall/RSS monitoring and per-phase maximum-RSS
checkpoints. Watchdog helpers are verified with short controlled probes before
real cases. A sandbox restriction on read-only ps monitoring was detected in
preflight; the monitor will run with the required process-observation permission.

Record macOS maxrss in bytes and ps RSS converted from KiB. Include imported
libraries, NumPy arrays and temporaries in child RSS. This is not machine-wide
memory. Conservative allocation estimates and checkpoints reduce transient
overshoot risk; polling is not a guarantee of instantaneous hard containment.
Declare any detected cap overrun or killed/incomplete phase as resource-censored,
not a failed correction. Never expand budgets after seeing a rescue.

Expected largest source temporary is the float64 rank-by-free matrix, about
150MB, plus its uint8 form and packed algebra. Candidate verification must not
materialize a 12240-by-10446 candidate array. On watchdog failure, an exception,
invalid candidate or integrity failure, preserve the journal and stop.

## Audit, decisions and scope

After the worker has selected outputs without labels, independently apply H/L
and cached actual logical labels to classify every saved output. Verify hash
integrity, source rule/coverage, all gates, candidate parity/score certificates,
case selection and resource accounting; preserve all rescues and regressions.

- At least one verified full-search rescue establishes a recoverable pair on
  this testbed, not a bounded-distance guarantee or publication novelty.
- Zero rescues after all twelve failures finish stops this specific route.
- Adapter, mathematical or resource failures leave headroom unresolved.

No new natural LER, net improvement over all512, or population regression rate
can be estimated from this selected panel. Static H/L are shared across cases;
runtime BP features are not compiler inputs. No structural generalization,
compiler improvement, optimal decoding or publishable novelty is assumed.
