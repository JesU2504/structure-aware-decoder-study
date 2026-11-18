# Reference probe: both observations remain unresolved

18 November 2026. The fixed two-case reference experiment attempted cases131
and228 once each. **Neither attempt returned a validated new correction. Both
are inconclusive; there is no evidence here that better corrections are absent.**

| Case | Recorded elapsed CPU | Recorded elapsed wall | Peak child RSS | Outcome |
| --- | ---: | ---: | ---: | --- |
| 131 | 62.118s | 63.037s | 201801728bytes | SIGXCPU interrupted native solver return; unresolved |
| 228 | 61.596s | 62.197s | 192970752bytes | SIGXCPU interrupted native solver return; unresolved |

The HiGHS console reported its time limit and an infinite primal bound in both
cases. Python received SIGXCPU while the native solve was returning, before the
wrapper supplied a result object. There is no returned incumbent array or raw
result metadata to validate. The invocation journal contains two starts and no
completed Python solver returns; this is intentionally preserved as partial work.

The solver had a nominal60-second time limit and10000-node cap; the enclosing
child requested90CPU/120wall seconds and1GiB RSS. These are distinct limits.
The recorded CPU values are elapsed since the worker's initial timestamp, while
the OS limit uses process CPU accounting. Absolute starting CPU and the active
limit at the signal were not recorded. Consequently, the precise SIGXCPU cause
or limit interaction is NOT established. No threading or OS-defect explanation
is supported. Do not interpret the handler's generic message as proof that90
seconds were consumed. No retries, larger budgets or changed options were used.

## What was attempted

The installed SciPy1.17.0/bundled HiGHS1.8.0 backend passed four small models
checked by exhaustive binary enumeration. Model and validation helpers used for
those fixtures stayed identical in the real worker; its source snapshot is saved.
Additional return-validation adapters rejected fractional, parity-invalid,
out-of-bounds, nonfinite and malformed data. The supervisor reviewed the actual
code and protocol before the36-file freeze, SHA256
`3126cd1fe4a5a9b110c24b3ae0e5fe68fff6929f47212b92892f2e5d758d8c1e`.

Each real model retained all12240 binary variables, all1800 detector equations
and12 actual logical equations, plus1812 integral parity-slack variables.
The unchanged source sum(log(1/p)) objective and full-1FV wrong winners were
used. Existing correct-class vectors passed the full model before solving, so
the constrained models are known feasible. These vectors were not supplied as
warm starts because the selected public SciPy interface does not expose one.

This was oracle-assisted reference analysis: known true logical labels were
constraints. Even a positive witness would not be a deployable decoder or a
population improvement. The four entry optimizations plus two real starts are
SIX reference-optimization calls, with four completed entry returns and zero
completed real returns. There were zero new BP/OSD/LSD calls, physical samples
or model fits; this does not mean zero decoding-related computation.

## Audit and supervisor check

The independent audit completed normally and passed its evidence-accounting
checks: frozen inputs, ordered calls, resource-stop records, known correct/wrong
adapters, lack of exclusion claims and all23 prior result manifests unchanged.
It made no solver calls. Its elapsed cost was0.802CPU/1.472wall seconds, peak
75087872bytes. **Audit PASS means the stopped work is recorded consistently;
it does not mean the two optimization problems were solved.**

The controller correctly retained the first resource stop and performed the
fixed second attempt. Preflight had corrected unknown solver-status handling,
preservation of rejected raw output and partial-call audit paths. There was
also an operational validation gap: entry tests covered small optimal and
infeasible returns but did not exercise the anticipated time-limit return path.
That path did not complete cleanly on either real case. This is a limitation
of the reference experiment, not undertraining or a discovered quantum failure.

## Scientific disposition

The earlier finding remains: both saved lists contain the correct class, but
its best listed representative loses the source-score comparison. This probe
has NOT separated missing competitive representatives outside the list from
more fundamental individual-error scoring ambiguity. No true-class optimum,
rigorous lower bound, impossibility, ML certificate or new repair is established.
Console dual values are numerical estimates only and cannot change this verdict.

The supervisor's next recommended task is a bounded timeout/signal integration
diagnosis on a NONRESEARCH fixture before any real-case rerun. Record absolute
and elapsed CPU, OS limit state and result-return behavior. Do not raise solver
budgets, switch optimizers or start AA/scoring/model experiments automatically.
The next engineering check is separate from this frozen study.

Read [supervisor postcheck](POSTCHECK.md), [frozen protocol](PROTOCOL.md),
[preflight](PREFLIGHT.md), [entry evidence](entry_result.json),
[process records](process_result.json), [independent audit](audit_result.json)
and the preserved per-case logs/stop records under `cases/`.
