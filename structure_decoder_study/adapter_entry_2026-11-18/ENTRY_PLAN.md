# Concrete synthetic entry implementation — 18 November 2026

This fresh folder implements the previously reviewed prospective integration
protocol. Scope is **the fixed synthetic native entry only**. It provides no
research-case launch mode and does not read cases131/228 or their matrices.
The immutable preparation package and all earlier failures remain unchanged.

## Code and preflight evidence

The signal guard and accounting policy/check script are byte-identical to the
reviewed versions. Model helpers build_model/model_witness/validate_incumbent
are extracted exactly from the original probe, with unchanged INT_TOL1e-7.
They contain no native solver call. Freeze verifies exact function-source
equality and the dependency/interpreter identities already recorded.

New transport captures native returns, writes raw arrays through a temporary
file handle, then raw metadata/manifest BEFORE warning/status/vector checks.
An interpretation-start marker records that order. The recording signal ledger
stays active through raw/provisional persistence; authoritative final reports
follow handler restoration and a stable signal snapshot. Unknown/nonfinite
scalars are labeled, not silently treated as good solver data.

New monitor retains the owned Popen, validates raw pid/stat/rss/time with
before/after polls and query timestamps, and feeds the unchanged policy. It
records every observation and action, retains terminal CPU maxima, incorporates
checked child telemetry only after reaping and never queries a reaped PID.
Live monitoring errors stay errors after exit. Runtime/exit and control-test
verdicts remain separate; expected guard/fault processes stay censored.

The stdlib CPU/wall/RSS/Z/fault modes dispatch before native package imports.
RSS control allocates/commits fixed96MiB, with a preallocation baseline and
64MiB test threshold. The Z control burns.1CPU, blocks behind an owned stdin
barrier, requires a positive live sample, receives exit permission, and gets
one ps query after a fixed.05-second delay without intermediate poll/wait.
Failure to observe actual Z is an unmet requirement, without a retry.

The independent audit imports no worker/transport/model/policy/monitor helper.
It reconstructs process evidence and CPU/RSS accounting, exact rounded parity
equations, binary graph constraints, scores, exhaustive toy optima, raw/interpretation
order, stable ledgers, signal timing and native call counts from saved files.
Expected status2 applies only to the declared inconsistent toy; it cannot make
status2 a successful result for the known-feasible real task.

Preflight offline checks passed without optimization, worker or ps calls:
77 policy checks; exact helper equality; exhaustive toy feasibility; invalid
fractional-array rejection; labeled fake raw payload surviving a subsequent
unexpected-warning failure; warning sets for each mode; handler restoration.
Those checks do not substitute for the pending native entry.

## Fixed execution

execution_plan.json and configs/*.json declare the13 children in the prepared
order: four original parity toys, three fixed MIS native calls, mock persistence,
CPU/wall/RSS guards, controlled Z observation and controlled malformed live RSS.
Exactly seven optimizer attempts if all stages are reached; zero calibration,
retries, research cases, BP/OSD/LSD calls or physical samples.

Entry admission ceiling120 seconds; at least11 seconds must remain before
another child. Ordinary child thresholds CPU10/wall8 seconds/RSS1GiB and OS
request[10,12]. Dedicated CPU threshold3 with OS request[1,3]; wall.15; RSS64MiB
with fixed96MiB allocation. Monitor polling.01, query timeout1, terminal reap
grace.5, SIGTERM wait.5 and SIGKILL wait.5 seconds. Report actual thresholds,
responses and overshoot; no instantaneous-cap guarantee. No duplicate cleanup
cycle. Unreaped containment failure aborts the queue and retains owned identity.
Abrupt controller SIGKILL containment and OS hard-limit enforcement are unproved.

Any unexpected outcome aborts the remaining suite. A partial entry directory
blocks resumption/retry. All starts, returned raw data, expected censored controls
and missing observations remain recorded. A failure is not relabeled by a new
post-hoc exception. The independent audit and AI supervisor postcheck must
complete before claiming entry success.

The reviewer must inspect concrete code and provide PREFLIGHT.md/PREFLIGHT.json
before freeze/run. Preparation's old launch flags remain historical false;
the fresh review can admit only this synthetic entry. No scientific-value gate
is resolved by entry success, and no case131/228 solve follows automatically.

## Concrete review corrections before freeze

The supervisor found an early post-spawn cleanup gap. A try/finally now begins
immediately after Popen returns and covers launch metadata and Accounting setup.
Fallback cleanup uses the owned process directly, without requiring a monitor
state, trace writer or writable metadata. Offline fake-process checks cover
writable and deliberately unwritable metadata. They launch no OS worker.
The controller records watch exceptions/known spawn facts, counts atomic
optimizer-attempt markers even if an append-only journal is incomplete, and
aborts the queue. Initial offline artifacts are retained; revision r2 tests
the revised sources. One pre-freeze rerun was blocked by the existing initial
mock directory before any new payload; evidence is preserved in that directory.

Source/config gates bind the prepared protocol and all13 fixed settings.
The Z control requires a positive live query starting AFTER its ready/burn
marker. Warning-context setup and start-journal fsync precede the signal-ready
marker, which is placed immediately before the optimizer API callback.
An injected signal within that recorded API interval does not identify the
exact native HiGHS instruction or prove the historical signal's cause.

Independent audit checks CPU-signal PID/phase/active limits, signal-ready and
restoration timing, first crossing to requested-stop latency and measured
overshoot. Parent containment requires TERM with observed -SIGTERM exit, or
TERM timeout followed by the declared KILL action and -SIGKILL exit; a lone
TERM action with -SIGKILL cannot masquerade as demonstrated parent containment.
The RSS fixture is a fixed96MiB allocation ATTEMPT: the64MiB guard may interrupt
before completion. Its first observed crossing must follow allocation_start,
whose baseline must be below64MiB. Unobserved CPU after a last sample remains
unmeasured rather than being inferred as zero.

If a future authorized task is lengthy, background it with durable progress and
approximately20-minute checks while the resource watchdog remains continuous.
This120-second entry is expected to finish sooner and will be checked on completion.
