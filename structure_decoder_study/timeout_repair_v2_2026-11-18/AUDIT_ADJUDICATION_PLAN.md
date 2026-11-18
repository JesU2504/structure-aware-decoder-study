# Supplemental audit of saved outputs — explicitly post hoc

The original frozen V2 audit FAILED. Do not edit that audit, its frozen hash,
the controller/worker or any output. Record the failure in
audit_initial_failure.json. No optimizer/decoder/worker will run again here.

The failed assumption was that every ps CPU sample must be nondecreasing.
Two final samples instead report matching PIDs with zero RSS and zero TIME:
legacy_injected after handler restoration and deferred_injected after result
finalization. Both immediately precede process reaping; all earlier samples
are nondecreasing. No process-state field was sampled, so the OS state and
accounting mechanism remain unproven. Do not label this proven zombie behavior.

An independent AI supervisor read those records and accepted a new narrowly
scoped engineering adjudication, explicitly distinct from the frozen audit.
Freeze this rule and audit_adjudicated.py after review before executing it.

Only allow a CPU decrease if it is the LAST monitor sample, both CPU and RSS
are exactly zero, there is a previous positive CPU maximum, and the query
starts after a verified terminal worker marker. For the legacy control use
the restored-handler marker and expected LegacySignalStop/exit1/no result;
for a returned result require finalized/restored report and exit0. There may
be no watchdog termination in either exception. The unchanged worker code
must show no further solve/loop after that marker.

Retain the preceding positive CPU maximum as the measured CPU evidence; do
not replace it by zero. Require that maximum and final in-child CPU both stay
below the parent budget and agree within .1 seconds. All timestamps and every
other sample remain subject to the original strict checks. The two known
exceptions must be reported explicitly; no new exception class is permitted.
All original independent graph/score/optimality, signal, restoration, process
censoring, hard CPU crossing, wall stop and hash checks remain unchanged.

A supplemental pass does not turn the frozen audit into a pass. Report both
outcomes and the absence of direct state evidence. It can establish that the
saved controlled tests satisfy their substantive return/containment checks,
subject to this reviewed terminal-accounting exception. It cannot establish
production readiness, historical signal origin or any scientific improvement.
