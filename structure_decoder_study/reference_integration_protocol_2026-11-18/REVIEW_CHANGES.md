# Corrections made before the preparation freeze

These are prospective design/prototype revisions. No new native integration,
optimizer or research experiment was executed. Initial draft specifications
and earlier deterministic check outputs are retained with explicit names.

The independent AI supervisor review prompted these changes:

- Explicit live-state precedence: later reaping cannot excuse a live CPU reset.
  Terminal evidence requires observed Z or separately confirmed owned reaping.
- Strict mapping/string/return-code/status/signal types, finite positive budget
  configuration, duplicate/out-of-order rejection and sticky failure reasons.
- Checked child CPU is incorporated only after owned reaping, avoiding a
  false decrease caused by comparing precise child CPU to rounded live ps TIME.
- A censored observed-Z process requests reaping without further live signals.
  Root self-review additionally distinguished unconfirmed PID absence: if its
  grace expires while still unreaped, request termination. The77-check result
  and source hashes include that distinction.
- Entry admission reserve increased prospectively from10 to11 seconds, since
  the declared query/poll/termination allowances can exceed10. Threshold
  overshoot and containment failure are reported rather than hidden.
- The controlled Z fixture requires a positive live sample before release.
  Expected injected faults remain censored processes even when their control
  tests pass; unexpected faults block the suite.
- Capture actual user-site SciPy and direct _highs_wrapper.py/native-core
  identities. Preserve the existing environment; no silent user-site change.
- Do not reuse old solve() unchanged: it asserts warnings before handing back
  the raw result. New transport must save raw output first and validate
  warnings/status afterward with separate parity/MIS warning expectations.
- Make relative input roots and all matrix/weight/priors paths explicit.
- Separate entry readiness from scientific value. Repeating the same solver
  after logs showed no incumbent has low expected new scientific value.
  Research launch remains disabled in this preparation package.

policy_checks_initial.json records the initial46 deterministic assertions;
policy_checks_schema_revision.json records76 after schema/configuration
changes; policy_checks.json records the final77 and its tested source hashes.
These are deterministic policy checks, not repeated solver calibration or
confirmation of actual platform behavior.
