# Independent AI supervisor preflight: timeout-return repair

18 November 2026. Read-only review of `PLAN.md`, the signal guard, worker, controller, independent audit and completed calibration evidence. This is internal AI review, not human expert validation. This reviewer ran no optimizer, signal test, decoder or scientific computation.

**GO for the nine fixed synthetic confirmation scenarios, conditional on the freeze and independent audit.** This approves an execution/result-preservation test only. It does not approve real-case reruns or establish the origin of the historical SIGXCPU.

## What the repair changes

The new guard records SIGXCPU instead of raising immediately while a native result is being handed back. It remains active while raw arrays and provisional metadata are saved. Its `finally` restores the original handler; only afterward is a stable final ledger captured and the authoritative classification written. This addresses both return loss and a signal arriving during persistence.

All work occurs in fresh owned children. OS hard CPU limits and external wall/RSS monitoring remain active. Resource/signalled runs cannot become ordinary solver success merely because a result file exists. The reusable guard does not change or promise to restore irreversible hard limits; those are configured at the isolated worker boundary. Main-thread use is explicit.

## Calibration and bounded scope

The declared calibration passed with two optimizer API attempts, about 0.842 controller-wall seconds: immediate timeout without an incumbent, and the fixed n=200/0.15-second independent-set fixture with a valid incumbent. Both exited normally, had finalized/restored reports and no signal event. Their helper/controller source hashes are retained. The zero-vector incumbent is adequate to test result preservation; it is not an optimization-quality claim.

The nine confirmation scenarios cover ordinary timeout with/without an incumbent, controlled legacy loss, guarded return under the same injected signal, ordinary completion, soft CPU signal, hard CPU kill, external wall kill, and late persistence with normal/exception handler restoration. The late-persistence case uses a labeled known payload, not an optimizer call.

The plan allows at most four calibration and five confirmation optimizer API attempts, no research inputs or physical samples, and at most thirteen children. Controller stage ceilings are 35 and 85 seconds, with a ten-second allowance required before another child; each child has its own wall/RSS and OS CPU limits. Calibration stopped after selecting the first valid declared fixture. There are no retries or unlisted variants.

## Code and audit checks

- Absolute CPU, user/system CPU, active resource limits and handler identity are captured before/after calls and at handler execution. Event timestamps mean `handled_at`; they do not claim native signal-generation time or origin.
- Controller injections target only its owned PID after a phase marker and fixed delay. The audit verifies PID/signum and timing within the intended call interval. The late case must have the guarded-persistence marker and a persistence-phase signal event.
- The legacy control must exit nonzero with the expected raising-handler exception and no returned raw/result file. The guarded control must preserve its signal ledger, returned payload and independently checked incumbent under the same graph/cost fixture.
- Independent audit imports no guard/controller helper. It checks finalized/restored records, stable ledgers, process outcomes, exact synthetic graph feasibility, objective sums and exhaustive n=6 optimum. Missing final records or abnormal exits remain censored even if provisional data exists.
- Soft-CPU evidence must show an active [1,3]-second limit and absolute CPU near/above the soft threshold, without a parent injection. The hard-limit and external-wall cases must demonstrate actual termination and remain failed/censored.
- The previous reference-study manifest is checked unchanged. Its real cases are not rerun or used as fixtures. This work cannot alter their inconclusive result.

## Pre-freeze issues corrected

Review prompted a stable post-restoration finalization step, explicit handler telemetry/restoration checks, process-aware calibration acceptance and a requirement for finalized/restored authoritative reports. Stage budgets now match the cumulative promise. Additional audit checks distinguish an injected call-time signal from a late-persistence event and a configured soft-CPU event. I reread those changes. The calibration-tested source files are subject to unchanged-hash gates at freeze.

## Meaning of a pass

A pass would establish that this isolated adapter preserves and classifies the tested return paths while retaining containment. It would not establish why the historical signal occurred, validate every platform or race, make the MILP reference tractable, yield a new correction or supply publication novelty. Require the completed independent audit and supervisor postcheck before reporting that the repair worked. Do not broaden the scenarios or retry real cases automatically.
