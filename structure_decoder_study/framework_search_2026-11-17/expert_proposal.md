# Mechanism proposal: safeguarded Anderson mixing inside BP

17 November 2026. Internal AI research review, not external human expert review.
This document proposes a possible pivot from compiler cost prediction to improving
the decoder's iterative inference. No experiment, candidate enumeration, decoder
call, fitting, source modification or new physical sample was performed.

**Recommendation: retain safeguarded Anderson acceleration as one conditional,
modest transfer hypothesis. Do not describe it as a new decoder or start a
performance campaign until message-state access and baseline fidelity pass.**

## What needs explaining

The checked adapted one-free-variable search repaired10/12 recorded native
BP20+OSD0 failures, while cases131 and228 remained incorrect. Improving the
surrogate score did not repair those two cases. Their cause is still unknown:
missing logical-class coverage, wrong representative selection, model mismatch
and other mechanisms have not been distinguished. We must not design this
proposal using their true fault supports or true logical labels.

All twelve baseline failures followed BP nonconvergence, but487 of512 BP20
shots were nonconverged and475 of those were nevertheless correctly repaired by
OSD0. Thus nonconvergence is not a useful failure label by itself. The relevant
question is whether a different inference trajectory can produce better final
corrections or reduce necessary postprocessing at a real computational cost.

## Adjacent-field shortlist and prior-art screen

| Candidate transfer | Mechanism | Assessment |
| --- | --- | --- |
| Numerical nonlinear solvers: Anderson acceleration | Combine a small history of BP message residuals to propose a better next state; reject poor proposals | Preferred conditional pilot: concrete, no neural training, small added state; direct qLDPC-BP use not established by this search |
| Statistical physics: logical-class free energies | Aggregate probability across equivalent corrections instead of choosing one low-cost error | Scientifically appropriate but heavily occupied by coset MRF, sampling and region decoders; not a fresh generic contribution |
| Graphical models: separator/cutset-conditioned exact inference | Solve a bounded coupled residual region rather than independent local choices | Plausible but overlaps AC, LSD and region/elimination decoders; useful separator width and a distinct mechanism are unproven |
| Combinatorial optimization: logical-signature-aware candidate diversity | Allocate a fixed list to distinct logical classes and improve representatives | Directly covered by recent logical-space OSD theory; reject this generic novelty claim |
| ML/search distillation | Train a small policy on verified search trajectories | Already explicitly explored by a decoder-model-factory framework; substantial data and generalization burden, weak first choice here |

Primary sources checked:

- [Walker and Ni, 2011](https://users.wpi.edu/~walker/Papers/Walker-Ni%2CSINUM%2CV49%2C1715-1735.pdf): Anderson methods accelerate fixed-point iterations using a short residual history; they are related to Krylov and secant methods.
- [Zhang, O'Donoghue and Boyd, 2020](https://web.stanford.edu/~boyd/papers/pdf/scs_2.0_v_global.pdf): safeguarded/restarted Anderson methods have convergence results under explicit operator assumptions. We have not established these assumptions for min-sum BP.
- [ADMM penalized decoding with Anderson acceleration, 26 August2026](https://ieeexplore.ieee.org/abstract/document/11666833/): already transfers Anderson mixing, regularization and safeguards into classical LDPC optimization decoding. The proposed transfer is specifically to qLDPC BP dynamics, not invention of this framework.
- [quimb's official BP documentation](https://quimb.readthedocs.io/en/latest/autoapi/quimb/tensor/belief_propagation/d2bp/index.html), checked17November2026: already exposes DIIS/Pulay acceleration for tensor-network BP with a history window and mixing parameters. Applying residual-history mixing to BP in general is therefore not novel either. Anderson, DIIS and Pulay must all be included as search terms and comparison baselines.
- [Certified decoding of quantum LDPC codes, 26 August2026](https://arxiv.org/html/2608.25545v1): already studies class-partition functions, sampling and a region hierarchy, blocking a generic statistical-physics novelty claim.
- [Logical-space OSD theory, 17 October2026](https://arxiv.org/html/2610.24503v1): explicitly separates coverage loss from representative-selection loss and constructs coverage-aware lists. The two current residual failures cannot be presented as a discovery of that distinction.
- [Ambiguity Clustering, 20 June2024](https://arxiv.org/abs/2406.14527): already divides BP's residual problem into independently decoded regions.
- [Decoder Model Factory, October2026](https://arxiv.org/abs/2610.41398): already proposes model-guided search and trajectory distillation. Abstract-level positioning only in this review; this is not a full reproduction.

## The preferred framework, operationally

Let x be the vector of variable-to-check log-likelihood messages on H's nonzero
entries. For the fixed syndrome, priors, min-sum scaling and update schedule,
one ordinary parallel BP sweep defines a map F(x). Its message residual is
r(x)=F(x)-x. The hypothesis is that slow or oscillatory modes in this iteration
can sometimes be reduced by short-history nonlinear acceleration.

For up to m+1 recent, actually evaluated states x_i, form residual columns r_i.
Choose coefficients by the small constrained problem

    minimize || sum_i alpha_i r_i ||_2^2 + lambda ||alpha||_2^2,
    subject to sum_i alpha_i = 1.

Propose

    y = (1-beta) sum_i alpha_i x_i + beta sum_i alpha_i F(x_i).

Evaluate F(y) to check its actual residual; the linearized combination is not
itself an acceptance certificate. Accept y only if finite and its residual
satisfies a frozen decrease criterion. Otherwise take the ordinary damped step
and clear history. Restart for ill-conditioned history or excessive coefficients.
Use consistent BP posteriors from an evaluated state, not independently mixed
posterior vectors. Count and, where valid, reuse every evaluated F(y).

Define the state at one coherent phase of the update: complete outgoing
variable-to-check messages for an unconverged sweep, with posteriors derived
fresh by the next check pass. The native implementation tests the hard syndrome
before its final extrinsic-message write, so a direct state snapshot at early
return cannot be treated as a completed sweep. Before a pilot, declare whether
a safeguard probe producing a valid syndrome is an eligible correction and in
what chronological order; use the same rule for ordinary look-ahead controls.
Otherwise the probe could silently become an extra candidate ensemble.

A reasonable first frozen configuration is history m=3, beta=0.5 and a small
scale-relative ridge, with coefficient-norm rejection and no per-shot tuning.
Exact constants, residual normalization, tie/clipping rules, update cadence and
the budget must be declared before even a development pilot; these illustrative
choices are not empirically selected recommendations. No clipping may be added
only to one arm without an explicit control.

The intervention changes the BP frontend, leaving the specified parity model,
noise priors and final scoring objective fixed. A message residual decrease is
only an algorithmic safeguard. It proves neither syndrome correctness nor the
correct logical class. It is not a certificate that decoding improved.

## Essential comparators and novelty boundary

[Relay-BP, June2025](https://arxiv.org/abs/2506.01779) already uses disordered
memory, relaying and multiple trajectories to change BP behavior. [PriorTilt,
9November2026](https://arxiv.org/html/2611.13373v1) perturbs selected prior LLRs
using decoder-state information. [TEMPO-BP, 16November2026](https://arxiv.org/html/2611.21086v1)
already controls memory strengths online through a predicted local response,
syndrome residuals and confidence, and reports broad comparisons.

Anderson's short global least-squares combination differs operationally from a
local memory-gain controller and sparse prior perturbations. That distinction
is a hypothesis worth checking, not sufficient novelty or an accuracy promise.
In particular, TEMPO is a mandatory close comparator, not optional background.
Generic BP+DIIS is already implemented in quimb, so a generic transfer claim
is ruled out. Focused Anderson/DIIS/Pulay searches did not establish priority
for the narrower quantum-error-correction min-sum setting. Priority remains
unknown. A useful contribution would need a distinct QEC-specific finding
about safeguards, wrong-class convergence and actual resource tradeoffs, beyond
running an existing accelerator on a new example. Novelty risk is high.

The safeguarded-operator theorem assumes properties such as nonexpansiveness
and existence of fixed points. Neither has been proved for this min-sum update;
therefore no general convergence theorem is inherited. Nonsmooth min selection,
wrong-class stable fixed points and global mixing overhead are central risks.

## First task and decisive pilot, conditional on entry

First task: inspect and verify an interface exposing the full per-edge state
and a faithful one-sweep F. Cached final LLRs cannot implement this method.
Also establish a legitimate interface from the modified BP outputs to the
declared postprocessor. If native ldpc does not expose that boundary, do not
silently substitute the earlier Python OSD reconstruction and call it native
BP+OSD. Either build and validate a documented backend or stop this entry task.
The root agent's source inspection found internal per-edge message fields and
a parallel update in the verified ldpc bp.hpp, but no corresponding step/message
callbacks in the installed Python wrapper. Its BP+OSD wrapper calls the full BP
routine before handing final LLRs to native OSD. A documented compiled instrumented
module is a possible implementation route; ctypes field access is not proposed.

Before testing acceleration, ordinary F must reproduce an independently checked
BP implementation on small dependent/cyclic fixtures and the source native
configuration on a frozen case panel, including stop iterations, hard decisions,
posteriors within declared precision and final outcomes. A failed adapter blocks
the pilot; no cases may be removed to make it pass.

If entry passes, use the existing512 observations as DEVELOPMENT data, not just
the twelve failures. Freeze all arms before running: ordinary BP, ordinary BP
with matched extra F evaluations, fixed damping, and safeguarded Anderson.
Keep the same postprocessor and its budget across arms. Add the close dynamic
memory comparator before any publication claim. A zero-history/no-acceleration
mode must reduce to its declared baseline; an unsafeguarded variant is a later
mechanistic ablation, not a reason to tune many variants now.

Record logical failures, rescues AND regressions over all512, syndrome validity,
postprocessor invocation, actual CPU/wall/RSS, F-evaluation count and rejection/
restart statistics. Count every safeguard trial, least-squares solve, posterior
formation and parity test. Compare actual cost as well as operation counts;
reducing reported iterations alone cannot establish a benefit. Use one CPU
thread and predeclared600CPU/900wall-second/1GiB ceilings for the bounded pilot;
a resource or adapter stop is unresolved, never accuracy failure.

Proceed only if a fixed variant shows a useful accuracy-cost signal against
matched plain BP AND fixed damping, attributable to the history intervention
rather than extra compute, followed by a separately frozen untouched-program/
noise confirmation. For the development panel, require positive paired net
rescues at no worse measured total CPU than its equal-resource comparator,
or equal logical outcomes with a prespecified material CPU reduction. The
minimum material reduction is a protocol choice, not an observed threshold.

Stop if the frontend cannot be instrumented faithfully, residual reduction does
not improve final logical/cost outcomes, damping or extra sweeps explain the
gain, safeguard overhead removes it, or the close dynamic-memory literature
already implements the same mechanism. Do not increase histories, retune per
failed case or keep adding operating points until a positive outcome appears.

## Expert judgment

This is a reasonable small numerical-analysis hypothesis to investigate, with
medium implementation risk and high novelty risk. It avoids neural training
and does not require quantum hardware. It may fail precisely because improving
BP fixed-point convergence can stabilize the wrong logical answer. That failure
would be informative for this hypothesis but not automatically publishable.

The honest next deliverable is the interface/baseline feasibility verdict and
supervisor challenge to this proposal. The evidence does not authorize a claim
that AA will repair cases131/228, outperform TEMPO/Relay-BP, restore the original
compiler-cost story, or yield a publishable result.
