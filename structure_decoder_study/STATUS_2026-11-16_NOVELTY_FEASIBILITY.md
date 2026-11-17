# Novelty and feasibility check — 16 November 2026

Latest assessment: [novelty_feasibility_2026-11-16/assessment.md](novelty_feasibility_2026-11-16/assessment.md).

Generic selective measurement is established; the exact proposed QEC timing
profile/admission workflow is plausible but unverified as novel. Primary-source
overlaps and their boundaries are documented in the separate AI review at
[qec_prior_art.md](novelty_feasibility_2026-11-16/qec_prior_art.md). This is not
external human peer review or an exhaustive priority search.

The prototype is feasible, but publication evidence remains weak. At the
inherited 2 ms diagnostic, a frozen linear base6 filter followed by profiling
every proposed admission matches uniform profiling's five admissions at
1,249.990 ms versus 3,087.996 ms of recorded partial cost. The absolute saving
is only 1.838 seconds. The nonlinear density filter is slightly more expensive;
the earlier deadband saves only 18.911 ms beyond the linear control while
accepting one unprofiled task. No complexity advantage is demonstrated.

Costs omit preparation, warmup, and training amortization; all 19 tasks/seven
parents are inspected development data. Matching uniform profiling does not
establish complete useful coverage or calibrated future safety. The original
graph-p95 improvement claim remains unsupported.

Recommendation: one bounded consumer/full-cost gate before any new experiment.
Specify a meaningful planner workload, real budgets and reuse, then assess net
cost against uniform profiling and the frozen linear filter. Only a credible
material benefit warrants a small independently frozen program-level trial.
Do not resume the old placement trial or enlarge training merely to obtain a
positive result. No publication outcome is promised.

This check made zero new decoder calls and fitted zero models. Raw replay and
prior integrity verification passed; see
[audit.json](novelty_feasibility_2026-11-16/audit.json). Earlier snapshots remain
unchanged. This is a new status note, not a replacement of frozen history.
