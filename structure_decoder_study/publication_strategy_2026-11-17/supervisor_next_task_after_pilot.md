# Supervisor recommendation after the all-correct pilot

17 November 2026. Separate AI review, not external human peer review. I read
the completed pilot protocol/results/audit and inspected primary methods and
public source. I ran no decoding, fitting, sampling or installation.

**Primary recommendation: reproduce a published natural-noise failure regime
with a runnable, already-supported backend. Stop the local weight-four search.**
The concrete task is BB144 Z-memory, **24 rounds, p=0.007, BP@20 plus OSD-0**,
from [Adaptive decoding through decoder disagreement](https://arxiv.org/html/2609.37629v1).
Its Appendix A1 reports 398 logical failures among 20,000 shots at this point.
That makes a small fixed natural-noise sample a plausible witness-reproduction
task; it does not guarantee a failure in any particular seed.

This is an explicitly different, published regime and backend. It must not be
presented as modifying BP+LSD until the previous pilot fails. **It is replication,
not a new publication result.** No manuscript drafting is needed.

## Interpretation of the completed pilot

The fixed panel found no BP+LSD failure. The 185 BP nonconvergences followed by
correct LSD output are successful complete decodes, not failure witnesses.
The verified forced-LSD adapters addressed the earlier early-return concern.
Choosing that established comparator before outcomes was reasonable; no repair
phase occurred, so there is no measured repair headroom on difficult cases.

The result does not contradict RelayBP/ImpulseBP/ELMS findings. The panel neither
enumerated their harmful classes nor tested their decoders. It also establishes
neither a natural logical-error rate nor universal weight-four correctability.
Further local sampling would currently be searching without a distinct claim.

## Access and exactness: what is verified and what is still a gate

The public [Adaptive-qLDPC repository](https://github.com/UCL-CCS/Adaptive-qLDPC)
contains the generator, converter and runner. I retrieved their source through
GitHub's contents API at commit `8cc32014a6461bb8f241f47f62a7e74f63817738`.
The construction/fast-path dependency chain uses NumPy, SciPy, Stim and ldpc,
which are already available. The source also imports a configuration module
that creates an output directory: isolate the new source snapshot.

**Do not launch `adaptive_v1_run.py` unmodified.** It invokes matched K500,
K1000 and full one-free-variable sweeps on every shot. A small reproduction
should call the reviewed construction helpers and native fast decoder directly.

The source retains one column per raw DEM error, rather than performing a
detector-only merge. However, its target accumulation does not explicitly XOR
repeated detector/logical targets across decomposition separators. Whether such
repeats occur in this task is untested here, not an established converter bug.
It also clips probabilities. Independently check complete detector-plus-logical
signatures and prior semantics before decoding; do not silently replace the
converter and still call the outcome an exact reproduction.

The paper reports H of shape 1800 by 12240 and rank 1794, with twelve logical-Z
observables. **Matching construction and semantics is an entry gate, not a
result already verified here.** Dimensions alone are insufficient. The prior
12-round generator and its 8784 merged columns are a different representation;
merely doubling its round parameter is not the requested reproduction.

## One bounded executable pilot, after that entry gate

Freeze the source, circuit/DEM, H/L, priors, sampler seeds and job order first.
Verify noiseless behavior, CSS/logical conditions and raw-DEM syndrome/observable
reconstruction with independent parity semantics. Stop on unexplained mismatches.

Then draw **512 natural circuit-noise shots**, two independent seeds of 256,
at the fixed published point. Decode all shots with:

1. The published fast path: installed ldpc 2.4.1 BP+OSD-0, min-sum scale 0.625,
   parallel schedule, BP cap 20 and one thread.
2. Our established BP+LSD0 at caps 30 and 100, on precisely those same syndromes
   and actual observables. These are paired controls, not the same algorithmic
   budget or a claim of an optimal decoder comparison.

Keep nonconvergence, invalid correction, syndrome-valid logical error, exception
and resource censoring separate. Save complete correction vectors, BP state,
logical predictions and costs. Evaluate logical equivalence, not equality to an
unobserved physical fault vector. Natural sampling does not supply a unique
raw/merged/physical fault support.

After the full sample, select the first at most eight fast-path failures and
eight matched successes under a predeclared rule. Check exact replay and apply
the already verified forced LSD0/CS2 controls if useful. Retain rescues and
regressions. A correction on one case demonstrates that case's recovery, not
bounded-distance correctness. Record initialization separately from service.

Suggested management limits: **1800 total decoder calls including adapters,
warmup and replays; 20 measured CPU minutes; 30 wall minutes**. These are proposed
resource choices, not power calculations or hardware deadlines. A native call
can overrun a between-call cap. Mark incomplete coverage instead of removing
slow cases. If the fixed sample has no failure, report that result and investigate
reproduction differences; do not increase noise or search seeds indefinitely.

The output is one independently checked replay packet, all 512 paired outcomes,
and a small correctness/cost transition table. It is not a trained predictor or
an estimate of an extremely low error-floor regime.

## Publication and compiler boundaries

This task directly answers the request for a decoder with a published failure
regime and public implementation. It does **not** itself establish novelty.
Risk-guided rescue, repair headroom, serial cost and cross-family routing already
have close prior art. Replacing OSD with LSD or changing a feature is insufficient
as the next paper claim. No distinct publishable extension has been established.

The original compiler-cost question is conceptually more aligned with compilation,
but its missing decision/cost contract remains. A logical-failure packet cannot
repair that gap: static circuit features are identical across shots of one DEM.
Online risk prediction is a different interface. Return to the compiler path
only with a concrete task-level decision that these failure/cost measurements
would change.

I recommend **no second fallback search now**. RelayBP memory reproduction is
possible after configuration/access work, but adds an installation and baseline
matching problem. The coordinator's complete saved Relay tree found memory
circuits, not the exact logical-operation circuits advertised more broadly;
the Tour-de-gross operation benchmark is therefore an access lead, not a ready
bounded task. This does not prove those artifacts are globally unavailable.

Run the proposed reproduction only as a tightly bounded diagnostic foundation.
If it supplies merely the already published behavior and no concrete new gap,
retain the reproducible packet and stop rather than promise a publication.
