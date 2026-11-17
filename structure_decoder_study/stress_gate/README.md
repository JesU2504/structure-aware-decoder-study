# Frozen-model stress exploration

Read `findings.md` first. This is a model-falsification and failure-localization
study, with explicit one-sector/full-block scope and selected-task limitations.
The original pilot and its frozen artifacts remain unchanged.

Run from the FTQC Research workspace with the recorded `.venv`. The primary run
sequence was:

```sh
./.venv/bin/python structure_decoder_study/stress_gate/stress.py prepare
./.venv/bin/python structure_decoder_study/stress_gate/stress.py discovery
./.venv/bin/python structure_decoder_study/stress_gate/analyze.py discovery
./.venv/bin/python structure_decoder_study/stress_gate/stress.py confirmation
./.venv/bin/python structure_decoder_study/stress_gate/analyze.py confirmation
./.venv/bin/python structure_decoder_study/stress_gate/analyze_prefix.py
./.venv/bin/python structure_decoder_study/stress_gate/diagnose.py
./.venv/bin/python structure_decoder_study/stress_gate/boundary.py prepare
./.venv/bin/python structure_decoder_study/stress_gate/boundary.py run
./.venv/bin/python structure_decoder_study/stress_gate/boundary.py analyze
./.venv/bin/python structure_decoder_study/stress_gate/box_challenge.py prepare
./.venv/bin/python structure_decoder_study/stress_gate/box_challenge.py run
./.venv/bin/python structure_decoder_study/stress_gate/box_challenge.py analyze
./.venv/bin/python structure_decoder_study/stress_gate/review_results.py
./.venv/bin/python structure_decoder_study/stress_gate/audit.py
./.venv/bin/python structure_decoder_study/stress_gate/plot.py
./.venv/bin/python structure_decoder_study/stress_gate/seal_artifacts.py
```

Run measurements serially. `prepare` is for a fresh study copy, not for overwriting
this frozen artifact. Existing measurement outputs are resumable under their
hashes. Static predictions and original analysis remain preserved. Reviewed
summaries qualify censored fields; use those for interpretation and plotting.

`pre_timing_lock.json`, `run_config.json`, and the phase protocols record the
initial scope and predictor. The fixed-prefix extension and selected noise-boundary
tests were documented before their fresh data. The confirmation metadata snapshot
was corrected after launch, as explicitly recorded; do not call it a pre-launch
hash lock or external preregistration.

There are 82,968 new physical observations and additional diagnostic replays.
Two large tasks hit CPU caps in their respective phases. The audit checks
physical sample replay and stored correction checkpoints, with no external
researcher review implied.

`manifest.json` and `../artifact_manifest_2026-11-13.json` are local post-analysis
integrity snapshots. The original 905-file `../artifact_manifest.json` is preserved
and verified separately. These snapshots are not external timestamps or
preregistrations.
