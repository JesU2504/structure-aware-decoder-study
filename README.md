# Structure-aware decoder study

Research code, protocols and simulated data for studying decoder costs and
reproducing decoding failures. This is exploratory work, not a manuscript or a
claim of a new decoder or compiler speedup. AI supervisor reviews are labelled
as AI reviews, not external human peer review.

## Current findings (17 November 2026)

- Earlier circuit-derived cost-model experiments did not establish a useful
  incremental benefit from the tested graph summaries or a compiler speedup.
- A source-matched BB144 Z-memory reproduction at 24 rounds and p=0.007 produced
  12 syndrome-valid logical errors in 512 natural circuit-noise observations.
  BP20+OSD0, BP30+LSD0 and BP100+LSD0 failed on the same 12 observations.
- The planned Python 1FV comparison stopped when its native-baseline equality
  gate failed at case 51. No real 1FV search was run.
- An implementation-derived ordering diagnostic matched all 24 cached native
  baselines, versus 23 for stable Python ordering. It accounts for that observed
  tie-order incompatibility on the fixed macOS arm64 panel. It does not resume
  the stopped search or establish repair headroom or cross-platform equivalence.

## Verify and replay

Python3.12 was used for the recorded experiments. Create a fresh environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verify.py
```

The verifier checks every exported file's checksum and independently recomputes
all 1,627 stored natural-noise experiment outcomes and the ordering-panel matches.
It makes no decoder calls. To replay the first recorded logical failure:

```sh
.venv/bin/python -m pip install -r requirements-decoder.txt
.venv/bin/python tools/replay_case.py --case 23
```

The recorded environment gives syndrome residual 0 and 6 wrong logical bits for
case 23. Exact correction vectors and random-seed streams can depend on package
versions and platform. The source circuit extracts **Z checks only**.

## Read the evidence

- [Natural-noise reproduction](structure_decoder_study/natural_noise_reproduction_2026-11-17/RESULTS.md)
- [Stopped headroom comparison](structure_decoder_study/headroom_1fv_2026-11-17/RESULTS.md)
- [Ordering diagnostic](structure_decoder_study/ordering_diagnostic_2026-11-17/RESULTS.md)
- [Supervisor review](structure_decoder_study/publication_strategy_2026-11-17/supervisor_headroom_postcheck.md)
- [Original cost-model study](structure_decoder_study/README.md)

## Export and provenance

This is a public mirror of the decoder project, not the surrounding workspace.
No environment, credentials, native binaries or unrelated projects are included.
Data arrays are byte-preserved. Personal host paths in text are replaced by
`<WORKSPACE>`, `<USER_HOME>` or `<TEMP>`; Markdown file links are made relative.
`PUBLIC_EXPORT.json` records original and exported hashes and all exclusions.

Historical machine-specific freeze/manifests are retained as provenance, not
re-signed as if sanitized bytes were the original experiment. Their old hashes
can differ from transformed text or omitted dependencies. Use `tools/verify.py`
for this mirror rather than running historical in-place freeze/audit drivers.
Fresh experiments belong in new output directories with a newly frozen protocol.

Upstream snapshots without an explicit license are not vendored. If needed,
`tools/fetch_upstream.py` restores their exact pinned files without executing
them. See [third-party notices](THIRD_PARTY.md). The saved-data verifier and
native case replay do not require those helpers.

The reproduction is a baseline. Publication novelty and a consequential
compiler-facing decision remain open research requirements.
