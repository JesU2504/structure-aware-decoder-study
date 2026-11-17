# Structure-aware decoder cost study

Stage 1 is a reproducible public-workload entry pilot. It does not establish a
publishable result, full logical accuracy, streaming deadlines, or compiler
speedup. Read `PROTOCOL.md` and `source_review.md` before interpreting results.
The completed result and its limits are in `findings.md`; figures are in
`results/pilot_overview.png` and `.pdf`.

The pinned Apache-2.0 TMCBS source and its vendored license notices are preserved
in `sources/`. No upstream files or earlier workspace studies are modified.

From the **FTQC Research** workspace, use the recorded workspace `.venv`:

```sh
./.venv/bin/python structure_decoder_study/study.py prepare
./.venv/bin/python structure_decoder_study/study.py validate
./.venv/bin/python structure_decoder_study/study.py freeze
./.venv/bin/python structure_decoder_study/study.py calibrate
./.venv/bin/python structure_decoder_study/study.py run
./.venv/bin/python structure_decoder_study/analyze_v2.py
./.venv/bin/python structure_decoder_study/audit.py
```

Run sequentially, with no concurrent CPU benchmarks. Preparation can take several
minutes because the public builder appends individual physical instructions.
`prepare` records all construction costs; those are excluded from pure decoder
service time but must be charged in future compiler comparisons. `calibrate`
uses separately named seeds and files and is excluded from model fitting.

Raw results are written by case and session and can be resumed only under the
same frozen hashes. Copy the study to a fresh output location for a new campaign
rather than overwriting prior data or rerunning preparation over a completed run.
The frozen config includes protocol, corpus, code, analysis, and source hashes.

`analyze_v2.py` uses leave-program-family-out ridge models and a connected-task
sensitivity analysis. Its budget curves are descriptive and **uncalibrated**.
The initial sample count screens mean/p95; it does not establish rare logical
failure rates or high-reliability p99 admission policies.

`audit.py` checks source/input/code hashes, recomputes stored timing summaries,
replays physical samples from recorded seeds, and verifies stored correction
checkpoints against their syndromes and logical outcomes. Seed replay is checked
only in the recorded software environment, not promised across Stim versions.

The original frozen `analyze.py` is preserved after a metadata-merging failure
before fitting. Read `ANALYSIS_AMENDMENT.md`; use `analyze_v2.py` for analysis.
The separately labeled post hoc controls can be reproduced sequentially:

```sh
./.venv/bin/python structure_decoder_study/robustness.py
./.venv/bin/python structure_decoder_study/component_control.py
./.venv/bin/python structure_decoder_study/audit_component.py
./.venv/bin/python structure_decoder_study/replay_slow_shots.py
```

Their protocols/configurations and raw outputs are retained. The component
control uses fresh physical samples and paired execution forms. Slow replay
selects extreme existing syndromes and cannot estimate population tail risk.

For a fresh timing campaign, copy only the source, scripts, and protocol files to
a new study directory; create its `circuits`, `logs`, and `results` directories
before preparation. Do not overwrite this archived corpus or frozen configuration
with new setup measurements. Reanalysis and audits use existing frozen inputs.
