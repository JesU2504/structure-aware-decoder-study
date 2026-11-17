# Resumption before bridge timing

15 November 2026 (client date, Asia/Tokyo). The previous turn was interrupted
after bridge preparation and the model-control job were launched. On resumption,
19 prepared circuits, 186 completed outer model fits, predictions, and their
configuration hashes were present. No bridge timing outputs existed.

The historical folder name and 13 November protocol are preserved. The bridge
will be measured on 15 November and its new configuration will record that date.
No candidate set, feature set, model grid, decoder budget, quality screen, or
service-budget grid is changed after seeing the completed model controls.

Implementation clarification before measurement: the profiling stream uses its
own decoder, with 32 warmup shots. Evaluation uses newly constructed decoder
instances, each given the same separate 32-shot evaluation warmup. This prevents
the BP30 profiling stream from giving its evaluation instance extra warmup.
The two warmup streams are not evaluation or profiling observations and are
accounted for separately. The resource cap applies to evaluation service CPU,
summed across settings, after complete paired blocks; profiling/setup/warmup CPU
is excluded from that research cap and reported separately where measured.

This is local provenance and an implementation clarification, not external
preregistration. No reserved final-test parents have been measured or selected.
