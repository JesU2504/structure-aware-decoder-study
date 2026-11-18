# Native adapter entry failed; one toy artifact retained

18 November 2026. Fresh transport, monitor/controller and independent audit
were implemented and reviewed, then the fixed entry suite launched once.

It stopped after the first toy because macOS ps returned an unsupported `?E`
state during exit. The prospective allowlist was incomplete for this
environment. The policy correctly kept a monitoring failure after owned
reaping and the controller aborted the remaining12 controls. No retry,
resumption or post-hoc state-acceptance exception followed.

The solver's returned raw vector and objective4 are independently valid for
the exhaustive toy. Raw-first persistence, restoration and finalization
worked for that artifact; native integration remains FAILED and the remaining
timeout/signal/resource paths have not passed this entry.

Actual counts:1 optimizer attempt/1 persisted return,1 worker,
0.690395041 controller-wall seconds,0 research-case calls and physical samples.
Cumulative relevant optimizer attempts are19. Cases131/228 remain inconclusive.

The failure-accounting audit and independent AI supervisor verify integrity,
the correct toy artifact, retained monitoring failure and bounded stop.
They do not reclassify the entry as PASS. Apple's source supplies a plausible
exit-state explanation without matching the exact installed binary.

Next review a separate **stdlib-only** ownership/reaping protocol using one
kernel-backed child reaper and final per-child usage. Keep ps as interim
telemetry, preserve invalid measurements, and test lifecycle/cleanup before
another optimizer entry. No repeated MILP run is needed for that debugging.

See [results](adapter_entry_2026-11-18/RESULTS.md),
[postcheck](adapter_entry_2026-11-18/POSTCHECK.md),
[failure accounting](adapter_entry_2026-11-18/failure_accounting.json), and
[final checks](adapter_entry_2026-11-18/final_checks.json).
This work is local; the older public GitHub snapshot remains unchanged.
