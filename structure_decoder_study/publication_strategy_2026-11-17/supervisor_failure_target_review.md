# AI supervisor review: failure target

17 November 2026. Separate AI research review, not external human peer review.
I inspected the target decision, protocol, probe/audit outputs, public-access
record and pertinent primary methods. No decoder experiment, fit or installation
was performed, and no frozen artifact was changed.

## Judgment

**Keep BB144 only for a small witness-and-repair feasibility pilot. Do not begin
training a failure predictor or building an adaptive decoder.** The generator
access work is sound enough to prepare that diagnostic, with the prior mismatch
explicitly paired. We have not reproduced a decoder failure or established a
new publication question.

Logical-failure analysis is a scientifically coherent new direction, but is a
**fork from the original static compiler-cost question**. Within one fixed DEM,
compiler-visible features are constant across shots. They cannot identify its
individual harmful supports. Syndrome/decoder-trace predictors change the
interface to runtime decoding. A return to the compiler claim would require a
demonstrated task-level correctness–cost decision, not merely a difficult shot.

## Novelty and access

[Trapping Sets of Detector Error Models](https://arxiv.org/html/2608.11516v1)
already establishes low-weight failures and harmful topology concentration for
RelayBP, ImpulseBP and ELMS on the r=12 BB144 task. Its RelayBP experiment uses
301 legs and stops at the first valid estimate. Those findings do not establish
BP+LSD failure or identify an exact support in our ordered matrix.

[Adaptive decoding through decoder disagreement](https://arxiv.org/html/2609.37629v1)
is very close prior work: BB144 circuit-level experiments, risk-guided deeper
OSD search, measured serial cost, simple routing controls, cross-family transfer
and the distinction between risk ranking and repair headroom. Its principal
BB144 setting is 24 rounds at higher noise; these differences leave room for a
different diagnostic, but do not make that diagnostic novel automatically.
Its appendix also reports converged logical failures on BB72. Generic false
convergence or selective rescue therefore cannot be our new claim.

An exact published witness is **not necessary** to create a useful, independently
reproducible new witness. Waiting indefinitely for one is unnecessary. A bounded
search must be labelled a new stress experiment, not reproduction of an
unspecified published support. I prefer the already pinned BP+LSD backend for
this first feasibility question; installing RelayBP and reproducing its complete
setup is an alternative reproduction project, not a required entry step.

## Confounds that must be addressed

- The additive/XOR prior discrepancy is real, small and potentially relevant to
  ties or trajectories. Preserve both vectors and compare outcomes on identical
  supports. It does not invalidate H/L, prove the publication wrong, or prove
  an observable decoding effect.
- State whether “weight four” counts merged columns, raw DEM mechanisms, or
  physical circuit faults. These are not interchangeable. Retain the mapping.
  Neither the code label nor one successful repair certifies bounded-distance
  correctability for this circuit/fault model.
- Check syndrome validity and logical correctness separately. Nonconvergence,
  a returned invalid correction, and a syndrome-valid logical error are different
  outcomes; a resource-censored call is another outcome.
- More iterations or restarts can change outcomes in either direction. Record
  precision, ordering, seed, early stopping and all attempted results. Repeated
  randomized runs of one support do not create independent circuit families.
- **A nominally stronger native OSD setting can be misleading.** The official
  [ldpc BP+OSD documentation](https://software.roffe.eu/ldpc/ldpc/bposd_decoder.html)
  states that OSD is invoked only if BP fails to converge. A syndrome-valid wrong
  BP result can therefore bypass higher-order OSD entirely. Record which branch
  ran, or use a separately verified forced-search comparator; validate its
  starting correction, information-set reconstruction and H/L checks. Failure
  of a bypassed search is not evidence of no repair headroom.
  The public page labels itself 2.1.0; the coordinating agent separately checked
  that the installed 2.4.1 decode docstring states the same early-return behavior,
  without constructing or running a decoder.
- An enriched fault panel estimates neither natural logical-error rate nor
  latency quantiles. Support probability, location and decoder behavior can vary
  within the same topology. Ground-truth error supports are for evaluation,
  not an available runtime routing feature.

## One ranked next action: a bounded paired witness pilot

After a separate execution protocol and adapter checks, retain the current
BB144 r=12, p=0.001 circuit and ordered H/L. Use ldpc 2.4.1 BP+LSD0, minimum-sum
scale 0.625, parallel updates, one thread and fixed seed, with BP caps 30 and
100. These are our declared backend settings, not a claimed RelayBP reproduction.

Freeze **128 distinct weight-four merged-column supports before outcomes**:
64 generated by a fixed connected-local-support rule and 64 uniformly sampled
from columns. Log duplicate/orbit relationships and generation seeds. Keep
zero-syndrome patterns if they occur. Evaluate both exact and additive priors
at both BP budgets: 512 initial calls. Retain every attempted outcome.

For at most eight failures and eight weight/syndrome-weight matched successes,
selected by a frozen rule, check deterministic replay and an established,
verified forced-search comparator, such as the published truncated 1FV branch
with K=1000 on this H. It is an adapted comparison, not an exact reproduction
of the 24-round experiment. If its reconstruction cannot be verified, stop at
the witness and report headroom as unknown; do not write a new decoder instead.

My suggested management caps are **640 total decoder/forced-search invocations,
20 measured CPU minutes and 30 wall minutes**, stopping before starting further
calls when reached. A native call may overrun a between-call cap; report censoring.
These numbers are design choices, not power calculations, guarantees of finding
a failure, timing requirements of quantum hardware or publication criteria.

**Feasibility gate:** save at least one exactly replayable logical-failure packet
and a comparable success. Determine whether the failure persists with exact
priors and the larger BP budget and whether the comparator actually repairs it.
A repair demonstrates recovery of that particular injected case only. If no
witness appears within the fixed panel/cap, stop this local search as inconclusive;
do not lower the decoder budget or raise noise until failure appears.

**Novelty gate:** even a persistent, repairable failure is only a diagnostic
result. Proceed toward a paper only if it exposes a specific weakness that the
trapping-set and adaptive-disagreement methods do not already address, and its
relevance can be established on a separate natural-noise or justified weighted
sample. If established baselines explain and handle the behavior, retain the
reproduction record and stop this branch. Do not manufacture a router, a
compiler claim or a new feature merely to turn the witness into a paper.

This review recommends the pilot; it does not execute it. No manuscript or
prospectus is recommended at this stage, consistent with the user's constraint.
