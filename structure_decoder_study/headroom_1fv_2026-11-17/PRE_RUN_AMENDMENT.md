# Pre-run controller correction — 17 November 2026

The implementation review caught a real status-classification defect after the
first setup freeze and before any real-case reconstruction, algebra adapter or
search execution. A worker result file saying `completed` could have been
accepted even if the child subsequently exited abnormally.

The corrected controller requires exit code zero, no watchdog stop, a readable
worker report and 24 completed gates/searches before accepting completion.
Nonzero exits/signals, unreadable reports and incomplete reports remain distinct
unresolved outcomes. Ten declared classifier probes cover these conditions.
The controlled CPU-limit probe accepts SIGXCPU or SIGKILL without an external
watchdog stop, accommodating platform CPU-limit signal semantics. Both remain
abnormal exits for the actual worker and can never count as successful completion.

`pre_run_v1/` preserves the first frozen plan, source and selection, with hashes
and a no-execution record. The scientific inputs, case IDs, source algorithms,
thresholds and budgets are unchanged. Version two will be frozen only after the
correction is reviewed. The old frozen source hash refers to the archived v1
source; it is not expected to match the corrected live source.

This correction follows a pre-execution code review, not inspection of a rescue
outcome. No case has been reconstructed, replaced, excluded or searched.
