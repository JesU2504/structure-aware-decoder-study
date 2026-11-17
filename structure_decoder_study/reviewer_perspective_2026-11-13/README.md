# Reviewer-perspective internal audit

Read [assessment.md](assessment.md) for the conclusions and revised next step.
This is internal checking by the same assistant, not external peer review.

The review reuses existing raw data. Its sensitivity analyses and structural
screens do not perform new decoder timing runs or update frozen predictors.

```sh
./.venv/bin/python structure_decoder_study/reviewer_perspective_2026-11-13/diagnostics.py
./.venv/bin/python structure_decoder_study/reviewer_perspective_2026-11-13/checks.py
./.venv/bin/python structure_decoder_study/reviewer_perspective_2026-11-13/candidate_screen.py
```

`PROTOCOL.md` declares the post hoc diagnostics. `sensitivity_summary.json`
contains all scenarios; checkpoints preserve outer predictions and nested
selections. `precision_and_context.json` records target/session precision and
archived total pipeline costs. `checks.json` records separate sklearn fits and
the limited projected-DEM screen. `compiler_candidate_screen.json` records the
existing same-program pairs. The local `manifest.json` is an integrity snapshot,
not external preregistration. Earlier artifacts remain unchanged.
