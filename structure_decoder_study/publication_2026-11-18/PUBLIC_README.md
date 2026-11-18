# Structure-aware decoder study

Research code, frozen protocols and simulated data for studying decoder cost
and task-specific decoding failures. This is exploratory work. No new decoder,
compiler speedup or publishable improvement has been established. Supervisor
reviews are internal AI reviews, not external human peer review.

## Current findings — 18 November 2026

- Earlier cost-model experiments did not establish a useful incremental
  benefit from the tested graph summaries or a compiler decision benefit.
- A pinned BB144 Z-check-only memory reproduction,24 rounds at p=.007,
  produced12 syndrome-valid logical failures in512 natural circuit-noise
  observations. Three existing BP+OSD/LSD settings failed on the same12 cases.
- After preserving an initially stopped ordering-mismatch run, an adapted
  **known1FV search** rescued10 of the12 selected failures;12 fixed success
  controls stayed correct. These24 inspected cases do not establish a new
  population error rate. No new search method is claimed.
- Cases131/228 remain wrong. Their saved candidate lists contain the correct
  logical class, but its best listed scores lose by substantial margins.
  This does not establish a flawed likelihood model or intrinsic uncorrectability.
- Two oracle-assisted reference optimizer starts ended without usable Python
  results. Both scientific outcomes remain **inconclusive**. A later native
  adapter entry also remains **failed** after one toy due to process-state
  monitoring; its12 remaining controls were not resumed.
- The **runner core now passes12 stdlib-only process controls** and independent
  audit: one kernel-backed owned-PID reaper records exit and final per-child
  usage, while interim telemetry stays separate. This is a software reliability
  result, not validated optimizer-adapter integration or decoder improvement.

The next engineering step is a fresh reviewed integration of that runner core
with the raw-first optimizer adapter. A real-case retry still needs a useful
scientific purpose; simply repeating the unchanged solver/seed/budget has low
expected new information.

## Verify the saved snapshot

Recorded experiments used Python3.12. Verification needs NumPy/SciPy:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verify.py
.venv/bin/python tools/verify_progress.py
```

These commands verify exported checksums, recompute1,627 archived natural-noise
outcomes, ordering matches, the24-case search outcomes, saved correct-class
representatives and the12 runner-control records. They make **no decoder,
optimizer or worker calls**. The progress verifier does not repeat the full
250,728-member candidate-class audit; that original audited evidence is included.

Optional native replay of one existing baseline failure requires the decoder:

```sh
.venv/bin/python -m pip install -r requirements-decoder.txt
.venv/bin/python tools/replay_case.py --case 23
```

That command performs an additional decoder call. It was not needed for this
update's saved-output verification. Exact native corrections/random streams
can depend on platform and package versions. The circuits expose **Z checks
only**, not full-Pauli logical-memory performance.

## Evidence and code

- [Natural-noise reproduction](structure_decoder_study/natural_noise_reproduction_2026-11-17/RESULTS.md)
- [Preserved stopped ordering run](structure_decoder_study/headroom_1fv_2026-11-17/RESULTS.md)
- [Ordering diagnostic](structure_decoder_study/ordering_diagnostic_2026-11-17/RESULTS.md)
- [Known1FV search on the selected panel](structure_decoder_study/headroom_cached_order_2026-11-17/RESULTS.md)
- [Candidate-class diagnosis and limits](structure_decoder_study/candidate_class_diagnosis_2026-11-18/RESULTS.md)
- [Inconclusive reference probes](structure_decoder_study/reference_probe_2026-11-18/RESULTS.md)
- [Preserved failed native entry](structure_decoder_study/adapter_entry_2026-11-18/RESULTS.md)
- [Passing stdlib runner core](structure_decoder_study/runner_repair_2026-11-18/RESULTS.md)
- [Runner implementation](structure_decoder_study/runner_repair_2026-11-18/runner.py), [owned reaper](structure_decoder_study/runner_repair_2026-11-18/owner.py), [independent audit](structure_decoder_study/runner_repair_2026-11-18/audit.py)
- [AI supervisor postcheck](structure_decoder_study/runner_repair_2026-11-18/POSTCHECK.md)
- [Original cost-model study](structure_decoder_study/README.md)

## Provenance and portability

This is a curated mirror of the decoder project. Virtual environments,
credentials, installed native binaries, private publication state and unrelated
workspace projects are excluded. Data arrays are byte-preserved. Personal host
paths in text become `<WORKSPACE>`, `<USER_HOME>` or `<TEMP>`; absolute local
Markdown links become relative. `PUBLIC_EXPORT.json` records original/exported
hashes and exclusions.

Historical machine-specific freezes/manifests are retained as provenance,
**not re-signed** as though sanitized text were the original experiment. Use
the public verifiers above for this mirror. Do not execute historical in-place
drivers expecting their original paths/hashes or overwrite existing outputs.
Fresh runs require new output locations and an appropriate reviewed protocol.
The runner core was tested on the recorded Darwin environment; its source
should not be read as proof of every platform/race or instantaneous containment.

Historical notes saying an update was local describe their original time;
this snapshot includes the subsequent results listed above. Previous failures
and inconclusive outcomes remain failures and inconclusive outcomes.

Upstream helper snapshots without an explicit license are not vendored.
`tools/fetch_upstream.py` can restore pinned public files without executing
them. See [third-party notices](THIRD_PARTY.md).

Publication novelty, a practical intervention and fair fresh-data confirmation
remain open research requirements. This repository is not a manuscript.
