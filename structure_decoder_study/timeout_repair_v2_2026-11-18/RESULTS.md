# Timeout repair completed with qualified engineering acceptance

18 November 2026. This stage repairs result preservation and containment using
synthetic fixtures only. It does not produce a quantum-decoding result.

## What changed

The fresh-child signal guard records SIGXCPU instead of raising an exception
at the native return boundary. It stays active while raw results are saved,
then restores the previous handler and writes a stable final classification.
Signal-observed results retain that classification. Parent process status
and budget termination take precedence over any result file.

V1's guard worked on controlled returns but its OS-only hard-CPU test failed:
the child continued to about 7.9 CPU seconds until the wall watchdog. V1 is
frozen unchanged and remains failed. V2 keeps the identical guard/worker and
adds parent CPU monitoring alongside wall/RSS monitoring. Only owned child
PIDs are monitored and signalled; malformed active-process data fails closed.

## Saved confirmation outcomes

All nine V2 scenarios ran once, with five optimizer API attempts and no new
calibration. The other four scenarios do not call the optimizer.

| Scenario | Observed result |
|---|---|
| Immediate solver timeout | Status 1, no incumbent; finalized return retained |
| Solver timeout with incumbent | Status 1, independently valid incumbent retained |
| Controlled signal, legacy raising handler | Exit 1; returned result lost as expected |
| Same fixture/signal, recording handler | Valid incumbent and signal record retained |
| Six-variable ordinary completion | Optimal solution verified exhaustively |
| Soft CPU signal | Signal recorded and previous handler restored |
| Parent CPU watchdog | Trigger at 3.00 measured CPU seconds; SIGTERM; censored |
| External wall watchdog | SIGTERM at wall budget; censored |
| Signal during persistence | Labeled mock payload retained; restoration checks pass |

The original frozen V2 audit **failed** its assumption that every ps CPU
sample is nondecreasing. Two final samples had matching PIDs but zero CPU
and RSS after verified terminal worker markers. We did not sample process
state, so their OS mechanism is unknown. Original source, outputs and failure
remain unchanged; there was no experimental rerun.

An independently reviewed, separately frozen **post-hoc supplemental audit
passed**. Its only exception permits those final zero-valued observations
after the required terminal markers. It retains preceding positive CPU
maxima, verifies agreement with child telemetry and keeps all other original
checks. This is a disclosed engineering audit correction, not prospective
confirmation of a new assumption or an unconditional frozen-protocol pass.

## Accounting and supported conclusion

Across V1+V2 there were 12 synthetic optimizer API attempts, 20 child
experiments and 19.813278083 measured controller-wall seconds, within the
120-second cumulative ceiling. V1 used seven attempts and V2 added five.
Supplemental auditing added no optimizer or experimental child calls.
There were zero research-case calls, new BP/OSD/LSD calls or physical shots.

The independent AI supervisor gives **qualified acceptance of the controlled
repair**: tested return preservation and external CPU/wall containment are
supported subject to the terminal-accounting adjudication. OS hard-limit
enforcement, an RSS-limit crossing, production readiness and historical signal
origin remain unestablished. Earlier cases 131/228 remain inconclusive.
No solver tractability, decoder improvement or publication novelty is claimed.

The bounded engineering exercise is closed. The next research step requires
a separate prospective protocol that integrates the adapter, records process
state/termination transitions and defines terminal accounting before any run.
Do not automatically rerun cases 131/228 or raise their budgets.

Evidence: [original failure](audit_initial_failure.json),
[supplemental rule](AUDIT_ADJUDICATION_PLAN.md),
[supplemental audit](audit_adjudication_result.json),
[supervisor postcheck](POSTCHECK.md), and [final checks](final_checks.json).
The original V2 freeze is
`249a520f00a6e2700b06efac405c9eb80eff2ddffb286767d13760f7ec4be761`.
The supplemental audit freeze is
`99cef203f8ddd751f65fb87792ff8b44234ba51947467e14a795f3b077eef426`.

This update is local; the older public GitHub snapshot has not changed.
