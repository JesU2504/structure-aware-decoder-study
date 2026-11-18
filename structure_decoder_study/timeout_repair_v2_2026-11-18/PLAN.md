# Timeout-return repair V2 — 18 November 2026

This is an explicitly versioned engineering correction after V1 failed its
hard-CPU containment expectation. Preserve the entire frozen V1, its failed
audit and its V1_OUTCOME.json. Do not change its expectation after observing
the result. No quantum/research cases, decoder runs or physical samples.

V1 demonstrated controlled return preservation, but its spin fixture with
active OS RLIMIT_CPU [1,3] continued to about 7.9 CPU seconds until the external
8-second wall watchdog terminated it. The cause is unresolved. V2 retains the
OS limits but adds independent parent monitoring of cumulative process CPU.
Local macOS ps(1) documents TIME as accumulated user+system CPU time.

Use worker.py and result_guard.py byte-for-byte from V1. Reuse the already
selected V1 n=200/.15-second independent-set fixture; no new calibration or
solver parameter search. Freeze after independent AI supervisor preflight.
Run exactly the same nine scenarios once, in the same order: timeout without
incumbent; timeout with incumbent; legacy injected signal; deferred injected
signal; n=6 optimum; soft CPU; hard CPU; wall guard; late persistence.
The last four make no optimizer call. The late-persistence payload is a mock.

Monitor only the owned fresh child PID using ps pid/rss/time, with a one-second
query timeout, strict PID/format validation and recorded raw CPU tokens,
timestamps and samples. Malformed or missing data for an active child fails
closed. Retain 1GiB RSS and 8-second wall limits (wall fixture .15 seconds).
Parent CPU budget is 3 seconds for the hard-CPU fixture and 10 for all others.
At a threshold crossing send SIGTERM only to the owned child, then SIGKILL if
not reaped within .5 seconds. Record actions and triggering sample. Budget
termination always censors results, even if output files exist. A signal-
preserved return has its own classification and is never ordinary success.

V2 adds at most nine children and five synthetic optimizer API attempts.
V1 used eleven children and seven API attempts (2 calibration + 5 confirmation).
Thus at most twenty children and twelve API attempts across both versions.
V2 controller cap is min(85,120 minus recorded V1 controller wall seconds),
and another child requires at least ten seconds remaining. Combined measured
controller execution must remain <=120 seconds. No retries or unlisted runs.
Interruptions leave any started run censored and require a new protocol before
additional attempts; a partially populated confirmation folder cannot resume.

Independently audit all raw synthetic graph constraints/objectives, exhaustive
n=6 optimum, signal injection timing/PID, raw persistence, stable final signal
ledger and handler restoration, source/old-output hashes, process censoring,
monitor CPU parsing and parent termination at the threshold. The hard-CPU
check now tests parent CPU containment, not the failed OS-only assumption.
Require observed CPU in [3,3.5] seconds at termination and final spin telemetry
near that threshold; wall fallback cannot substitute for this check.

Success establishes these controlled return paths and containment on this
machine. It does not identify the historical signal origin, demonstrate every
platform or race, validate an RSS-limit crossing, make MILP tractable, improve
a decoder or resolve the two earlier inconclusive research cases. Those cases
remain untouched; a future rerun needs a separate reviewed protocol.

Primary semantics: [Python signals](https://docs.python.org/3.12/library/signal.html),
[resource limits](https://docs.python.org/3.12/library/resource.html),
[SciPy milp](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.milp.html).
