# Bridge analysis implementation timing

15 November 2026. The analysis script was implemented after timing was launched.
By this point processes 0 and 1 had completed, and their progress/sample-count
summaries had been read. No case-level bridge latency, accuracy, profiling,
configuration-comparison, or schedule-choice result had been inspected.

The protocol had already declared the candidates, comparison models, BP budgets,
quality screen, budget sweep, and interval families before timing. The analysis
implements those declarations. The script and this note are separately hashed
before the first analysis run. This is an internal provenance statement, not
an externally timestamped pre-analysis registration.

All schedule choices condition on the same retrospective calibration quality
screen. That is a diagnostic cost-model ablation, not a deployable compiler
accuracy policy. Trivial one-eligible-candidate pairs are separated from actual
two-candidate cost choices. The measured finite-candidate oracle has uncertainty;
nonoverlapping p95 intervals are reported separately from point-estimate regret.
