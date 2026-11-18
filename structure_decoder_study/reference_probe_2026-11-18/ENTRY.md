# Available-backend entry assessment

18 November 2026. Follow-up to the supervisor's saved-list diagnosis. This is
post hoc oracle-assisted analysis of two inspected observations, not an online
decoder, new method, error-rate estimate or compiler experiment.

SciPy1.17.0 and its bundled HiGHS1.8.0 are installed. The public SciPy milp API
supports time/node limits and an integer-parity optimization formulation. The
public QLDPC certification reference uses this same standard formulation in
AppendixC; we are not implementing its branch-and-bound certifier.

- [SciPy versioned milp documentation](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.milp.html)
- [QLDPC reference formulation and numerical limitations](https://arxiv.org/html/2610.28008v1)
- [HiGHS feasibility/tolerance documentation](https://ergo-code.github.io/HiGHS/dev/guide/kkt/)

The solver's floating lower bound, optimal status or infeasible status does not
provide a rigorous exclusion certificate for the real task. This entry permits
only a ONE-SIDED witness test: an independently verified feasible correct-class
vector cheaper than the CURRENT FULL-1FV WRONG WINNER establishes an outside-list
competitive representative. No such witness leaves the question unresolved.

Before real solves, test the exact same model builder against exhaustive small
binary instances, including dependent rows, integral parity slack, forced bits
and an infeasible fixture. Freeze code/options/inputs after supervisor preflight.
Use existing binary corrections to verify real model feasibility before solving.
No new dependency, certifier, full-class enumeration or model change is required.

Count reference-optimization calls explicitly. They are additional decoding-related
computation even though no BP/OSD/LSD or quantum sampling call is made.
