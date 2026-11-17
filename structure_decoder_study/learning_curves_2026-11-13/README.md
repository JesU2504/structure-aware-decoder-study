# Incremental-training experiment

Read [findings.md](findings.md) and inspect
[learning_curves_sensitivity.png](learning_curves_sensitivity.png).

This completed post hoc experiment progressively increases distinct training
program groups using existing timing data. It does not increase decoder shots
or change the frozen stress-study predictor. The independent variables and
limits are declared in [PROTOCOL.md](PROTOCOL.md).

Run from the FTQC Research workspace:

```sh
./.venv/bin/python -u structure_decoder_study/learning_curves_2026-11-13/run.py
./.venv/bin/python structure_decoder_study/learning_curves_2026-11-13/analyze.py
./.venv/bin/python structure_decoder_study/learning_curves_2026-11-13/audit.py
./.venv/bin/python structure_decoder_study/learning_curves_2026-11-13/report.py
```

The runner lowers its process priority and restricts numerical libraries to one
thread. It saves atomic checkpoints and progress after every held-out group.
Existing checkpoints are reused only under the same configuration hash. Fitting
finished in about 13 seconds; no long-running job remains. `progress.json`'s
historical `measurements_complete` label means the fitting stage completed;
`decoder_shots_collected` is explicitly zero.

The outer metrics, splits, and a numerical subset of nested selections are checked
by separate sklearn code. `manifest.json` is a local post-analysis snapshot, not
external preregistration. All previous artifact snapshots are preserved.
