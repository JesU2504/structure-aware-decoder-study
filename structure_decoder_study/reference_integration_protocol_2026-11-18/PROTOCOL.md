# Prospective reference-adapter integration protocol

18 November 2026. **Preparation only. No native integration test or research
solve has been performed under this protocol.** This is an internal prospective
plan, not external preregistration, a manuscript or a new decoding method.
The prior failed and inconclusive runs remain frozen.

## Purpose and launch gates

The repaired signal guard preserved controlled native returns, but V1 failed
its OS-only CPU expectation and the original V2 audit failed a terminal-
accounting assumption. Its supplemental pass was explicitly post hoc. This
protocol defines state/exit/accounting rules before another experiment.

There are separate gates:

1. Preparation: freeze this plan, machine-readable limits/fixtures, policy
   prototype, deterministic checks, actual environment and AI review. This
   step grants no native or research launch authority.
2. Implementation: build a fresh versioned controller/worker/independent audit,
   review concrete code and freeze exact sources and binary identities. Reuse
   the previous parity model builder/validator and recording signal guard by
   hash; do not reuse the old solve() as an unchanged transport wrapper (see
   persistence rules below). Do not edit any old folder. The current policy prototype performs no
   process, solver, persistence or independent correction validation.
3. Native entry: execute the fixed suite below once under that exact adapter
   after implementation review. No calibration, retries, unlisted cases,
   concurrency or environment/solver tuning. Any missing expected observation,
   drift, invalid vector or UNEXPECTED monitoring/containment failure blocks
   the gate. Dedicated guard/fault controls pass only if the declared injected
   condition, censor reason, owned termination/reaping and no-promotion checks
   match. The process remains censored even when its control test passes.
   A new versioned review is required to change a failed design.
4. Scientific value: entry PASS does not launch research cases. Before any
   real solve, review and freeze a specific purpose. The old native logs
   reported no primal incumbent around 60 seconds on both cases. The same
   model/seed/budget may recover metadata but has low expected new scientific
   value. Distinguish an optional exact-input infrastructure replication from
   a different witness-search method, which needs its own scientific protocol.
   Do not raise budgets or restart because the answer is inconclusive.

`research_launch_authorized` and `native_entry_launch_authorized` remain false
in the preparation spec. These are readiness/scope indicators; this document
does not substitute for the missing implementation or its review.

## Fixed scientific question and optional replication envelope

If an exact-input replication is later selected and reviewed, only development
cases 131 then 228 are eligible, each once. This is oracle-assisted post hoc
diagnosis of inspected BB[[144,12,12]], 24-round, p=.007, Z-check-only observations,
not independent confirmation or a population sample. No new noise samples,
BP/OSD/LSD calls, model fitting, online intervention or compiler decisions.

Keep all 12,240 fault bits and 1,812 detector/logical parity equations, with
integral parity slacks, for 14,052 integer variables. Use the unchanged source
score S(x)=sum log(1/p_i)x_i with the frozen float64 coefficients; no log-odds
replacement, restricted graph, warm start, cutoff or alternate objective.
Before solving, verify the known saved correct-class vector in the full model
and the full-1FV wrong winner's detector/logical labels.

The threshold is the CURRENT full-1FV wrong winner, not the earlier OSD0 result.
For case 131 it is about 520.8767105141355; for case 228 about 450.11581399781005.
The best correct-class members in the saved list scored about 553.6291408940393
and 474.48544531198894. Frozen files and recomputed values are authoritative.

Keep solver time_limit=60 seconds, node_limit=10000, threads=1, random_seed=0,
presolve=True, mip_rel_gap=0 and mip_feasibility_tolerance=1e-8. Freeze forwarded
options and expected warnings. An ordinary limit without an incumbent permits
the second fixed case; an unexplained signal, validation/formulation error,
monitoring failure or containment failure aborts the remaining queue. A new
instrumentation fault is not a reason to expose the second case to the same
fault. Started-but-interrupted cases count as attempts and cannot be resumed.

## Native entry: thirteen fixed children, at most seven optimizer attempts

Use the exact shared transport and scientific model helpers planned for research.
Freeze model-helper equality and the expected options for each mode. Nonresearch MIS payloads test
native return handling; the parity fixtures test the scientific model adapter.
Neither alone substitutes for the other. All cases run sequentially, once.

| Order | Entry fixture | Optimizer attempts | Required observation |
|---|---|---:|---|
| 1 | integral_slack_required | 1 | Original two-bit parity toy, exhaustive optimum |
| 2 | dependent_cyclic | 1 | Original five-bit toy, exhaustive optimum |
| 3 | zero_syndrome | 1 | Original four-bit toy, exhaustive optimum |
| 4 | inconsistent_duplicate_rows | 1 | Original three-bit toy, expected infeasible |
| 5 | timeout_none | 1 | Fixed MIS n=200/seed2026111801/density.08/time0, status1/no incumbent |
| 6 | timeout_incumbent | 1 | Same MIS/time.15, status1/valid incumbent |
| 7 | signal_during_call | 1 | Same .15 fixture, owned-PID SIGXCPU after ready+.02; valid payload and signal record |
| 8 | signal_during_persistence | 0 | Labeled mock payload, guarded persistence, restored handler and stable ledger |
| 9 | parent_CPU | 0 | Stdlib spin, OS request[1,3], parent threshold3 CPU; preserved soft-signal record and parent stop |
| 10 | parent_wall | 0 | Stdlib wait, .15-second parent wall threshold; censored |
| 11 | parent_RSS | 0 | Fixed committed bytearray96MiB held in stdlib child; test-specific64MiB RSS threshold; censored |
| 12 | observed_terminal_Z | 0 | Bounded handshake, actual ps Z state, owned reaping, retained positive CPU highwater |
| 13 | malformed_active_monitor | 0 | Labeled controlled instrumentation fault; true live owned PID retained; fail closed and stop |

The four exact parity fixtures, all weights and exhaustive expected outcomes are
in entry_fixtures.json, extracted from the original entry source by AST literal
reading without importing or executing it. Parity toy options match the old
entry: time_limit2, node_limit1000, dispFalse; other scientific options unchanged.
MIS options retain the earlier repair settings (presolveFalse, gap0, one thread,
seed0, dispFalse); no new calibration. A different observed timeout outcome
fails the entry gate rather than justifying time/size tuning.
The known-feasible research execution classifier is not the expected-infeasible
entry control's verdict. Entry fixture4 has its own declared status2 check.
Dispatch stdlib guard/fault modes before native package imports; they exercise
the shared controller and accounting without a SciPy RSS baseline confound.

Every child normally gets parent CPU10/wall8 seconds/RSS1GiB and OS request
[10,12]. Dedicated CPU/RSS/wall cases use the table's lower test thresholds.
Entry controller admission ceiling is120 seconds, with at least11 seconds
remaining before another child. Actual end-to-end durations and any threshold
overshoot are retained; exceeding120 prevents a PASS. No child is launched
unless it has a full bounded termination/reaping allowance.

For the Z fixture, keep the child alive behind an owned IPC permission barrier.
After the .1-CPU-second burn, confirm Popen.poll()==None and obtain a validated
positive LIVE ps sample while the child remains at the barrier. Then permit
exit, wait a declared .05-second query delay
without poll/wait, query ps once, then perform the owned post-query poll/wait.
Require actual Z and no outcome-driven retry. It should consume a fixed .1 CPU
second before the barrier so a positive highwater can be checked. If Z is not
observed, mark the entry requirement unmet. This controlled choreography tests
the state transition, not the ordinary poll cadence. The fault fixture records
the real owned PID/state and the deliberately corrupted record separately;
it does not masquerade as a natural ps malfunction.

## Prospective process accounting

Target the current Darwin environment. ps(1) locally documents TIME as cumulative
user+system CPU and stat's leading states I/R/S/T/U/Z, with Z meaning dead/zombie.
Freeze the relevant local manual extract. Modifiers such as E are not an
independent terminal state. Retain raw stat rather than inferring state from
zero CPU/RSS. Reject unknown states/modifiers, wrong PID or malformed numbers.

Every observation records owned PID, poll-before time/returncode, raw ps output,
query start/end/status/error, parsed PID/stat/RSS/TIME, and poll-after time/
returncode. Query only after poll-before returned None. **Never query a PID
after the owned Popen has reaped it.** This prevents PID reuse from becoming
accounting evidence. Never run a new child until the prior child is confirmed
reaped. No outcome-changing signal injections occur in reaping or censored states.

Rules are prospective and conservative:

- A first live CPU0 with positive RSS is allowed. While live, any CPU decrease
  from its prior positive highwater, zero RSS, missing fields or unknown state
  is a sticky monitoring failure. Later reaping cannot excuse that live sample.
- A valid Z record is terminal evidence, including zero accounting. Retain the
  preceding positive CPU maximum. Positive terminal CPU/RSS values can increase
  the maxima and trigger resource censoring. Terminal zero is noninformative.
- Empty/PID-gone ps output is not proof of exit. Accept terminal disappearance
  only when the owned Popen independently reaps. Otherwise enter a bounded
  .5-second reaping grace with no new ps query/solver/injection; require owned
  confirmation, or mark a monitoring failure and terminate. A generic live
  zero record never receives this grace exception.
- Z/PID absence enters REAPING, then REAPED; there is no transition back to
  ordinary running. Keep previous failures even after a normal exit code.
  Missing finalization/restoration, abnormal code or unresolved reaping cannot
  become clean completion merely because a vector file exists.
- Reject duplicate/out-of-order observations and invalid query/poll intervals.
  Before final accounting, independently check complete child CPU snapshots'
  identity/hash/timestamp. After reaping, include them in the effective maximum
  along with valid ps highwater. Do not use RUSAGE_CHILDREN deltas: ps queries
  are also children. This plan does not introduce wait4/Popen double-reaping.

The pure accounting_policy.py prototype and deterministic check_policy.py
exercise these decisions without any native/OS experiment. Their pass does not
establish actual controller integration, platform behavior or physical timing.

## Budgets, actions and background operation

For optional real replication the parent CPU threshold is90 absolute process
CPU seconds, including interpreter/import/setup, not just solver elapsed CPU.
OS RLIMIT_CPU[90,95] remains a request; hard enforcement was not established.
Parent wall threshold is120 seconds and RSS threshold1GiB. CPU>=90 or wall>=120
or RSS>1GiB causes censoring, including limits discovered in terminal evidence.
Solver60 and node10000 limits remain separate from the process budget.

Monitor cadence is.01 seconds, ps query timeout1 second. At a resource/monitor
stop request SIGTERM for the owned child, wait at most.5 seconds, request SIGKILL
if needed and wait at most another.5 seconds. Log every action and observed
crossing. If still unreaped, record containment_failure, retain the owned handle
and identity, abort the queue and arrange follow-up; never block forever or
claim successful containment. Thresholds are polling triggers, not guarantees
of instantaneous CPU/memory/wall caps. Publish actual overshoot and response
intervals; do not claim a proven worst-case bound for scheduling delays or
uninterruptible OS states. The optional two-case controller ceiling is260
seconds with130 seconds remaining required before a case starts; any overrun
blocks acceptance and remains recorded.

For future lengthy authorized batches, use a durable background process with
atomic progress, append-only attempt journal, owned PID/start identity and
logs. Inspect progress about every20 minutes as requested by the user; detect
completion promptly when possible. Continuous resource monitoring stays at the
declared cadence. Background mode and less frequent human-facing checks do
not extend solver/resource budgets, permit restarts or mask a stopped monitor.
No periodic automation or long experiment is launched by this preparation.

## Environment, persistence and independent audit

Record the actual imported interpreter, NumPy/SciPy paths/versions, native HiGHS
core path/hash, package wrapper files, platform and thread environment. The
observed SciPy is in user-site despite the .venv interpreter. Do not silently
disable user-site or change dependencies; reject drift or use a new reviewed
version and fresh entry. Freeze worker/controller/model/guard/audit sources,
solver options, prior manifests, matrix/priors/input and known-witness hashes.

The old probe.solve() asserts warning expectations before returning its
OptimizeResult. Calling it unchanged could lose a returned payload on an
unexpected warning, and its three-option warning expectation does not fit
the two forwarded options of the MIS fixtures. Preserve the mathematical
helpers build_model/model_witness/validate_incumbent; implement a fresh shared
transport wrapper that captures the native return and saves raw arrays and
minimal identity metadata BEFORE warning/status validation. Parity modes expect
forwarding of threads/random_seed/mip_feasibility_tolerance; MIS expects only
threads/random_seed. Freeze per-mode warning rules. An unexpected warning
remains a recorded validation error, with the raw payload preserved.

Inside a fresh main-thread child install the nonraising SIGXCPU ledger before
the native call. Keep it through raw array and provisional-metadata atomic
persistence, with case/input/source identities and complete-file hashes. Restore
the prior handler in finally; only then snapshot the stable ledger and write
the authoritative final report. Signals are handled_at events, not inferred
generation times or causes. Missing/partial files and stale prior outputs
cannot be reused. A preexisting output/attempt directory blocks another launch.

An independent audit imports no solver/model/monitor helper. Check input and
source hashes; native call journal; raw/provisional/final identities; handler
restoration, stable ledger and timing; process state/reaping; strict live
monotonicity and retained terminal CPU maximum; actual guard actions; all
entry enumeration, returned-array and score checks; all previous manifests.
No new post-hoc exception is permitted to turn a frozen failure into PASS.
Preserve a failed protocol and review a separate correction instead.

## Execution status and witness evidence are different axes

Runtime statuses distinguish finalized ordinary return, finalized signal-
observed return, resource/monitor/exit censoring, incomplete output and backend/
validation error. Only normal owned reaping with valid finalization/restoration/
ledger/identity can be an ordinary return. A signal-observed return keeps that
label; unexplained signals stop further research-case execution.

Independently classify any complete raw incumbent as absent, invalid, valid
but noncompetitive, or verified competitive. Require finite shape, integer
proximity<=1e-7 before rounding, exact integer bounds/equations, every H/L bit,
unchanged syndrome/actual logical target and frozen case identity. Never repair
a returned vector to make it pass. Recompute score by dot/fsum and exact Fraction
sums of the represented float64 weights. Competitive means the exact represented
difference exceeds 1e-8+1e-12*max(abs(new_score),abs(wrong_score)); also compare
against the best correct-class saved candidate and verify outside-list status.

A competitive vector from a finalized ordinary return is primary constructive
evidence. A complete vector from a signal-observed or censored process may
support separately tagged **artifact-only constructive existence evidence**
after the same independent audit, but never normal completion, budget
feasibility, a timing-model sample or a rate improvement. Report process and
witness axes together; invalid monitoring remains invalid.

No returned witness means INCONCLUSIVE. Numerical dual bounds, optimal or
infeasible status do not exclude a competitive correction; known real-model
feasibility makes a reported infeasible status a backend/formulation error.
A witness cannot show the correct class globally wins over all wrong classes.
These inspected cases cannot estimate a new logical error rate or establish
decoder improvement, noise mismatch, publication novelty or a deployable method.

## Counts and exit rule

Historical optimizer API attempts relevant to this branch:6 original reference
probe (4 entry+2 real starts) plus12 timeout-repair attempts=18. This preparation
adds zero. A future native entry adds at most7, and the optional real envelope
at most2, for at most9 additional attempts/15 experimental children. Count
failed, interrupted and rejected starts. This is additional decoding-related
computation even though new BP/OSD/LSD and physical samples stay zero.

Close an entry failure without trying new parameters. Close an authorized
optional replication as witness/no-witness/infrastructure-failed with the two
axes intact; never expand because evidence is inconclusive. The next research
method must be justified separately by the failure mechanism and stronger
controls, rather than by more repetitions of the unchanged solver.

Primary semantics: [Python signals](https://docs.python.org/3.12/library/signal.html),
[subprocess polling](https://docs.python.org/3.12/library/subprocess.html), and
[versioned SciPy milp](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.milp.html).
