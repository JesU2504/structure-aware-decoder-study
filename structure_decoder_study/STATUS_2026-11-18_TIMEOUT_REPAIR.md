# Timeout repair: controlled tests completed, qualified acceptance

18 November 2026. Latest update after the inconclusive reference probe.

The repaired signal guard preserves returned solver data without raising at
the native return boundary, records signals and restores the prior handler.
A parent CPU watchdog now supplements wall/RSS monitoring after the first
version failed its OS-only hard-CPU expectation. Both versions and all failed
checks remain preserved.

All nine V2 synthetic scenarios completed once. The parent stopped the hard
CPU fixture at 3.00 measured CPU seconds. Ordinary solver timeouts retained
their incumbent/no-incumbent distinction; controlled legacy result loss was
reproduced; the recording handler preserved the valid returned result.

The original frozen V2 audit failed on two final zero-valued process-accounting
samples. A separately reviewed/frozen, explicitly post-hoc supplemental audit
passed with a narrow terminal-marker exception. This does not turn the original
audit into a pass; the OS state/accounting mechanism remains unresolved.
The independent AI supervisor gives qualified acceptance of the controlled
engineering repair, with no production-readiness or scientific claim.

Totals across both versions: 12 synthetic optimizer API attempts, 20 child
experiments and 19.813278083 controller-wall seconds. No quantum/research cases
or new physical samples were run. Cases 131 and 228 are still inconclusive;
the earlier candidate-list diagnosis is unchanged. No decoder improvement,
tractability or publication novelty has been established by this repair.

This engineering exercise is closed. Next: separately review a prospective
integration protocol that records process state/termination transitions and
defines terminal accounting before any research rerun. No automatic rerun
or larger research budget follows from these tests.

See [results](timeout_repair_v2_2026-11-18/RESULTS.md),
[AI supervisor postcheck](timeout_repair_v2_2026-11-18/POSTCHECK.md),
[supplemental audit](timeout_repair_v2_2026-11-18/audit_adjudication_result.json),
and [final checks](timeout_repair_v2_2026-11-18/final_checks.json).
This work is local; the older public GitHub snapshot is unchanged.
