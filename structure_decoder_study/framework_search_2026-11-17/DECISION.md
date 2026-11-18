# Reviewed framework proposal

17 November 2026. A separate AI research agent proposed mechanisms; the AI
supervisor independently challenged the proposal. These are internal research
reviews, not external human expert validation. No experiments were run.

**Preferred candidate: safeguarded Anderson/DIIS history mixing inside min-sum
belief propagation. Conditional go for an interface/baseline feasibility check
only. Improvement and publication novelty remain unestablished.**

## The idea in plain language

BP repeatedly sends numerical evidence along the decoding graph. The proposed
framework keeps a few recent message states, solves a small least-squares
problem to combine them, and tests whether the proposed state actually reduces
the message-update residual. Unstable or unhelpful proposals trigger a declared
fallback and restart. This borrows an established numerical-analysis technique
for iterative equations, rather than training a neural decoder.

The proposed hypothesis is that this can reduce wasteful oscillation or slow
progress enough to improve final correction accuracy or total decoding cost.
Our current two remaining failures do not establish either mechanism. Faster
convergence can also stabilize an incorrect logical class.

Anderson acceleration is established in numerical analysis. BP software already
uses related DIIS/Pulay mixing, and classical LDPC optimization decoding already
uses Anderson acceleration. We cannot claim to introduce this framework to BP.
A useful QEC-specific outcome against strong controls would have to supply the
contribution. Novelty risk is high; implementation risk is medium.

## Why this candidate survived the shortlist

The expert considered five transfers. Logical-class coverage/list diversity,
statistical-physics probability aggregation, separator/local exact inference and
ML search distillation all have substantial direct prior art. The chosen
numerical intervention is precise, requires no neural training or quantum
hardware, and has a clear failure test. That makes it a reasonable bounded
exploration, not a demonstrated novel method.

## Supervisor conditions

1. Verify access to complete per-edge messages and a coherent BP sweep. Cached
   final LLRs are insufficient. The installed interface lacks the required
   step/message boundary; a documented source build would need validation.
2. Define an explicit plain-BP mode and a separate damping mode. A one-state
   history update with beta=.5 is damping, not plain BP. The expert accepted
   this correction before implementation.
3. Freeze whether a valid correction found during a rejected residual probe
   can be returned, and apply a consistent policy across comparisons. Charge
   every probe, matrix operation, parity test, restart and postprocessor call.
4. Any later pilot must compare ordinary BP, matched extra BP work, fixed
   damping and the proposed mixing on all512 development observations. Same-map
   DIIS/unsafeguarded-history attribution is needed before a safeguard claim;
   TEMPO-BP is a close comparison before a competitive method claim.
5. Judge final logical outcomes and measured total CPU, including regressions.
   Lower residuals or fewer nominal iterations alone do not demonstrate success.

The current proposal does not specify a frozen performance protocol. Parameters,
state phase, fallback/probe semantics, budgets and untouched confirmation access
remain prerequisites. Existing inspected cases cannot provide final confirmation.

## Decision

The next task would be one bounded source-interface and unmodified-baseline
validation. If the baseline cannot be reproduced faithfully within its declared
cap, stop. If entry passes, a separate reviewed development protocol can test
whether history mixing adds value beyond its controls. Stop that direction if
damping/extra work explains the effect or measured cost removes it.

This is a possible pivot toward decoder internals. It does not establish the
original structural-cost-model or compiler-decision claim. No implementation,
benchmark expansion, training or manuscript was started in this review.

Read the [expert proposal](expert_proposal.md), [supervisor review](supervisor_review.md)
and [expert response](expert_review_response.md). Primary references include
[Anderson acceleration](https://users.wpi.edu/~walker/Papers/Walker-Ni%2CSINUM%2CV49%2C1715-1735.pdf),
[existing BP/DIIS](https://quimb.readthedocs.io/en/latest/autoapi/quimb/tensor/belief_propagation/d2bp/index.html),
and [TEMPO-BP](https://arxiv.org/html/2611.21086v1).
