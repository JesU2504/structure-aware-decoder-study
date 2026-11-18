# Runner core passes its bounded process tests

18 November 2026. One kernel-backed owner now tracks each child's exit and
final CPU/peak-memory usage. Interim ps data no longer serve as a complete
lifecycle model. Invalid live measurements remain invalid after exit.

All12 fixed stdlib controls passed in2.610721 seconds, with independent audit
and AI supervisor postcheck. The32 preceding checks used fake interfaces and
launched no workers. No optimizer, decoder, research-case or physical-sampling
call was added; cumulative relevant optimizer attempts remain19.

This validates the tested runner core on the recorded Darwin environment.
It does not yet validate its integration with the optimizer adapter. The old
native entry remains failed and cases131/228 remain inconclusive. No new
decoder improvement or publication claim follows.

Next integrate the core into a fresh versioned adapter, review/freeze the code,
and validate that integration under a new bounded entry. Do not resume earlier
stopped runs or repeat real-case solves without a useful scientific purpose.

See [results](runner_repair_2026-11-18/RESULTS.md),
[AI review](runner_repair_2026-11-18/POSTCHECK.md),
[audit](runner_repair_2026-11-18/audit_result.json),
and [final checks](runner_repair_2026-11-18/final_checks.json).
The user-authorized GitHub mirror update is handled in publication_2026-11-18.
