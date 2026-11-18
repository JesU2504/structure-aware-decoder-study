# Bounded timeout-return repair — 18 November 2026

Repair execution/result preservation only. Do not read or rerun BB144 cases,
change any historical freeze, install a solver, increase research budgets or
claim decoder improvement. Every optimization here uses a synthetic graph.

Python may defer a signal handler until native code yields. A handler that
raises can discard a returning solver result. Test recording SIGXCPU without
raising, retaining the handler through raw result persistence. Keep independent
OS hard CPU and external wall/RSS limits. Signals remain visible and censored;
the repair must not label a genuine resource event as ordinary solver success.
The origin of the historical SIGXCPU remains unknown unless new evidence
actually identifies it. No risky signal-ABI code is needed.

Use fresh children for every scenario. Record absolute/elapsed process CPU,
ru_utime/stime, active limits and handler state before/after calls and at handler
execution. Name timestamps handled_at, not generated_at. Known parent injection
origin is recorded by the controller; unknown origins remain unknown.

Engineering calibration is limited to four synthetic independent-set MILPs:
one immediate timeout (time_limit0) and up to three fixed candidate fixtures
for a timeout with an incumbent. Fixed n/time pairs:200/.15s,300/.5s,400/1s;
edge density.08, seed2026111801. Stop calibration once a valid incumbent timeout
is found. Preserve every call. If no suitable fixture is obtained, report that
coverage gap and do not silently expand the calibration.

Freeze the selected fixtures and confirmation code after supervisor preflight.
Confirmation scenarios: ordinary timeout without incumbent; ordinary timeout
with incumbent; legacy raising handler plus a controlled parent SIGXCPU;
recording handler with the same controlled signal; ordinary solved fixture;
real soft-CPU signal; hard-CPU kill; external wall kill; and a late-persistence
signal unit with handler-restoration checks. The last four do not solve MILPs.
The parent injects only into its owned child after the declared ready
marker and a short fixed delay; confirm the intended delivery occurred.

Calibration native calls<=4 and confirmation native calls<=5; no quantum
decoding or physical samples. One native thread requested. Every child gets
an8s external wall/1GiB RSS ceiling, with OS CPU limits10/12s except the explicit
CPU guard fixtures (soft1/hard3s). The external-wall fixture gets.15s. At most
13 children and120s cumulative controller execution (35s calibration,85s
confirmation); do not start a child without a10s remaining stage allowance.
No outcome-driven retries.

Preserve raw arrays before interpretation, independently validate returned
incumbents against synthetic graph constraints and score, and test incomplete
or signalled output handling. A killed process is censored even if a partial
result file exists. Keep the signal recorder installed until durable raw data
and provisional metadata are written; restore the previous handler afterward
in finally. Only then take the stable final ledger snapshot and write the
authoritative classification. A missing final record is censored.
Hard resource limits are installed only at the isolated worker boundary, not
inside a reusable context that promises to restore them.

Success is reliable return/preservation/classification on the tested scenarios,
with a supervisor review. It does not establish the historical signal origin,
production readiness on every platform, MILP tractability or any new research
result. Preserve earlier inconclusive cases unchanged. Any real-case rerun
would require a new reviewed protocol.

Primary references: [Python signal semantics](https://docs.python.org/3.12/library/signal.html),
[resource limits](https://docs.python.org/3.12/library/resource.html), and
[SciPy milp return semantics](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.milp.html).
