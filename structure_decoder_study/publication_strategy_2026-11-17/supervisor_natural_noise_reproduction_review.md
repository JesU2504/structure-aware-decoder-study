# Independent AI supervisor review — 17 November 2026

**Verdict: the bounded reproduction passed its technical objective. It supplies verified whole-decoder logical failures and a reproducible failure packet. It does not yet supply a new publication claim.** This is a separate AI methods review, not external human peer review. I inspected the frozen runner, protocols, entry checks, saved-output audit, sampler-regeneration audit, selected pairs, and first witness metadata; I made no decoder calls or source changes.

## What the evidence establishes

The fixed BB144, 24-round, p=0.007 experiment completed all 512 natural circuit-noise shots and all 1,627 declared calls: 11 adapters, 1,536 main calls, 48 fresh replays, and 32 selected forced comparisons. Nothing was censored or extended after seeing outcomes. The run used about 34.90 CPU seconds and 35.41 wall seconds, within its declared management limits.

BP20+OSD0 returned 12 syndrome-valid logical failures and no invalid corrections: 12/512 = 2.34375%, with marginal Wilson 95% interval 1.3457–4.0516%. The two seed blocks contributed 9/256 and 3/256. This is compatible with the source paper's reported 398/20,000 at this regime; it is not proof that the underlying rates are equal or a replication of its precise seeds, sample size, or hardware timings. The regime and primary settings were selected from the [published study](https://arxiv.org/html/2609.37629v1), before these outcomes.

LSD30 and LSD100 fail on **the same 12 shots**, not merely the same number. They change 185 and 206 corrections relative to OSD20, respectively, without any correctness transitions. All 12 failures follow BP nonconvergence. Conversely, OSD20 correctly processes 475 other BP-nonconverged shots, so BP nonconvergence alone is not a whole-decoder failure.

Forced LSD0 and LSD_CS2 rescue zero of the eight selected primary failures and regress zero of the eight selected primary successes. Nonempty cluster statistics verify that post-processing ran. These tests do not reproduce the source's K1000/full-1FV search, and they do not show that stronger search cannot repair the failures.

The first packet, case 23, has zero syndrome residual and six wrong logical-observable bits. Its fresh-instance replay reproduces the correction and BP state. This is a genuine failure under the specified circuit/noise model; no unique physical fault support or fault weight has been identified. Neither a future successful repair of this shot nor the code's nominal distance would establish a bounded-distance correction guarantee.

## Implementation and design assessment

I found no material implementation error in the reviewed path. The runner immediately copies native correction, BP decision, LLR, and OSD readout buffers. Every OSD result matches the upstream `osd0_decoding` readout. Decoder inputs exclude the actual logical labels; labels enter scoring and later case selection only. Persistent main instances follow the declared seed-block order; all 48 selected fresh replays match their saved correction, BP decision, convergence flag, iterations, and outcome.

The independent audit recomputes all 1,627 correction outcomes with H/L and saved truth, finds no nonfinite LLRs, and verifies invocation accounting. The 512 detector/logical observations regenerate identically at the fixed Stim seeds. This regeneration checks provenance; it adds no independent samples. The earlier 18 manifests remain unchanged.

Entry validation resolves the converter concerns for this particular DEM: source and independent H/L/priors agree, dimensions and rank match the paper, and no repeated targets, separators, or clipped priors occur. That does not validate the helper for every possible DEM. Crucially, the 512 evaluation observations come from **circuit-noise sampling**, not independent sampling of the DEM's columns. The circuit measures Z checks only, so conclusions must retain that scope.

The selected forced comparison has limited generality. All eight failures selected by the declared first-failure rule occur in the first seed block. The controls are nearest available successes under the rule, not uniformly close matches: case 23 differs by 44 syndrome bits and case 66 by seven; six other pairs match syndrome weight exactly. No control-decoder outcomes affected selection. The conditional 0/8 result is therefore a diagnostic, not a population rescue-rate estimate or a controlled causal estimate of topology.

## Research judgment

There is no training or undertraining question in this experiment: nothing was fitted. Increasing the BP cap and changing post-processing demonstrate that these particular extra computations did not repair the observed cases. They do not establish convergence to an optimal decoder, algorithmic equivalence, or the absence of repair headroom. The numerical sample/call/time caps were pragmatic design choices, not power guarantees.

Retain this as a validated failure testbed and stop the declared run. Its replication value is real; observing known failures and trying two local comparators is insufficient for a novel paper. The close prior already studies risk-guided search and correctness/cost tradeoffs. Any later proposal must identify a distinct, falsifiable question before authorizing another campaign. This result supplies neither structural causation nor evidence for the original compiler cost-model claim. Syndrome, BP state, and cluster features become available at runtime; they cannot silently be treated as static compiler inputs. The measured service times are descriptive on this machine and imply no hardware deadline or compiler benefit.

No correction to the reported research conclusions is needed provided these boundaries remain explicit. No additional experiment is required to complete this milestone.
