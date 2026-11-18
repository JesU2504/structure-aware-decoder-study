# Independent AI supervisor postcheck — 18 November 2026

Internal AI review by `/root/timeout_repair_supervisor`; not human expert
validation. The reviewer performed read-only integrity and numerical checks
on saved outputs, with no new optimizer, decoder or experimental worker runs.

**Qualified acceptance for the controlled engineering scope.** The tests
establish result preservation under the tested delayed-signal conditions and
demonstrate the added parent CPU watchdog. They do not constitute an
unconditional pass of the original frozen protocol.

The reviewer independently checked:

- V2 frozen inputs (13 files), supplemental-audit inputs (6), and raw-output
  manifest (86): no hash mismatches.
- Preserved V1 manifest (119 files) and earlier research-reference manifest
  (30): no mismatches.
- Saved returned vectors against synthetic graph constraints and objective
  sums, including exhaustive verification of the six-variable optimum: passed.
- All nine process outcomes: ordinary timeouts retained their incumbent/no-
  incumbent distinction; the legacy handler lost its return; the recording
  handler retained a valid result and signal record; soft CPU, external CPU,
  wall termination and late persistence behaved as documented.
- The external CPU fixture triggered at **3.00 measured CPU seconds**,
  received SIGTERM about nine microseconds after the recorded sample and
  remained censored. Last child telemetry showed 2.900498 CPU seconds.
- Accounting: **12 synthetic optimizer API attempts, 20 children,
  19.813278083 cumulative controller seconds**, zero research-case calls
  and zero physical samples.

**The failures remain part of the record.** V1 failed its OS-only hard-CPU
containment expectation. The original V2 audit failed its requirement that
every CPU sample remain nondecreasing. Its two final zero-RSS/zero-CPU samples
occurred after verified terminal worker markers. Their OS state and accounting
mechanism were not sampled and remain unresolved.

The separately reviewed, frozen, explicitly post-hoc supplemental audit
passed. It retained preceding positive CPU maxima of .43/.44 seconds,
checked agreement with final child telemetry and allowed only those two
terminal observations. It did not rerun workers, alter results or convert
the original audit failure into a pass.

The supported conclusion is: **the saved controlled tests demonstrate the
intended return-handling repair and external CPU/wall containment, subject to
the disclosed terminal-accounting adjudication.** This does not establish OS
hard-limit enforcement, an RSS threshold crossing, production readiness,
historical signal origin, MILP tractability, decoder improvement or a result
for cases 131 and 228.

Preserve these artifacts and close this bounded engineering exercise. Before
using the repair for a future research probe, integrate it through a separately
reviewed protocol that records process state/termination transitions and
defines terminal accounting prospectively. **Do not automatically rerun the
two research cases.**
