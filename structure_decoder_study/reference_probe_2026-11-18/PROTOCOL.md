# Two-case, one-sided reference witness probe — 18 November 2026

## Scope and decision rule

Use the existing public SciPy1.17.0/HiGHS1.8.0 optimizer, validated on four
exhaustively checked tiny fixtures. This is a standard parity-MIP adapter,
not a new certifier. Investigate ONLY development cases131 and228, in that
order, of the frozen BB144/r24/p=.007/Z-check-only task. No new physical samples,
BP/OSD/LSD calls, score changes, online decoder, training or manuscript.

The logical target is the known actual observation; this is post hoc oracle-
assisted mechanism diagnosis. It cannot itself be deployed at runtime.

Minimize the SAME source S(x)=sum_i log(1/p_i)x_i over all12240 binary fault
variables, subject to every1800 detector and12 observed logical equations.
Encode each parity row by sum(x)-2z=b, with BOTH fault and parity-slack variables
integral. Slack bounds are0 through floor((rowdegree-b)/2). No objective cutoff,
restricted subgraph, extra search variant, noise modification or alternate score.

The comparison threshold is the CURRENT SAVED FULL-1FV WRONG WINNER: about
520.87671 for131 and450.11581 for228. It is not the older OSD0 baseline.
Before solving, independently check one saved correct-class correction against
the complete MIP matrix, bounds and integer domains, and check that the wrong
winner has the correct detector syndrome but fails the target logical equations.
No warm start is supplied; the SciPy public API does not expose one here.

An independently verified correct-class witness cheaper than that wrong winner
beyond the frozen score tolerance proves an outside-list competitive correct
representative exists. It does NOT prove global decoder success: another wrong
class might also improve. No witness means UNRESOLVED. Infeasible/optimal solver
status or numerical lower bounds never prove absence or certify the real optimum.
Solver infeasibility without a cutoff contradicts the known feasible vector and
stops interpretation as a backend/formulation error.

## Entry, freeze and implementation validation

The four entry fixtures cover dependent/cyclic equations, a forced even-parity
case requiring INTEGER slack, a zero-syndrome case and inconsistent duplicate
rows. Compare against exhaustive binary enumeration; keep its call counts.
Entry passes only with normal process exit and within its15CPU/30wall-second/
1GiB ceiling. Preserve the exact entry-tested source snapshot; verify the model,
feasible-vector validation and solver-interface functions are unchanged in the
execution worker. Worker reporting glue may add explicit invocation journals,
without changing those tested helpers or solver options.

Freeze this protocol, entry report/snapshot, solver options, monitor/worker/audit/
controller code, installed binary hash and all prior input/known-witness files
before either real solve. The AI supervisor must review the concrete code and
preflight before freeze, then inspect completed evidence before the final reply.

## Fixed budget and records

One attempt per case, no retries or outcome-driven tuning. Each solver gets
60 seconds and10000 nodes; one CPU thread, seed0, presolve enabled, relative
gap0 and mip_feasibility_tolerance1e-8. The enclosing child has90CPU/120wall-
second/1GiB operational limits. Count trials that are rejected or incomplete.
RSS polling does not guarantee instantaneous hard containment. Fixed second
case still runs after an ordinary solver limit; a validation/formulation error
stops further case execution. Save logs, options, messages, numeric estimates,
raw incumbent arrays, checked integer arrays and reference-call chronology.

Four toy reference-optimization calls and up to TWO real reference-optimization
calls are additional decoding-related computation. Do not report blanket zero
decoding computation. Zero new BP/OSD/LSD calls and physical shots remains true.

## Witness verification and limitations

Require finite returned arrays and integer proximity<=1e-7 BEFORE rounding.
Then check every binary/domain constraint and every integer parity equation
EXACTLY after rounding. Never repair an invalid vector's parity. A valid incumbent
from a time-limited solve can establish existence; lack of one is inconclusive.

Recompute BOTH the new correction and saved wrong winner with identical frozen
float64 log(1/p) coefficients. Compare dot products, independent math.fsum and
exact Fraction sums of these binary floating coefficients. Declare better only
if the exact represented-coefficient difference exceeds atol1e-8 plus rtol1e-12
times the maximum absolute score. Solver objective discrepancy is descriptive;
a checked feasible vector supplies its own independently verified objective.
This does not certify exact real logarithms or the physical circuit posterior.

The independent audit imports no solver/model helpers. It verifies frozen input
hashes, raw integer proximity, binary bits, auxiliary equations, allH/L rows,
known correct feasibility, source-winner identity, costs and outside-list status.
An improvement must also beat the best correct-class member in the old saved list.
Check its free-coordinate pattern against that list's baseline/single-free forms.

Prior full-class optima and coset probabilities stay unknown. Numerical HiGHS
dual estimates are recorded only as such; a trustworthy real-case lower bound
is NOT available in this probe. No population error-rate improvement, practical
repair method, ML certificate, intrinsic uncorrectability or novelty follows.
