# AI supervisor review of the stopped headroom run

17 November 2026. Separate AI review of the frozen protocol, runner, resource
records, saved gate outputs and independent audit. I made no reconstruction,
decoder, candidate-search or sampling calls. This is internal AI supervision,
not external human peer review.

**Verdict: the run respected its stop rule, and the post-run audit passes.
Repair headroom remains unresolved because the baseline adapter did not pass.
There is no valid stronger-search result to interpret.**

## What happened

The plan contained all twelve verified primary failures and twelve predetermined
BP-nonconverged successes, six from each seed block. Eight reconstructions
matched exactly: cases 0, 1, 2, 3, 4, 5, 23 and 24. The ninth, case 51, differed
from its cached native OSD0 correction in four bits. The runner then stopped,
before the full-search loop, as the frozen protocol required.

The fifteen remaining baseline cases were not attempted; they did not fail.
There were zero real-case 1FV searches, new native decoder calls or physical
samples. The synthetic algebra adapters did run, but their success does not
validate unexecuted real-case candidate or score checks. `search/` is empty and
there is no successful global-gate event or file.

The worker exited normally with `baseline_mismatch`; the controller preserved
that status rather than reporting completion. No resource censoring occurred.
The worker used about 1.45 CPU seconds and 1.61 wall seconds, with peak child
RSS 230,883,328 bytes. The resource and exit-classification probes passed. The
earlier controller completion-status bug was fixed before execution, with v1
preserved and scientific inputs unchanged.

## Independent checks and meaning of the mismatch

The coordinating audit verifies all 67 frozen file hashes, selection and archive
history, the nine saved gates, pivot ranks/identity, stable ordering and all
1,800 detector equations. It verifies the global gate prevented searches and
that all nineteen earlier result manifests are unchanged. I inspected the
result audit and separately computed the saved case-51 vector comparison.

Case 51 differs at columns 938, 940, 949 and 1006. Both corrections have zero
syndrome residual. Their XOR has zero H and L image; both still misidentify the
same nine measured logical bits. Their prior-weighted surrogate scores agree
up to approximately 1.1e-13 roundoff. Thus this discrepancy is **not a repair**.

All four changed columns have exactly the same cached float64 reliability and
prior. Two are Python pivots and two are Python free columns. This is strongly
consistent with the tie-order ambiguity identified before the run. However,
the native pivot ordering was not observed. Neither the existence of ties nor
the vector equality on other cases proves the exact causal mechanism.

Logical equivalence does not satisfy the frozen bit-for-bit gate. Changing the
baseline vector can change a one-free-variable neighborhood, and equal e0 would
not itself prove hidden native pivot equivalence either. The comparison must
remain labelled as an unresolved adapter problem, not as an unsuccessful
strong decoder, absence of rescue, or proof the published study is invalid.

## Recommended next action

Finish this milestone by preserving the stopped run and its audit; no extra
search is needed to complete the user's requested post-run check. Do not drop
case 51, try tie permutations until a preferred answer appears, or relax the
gate and reuse this protocol as if nothing changed.

If continuing this route, the next bounded task is a **reconstruction/ordering
diagnostic**: compare the exact native version's ordering rules with the pinned
Python stable-sort reconstruction on the cached case, then validate any proposed
adapter policy on a separately declared fixed panel. Derive the policy from
implementation evidence, not logical labels or whether it produces a rescue.
No candidate search is necessary to diagnose the present baseline discrepancy.
If a faithful adapter cannot be established at reasonable cost, stop the exact
reproduction route. A deliberately different Python-baseline experiment would
require an explicit new target and protocol.

The verified twelve-failure natural-noise testbed remains valid. This stopped
run adds a reproducibility limit for the proposed adapter, not a novel compiler
or decoder contribution. No training, undertraining, optimality, across-task
generalization or publication claim follows from it.
