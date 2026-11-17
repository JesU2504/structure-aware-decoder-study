# Bounded validation gate

Read [findings.md](findings.md) and inspect [validation_gate.png](validation_gate.png).
Preparation/model fitting began on 13 November; audits and new bridge timing
completed on 15 November 2026. The older folder name is preserved.

The gate contains a controlled linear/nonlinear comparison, a balanced
interleaved bridge on previously inspected parents, paired decoder-iteration
controls, and a same-program calibration decision. It is not a final reserved-
parent trial. No large new-parent campaign was launched after these results.

The completed sequence, from the FTQC Research workspace, was:

```sh
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/prepare.py
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/models.py
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/audit_models.py
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/bridge.py freeze
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/bridge.py run --session 0
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/bridge.py run --session 1
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/bridge.py run --session 2
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/analyze_bridge.py
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/audit_bridge.py
./.venv/bin/python structure_decoder_study/validation_gate_2026-11-13/report.py
```

Do not rerun `prepare`, `freeze`, or an existing timing session over this artifact.
Use a new copy for a new measurement campaign. Models/measurement settings and
pre-timing predictions are hash checked. Analysis implementation timing and
interruption provenance are explicitly documented, without external registration
or independent-review claims.

Raw correction vectors are bit-packed in each NPZ file. The audit replays the
physical sampler seed and checks every correction against H and L. Profiling,
evaluation, and warmup streams are separate. All three timing sessions are
complete and no job remains running.

`manifest.json` and the parent study's `artifact_manifest_2026-11-15.json` are
post-analysis local integrity snapshots. All older manifests are preserved.
