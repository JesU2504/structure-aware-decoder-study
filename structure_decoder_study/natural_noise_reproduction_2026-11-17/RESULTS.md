# Natural-noise failure reproduction — 17 November 2026

**The experiment produced independently checked, replayable logical decoding
failures: 12 of 512 shots for BP20+OSD0.** BP+LSD30 and BP+LSD100 failed on
the same twelve shots. All returned corrections satisfy their syndromes.

This is a small replication of the public source's Z-memory setting, not a new
decoder, trained predictor, compiler result or established publication claim.
The pinned paper reports 398/20000 fast-path failures at this operating point
([Methods and Appendix A1](https://arxiv.org/html/2609.37629v1)). Different seeds,
sample count and CPU platform prevent calling this an exact numerical rerun.

## Setup and entry checks

The public Adaptive-qLDPC source was pinned at commit
`8cc32014a6461bb8f241f47f62a7e74f63817738`. Nine small files were downloaded
with byte-count, Git-blob and SHA256 checks. We invoked only the reviewed
construction/conversion helpers and native decoders, not the source entry point
that runs expensive truncated/full searches on every shot. Dependencies were
already installed; no installation or prior-result change was needed.

The source circuit has 144 data qubits and 72 Z-check ancillas, 24 extraction
rounds, p=0.007, and twelve logical-Z observables. It extracts **Z checks only**;
this scope is not a full both-check memory or hardware demonstration. The
source's noisy circuit model was preserved.

All 24 entry checks passed. H is 1800 x 12240, GF(2) rank 1794, with 34,992
nonzero entries; L is 12 x 12240. Independent parity conversion exactly matches
the source H, L and raw DEM priors. This actual DEM contains no separator hints
or repeated targets, and source prior clipping changes no values. The earlier
static concerns therefore do not create an observed discrepancy in this task.
CSS/logical commutation, independence and pairing checks passed. Sixteen
noiseless circuit samples, 64 DEM validation samples and a synthetic parity
replay passed; none is part of the 512-shot evaluation sample.

The execution protocol, reviewed source, runner, compiled modules, circuit,
matrices, priors, observations and job order were hashed before any decoder
call. Frozen setup SHA256:
`2cc97376823f7a31014e631b7eb77050d9ddc79732336bc04af05bb55c2e4f00`.
Independent pre-run checks verified all 512 syndrome vectors lie in H's column
space. The AI supervisor approved the protocol conditional on those freezes and
the adapters passing. This is internal AI review, not external human peer review.

## Fixed paired experiment

Natural circuit-noise sampling used seeds 2026111731 and 2026111732, 256 shots
each. All three configurations saw the same cached syndromes and actual logical
flips. One persistent instance per configuration and seed block matched the
source usage pattern; configuration order within each case was shuffled using
the predeclared seed. Min-sum scale was 0.625, updates parallel, thread count one,
schedule seed zero, ldpc version 2.4.1.

| Configuration | Logical errors / shots | Invalid corrections | BP nonconverged but full decoder correct | Mean service time |
| --- | ---: | ---: | ---: | ---: |
| BP20 + OSD0 | 12/512 | 0 | 475 | 6.77 ms |
| BP30 + LSD0 | 12/512 | 0 | 471 | 11.48 ms |
| BP100 + LSD0 | 12/512 | 0 | 469 | 24.87 ms |

Each observed logical-error fraction is 2.34375%, with a **marginal** Wilson 95%
interval of 1.346%–4.052%. These are paired outcomes, not three independent
replications; these intervals establish neither simultaneous superiority nor
equal true error rates. Each configuration had nine errors in the first seed
block and three in the second.

All three settings failed on the same case IDs:
23, 24, 51, 66, 131, 167, 188, 228, 249, 256, 260 and 407.
There were zero native rescues or regressions relative to the primary over all
512 paired shots. LSD30 changed 185 correction vectors relative to OSD20 and
LSD100 changed 206, without changing the final correct/incorrect classifications.
All twelve failures were BP-nonconverged cases; this run does not demonstrate
silent logical failure after BP convergence.

The service times are descriptive wall times for these fixed configurations on
this macOS arm64 CPU context. They exclude separately recorded initialization
and evaluator/I/O overhead. Main initialization took about 15.7–16.0 ms per OSD
instance and 5.2–5.5 ms per LSD instance. Different BP budgets and post-processors
are not matched computational work, and no optimality or hardware-deadline
conclusion follows. These are not the paper's Xeon timing measurements.

## Selected replay and forced reprocessing

The first eight primary failures by case ID and eight unused nearest available
primary successes were selected using the frozen rule, without consulting LSD
outcomes. All eight failures selected for this phase came from the first seed
block. The comparison cases are **nearest available controls**, not uniformly
close matches: the case-23 control differs by 44 syndrome bits and the case-66
control by seven. See `selected_pairs.json` for every matching difference.
Do not use this panel for a causal cost comparison or a population rescue rate.

All sixteen selected cases were replayed on fresh instances of all three native
configurations: 48 calls. Correction vectors, BP decisions, convergence flags,
iteration counts and outcome classifications matched the original calls exactly.

Existing forced LSD0 and LSD combination-sweep order-two reprocessing at BP30
were then applied to these same sixteen cases: 32 calls. Cluster statistics
confirm the forced processing executed. Neither setting repaired any of the
eight selected failures or damaged any of the eight selected successes.
This is a selected-case diagnostic. It does not test the paper's K1000/full-1FV
search or establish that other algorithms cannot repair the shots.

## Independent audit and reproducible packet

The audit recomputed H times correction and L times correction for all 1,627
calls, using the saved observations, and verified binary values, hashes, planned
job coverage, source/native fast-path readout equality and all replay comparisons.
No saved LLR array contains a nonfinite value. Deterministic sampler regeneration
reproduced both 256-shot blocks bit for bit; it checks provenance of the same
512 observations rather than supplying new independent samples. All eighteen
earlier manifests were verified unchanged. The audit made zero decoder calls.

`witness_packet/` contains the first independently checked logical-failure case
(23), its cached syndrome/actual labels, circuit/DEM, H/L/priors, decoder/version
metadata and all its native, replay and forced-comparison outputs. Its sample
provenance is seed 2026111731, within-seed index 23. It asserts no unique raw,
merged or physical fault support for that natural-noise observation. The
syndrome-valid correction has the wrong measured logical class and reproduces
on a fresh instance with the frozen native settings.

There were **1,627 completed decoder calls**: eleven adapters, 1,536 main paired
calls, 48 selected fresh replays and 32 forced comparisons. No call was incomplete
or removed. The run used about 34.90 CPU seconds and 35.41 wall seconds, below
the declared caps. No new model, training sample, reserved program or manuscript
was produced. The earlier low-weight pilot remains a separate all-correct
experiment and was not enlarged or reinterpreted as this result.

## Research decision

The failure-witness feasibility gate now passes. Increasing the BP cap and the
tested local reprocessing did not change logical correctness on these observed
cases, so “more iterations will repair them” is unsupported. Broader repair
headroom remains unknown under this experiment's controls.

The result supplies an audited baseline and failure packet. A distinct
publication contribution and a task-level compiler decision remain unestablished.
Risk-guided rescue and serial cost already have close prior work. Further runs
should answer a specific new question rather than merely seek additional errors.
The [final AI supervisor review](../publication_strategy_2026-11-17/supervisor_natural_noise_reproduction_review.md)
accepts the technical objective, finds no material implementation defect in the
reviewed path and requests no additional experiment to complete this milestone.
It retains the Z-check-only scope, weak nearest-control matches, selected-case
interpretation and unestablished publication novelty.
