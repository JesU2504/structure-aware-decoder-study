# Bounded BB144 witness pilot — 17 November 2026

This exploratory pilot implements the AI supervisor's recommendation in
`../publication_strategy_2026-11-17/supervisor_failure_target_review.md`.
It is a new injected-pattern experiment, not a reproduction of an unspecified
published fault support. No model will be trained. All cases are development.

## Frozen inputs and question

Reuse the validated BB144 r=12, p=0.001 Z-memory circuit, un-decomposed Stim DEM,
ordered H/L, exact parity priors and repository additive priors from
`../failure_target_2026-11-17/construction_probe/`. Verify that stage's manifest.
The question is whether a small fixed stress panel contains an exactly
replayable BP+LSD logical failure, whether a larger BP budget changes it, and
whether established higher-order post-processing repairs it.

“Weight four” means four distinct **merged detector/logical-signature columns**.
It is not asserted to mean four physical gate faults or a uniquely specified
set of four raw DEM events. Preserve raw DEM indices and probabilities for each
merged column. No circuit-distance or bounded-distance-correctability claim is
permitted from a label or a successful recovery of one injection.

## Panel preparation before decoder calls

Use NumPy PCG64 seeds 2026111711 (connected), 2026111712 (uniform) and
2026111713 (execution order). Freeze 128 distinct supports and all 512 initial
job assignments in `panel.json`, `jobs.json` and `frozen.json` before calling
any decoder, including adapter checks. Preparation is allowed to read only
structure and priors, not decoder outcomes.

- Cases 0–63: choose a uniform random root column; grow to four columns by
  repeatedly choosing uniformly from the sorted union of columns sharing at
  least one detector with a selected column. Exclude selected columns. Restart
  a dead-end or duplicate support; log attempts/root/growth. Cap generation at
  10,000 attempts per half.
- Cases 64–127: uniformly sample four distinct columns without replacement;
  reject only exact support duplicates already in the panel.
- Retain zero-syndrome and zero-logical-flip patterns. Compute the true syndrome
  H e and logical flips L e, rather than assuming that injected errors flip a
  logical observable. Store the probability of exactly that merged support in
  log form under the exact independent DEM distribution.
- Record pairwise column overlap and a detector-only torus-translation key
  (13 blocks of 72 detector labels on a 12 by 6 grid). This key ignores logical
  basis transforms and is only a relatedness flag, not a certified full-circuit
  automorphism or an independent-family count. Report how many keys repeat.
- Shuffle case order and the four configurations within each case, using the
  execution seed. Timing is descriptive; no latency-quantile estimate is intended.

## Decoder, comparisons and adapters

Use installed ldpc 2.4.1. Pin hashes of its compiled BP+LSD module, shipped
Cython source and interface, and record Python/NumPy/SciPy/Stim versions.
Set thread environment variables to one before numerical imports. Baseline:
minimum-sum BP, scale 0.625, parallel schedule, seed 0, one OpenMP thread,
`bits_per_step=1`, `lsd_method=LSD_0`, `lsd_order=0`,
`always_run_lsd=False`, input vector type syndrome. Cross BP caps {30,100}
with priors {exact,additive}, giving 512 panel decode calls. Create a fresh
decoder for every call to avoid hidden state carried between syndromes. Record
construction CPU/wall time separately from decode CPU/wall time.

**Comparator choice declared before outcomes:** use the package's existing
`LSD_CS` order 2 with `always_run_lsd=True`, BP cap 30, and both prior vectors.
Also run forced LSD order zero to distinguish forcing from higher-order search.
This is an established package reprocessing control, not the supervisor's
illustrative truncated 1FV comparator, not a new decoder, and not a guarantee of
greater accuracy. The installed 2.4.1 docstring and shipped Cython explicitly
expose the forcing option; its nonzero-syndrome path calls LSD even when BP
converges. Zero syndrome still has an early return.

Before the panel, use at most 16 counted adapter calls (13 planned): each of
the four baseline settings on zero and singleton-column-0 inputs (8); native,
forced-order-zero and forced-order-two on a 3-bit repetition check matrix (3);
the two forced settings on the BB singleton with exact priors (2). Check output
shape/binary values, H/L reconstruction, configured order/method, and an
independent exhaustive weighted valid-correction comparison for the toy case.
Enable package cluster statistics on adapters and forced comparisons to verify
post-processing actually executed on nonzero syndromes. If these checks fail,
stop before the panel; do not silently replace the comparator or alter settings.

## Outcomes, selection and replay

Store every invocation's ID, phase, case/configuration, source hashes, correction,
BP hard decision, BP convergence flag, iterations, syndrome residual, logical
prediction and timing. Ground truth is used only by the external evaluator;
neither decoder nor comparator receives the true fault support or logical flips.
Keep these outcomes distinct:

1. syndrome-valid and correct logical class;
2. syndrome-valid and wrong logical class;
3. invalid correction (including BP nonconvergence separately as a stage flag);
4. exception, interrupted call or resource-censored call.

Correctness requires both H e_hat = H e and L e_hat = L e. BP convergence is
not the convergence/correctness of the complete BP+LSD pipeline. A nonconverged
BP stage followed by successful LSD is a correct full result.

After all 512 panel calls, select at most eight cases with any invalid or
logical-failure result, in ascending case-ID order. For each, greedily select
one unused case correct under all four settings, prioritizing same panel half,
then closest syndrome weight, then closest exact log probability, then case ID.
Record unmatched attributes; these are descriptive controls, not a causal or
balanced-sample inference. All cases have merged weight four. Select no cases
for the repair phase if there are no failures.

For the selected cases (at most eight failures and eight controls), replay
exact BP30 and exact BP100 and, if different, the first failing configuration
in the fixed order exact30, exact100, additive30, additive100. Maximum 48
replay calls. Require exact correction, BP output and classification equality;
if replay differs, preserve it and suspend deterministic-witness claims.

For those same cases, compare forced order zero and forced order two at BP30
with both prior vectors, maximum 64 calls. Require nonempty cluster statistics
for nonzero-syndrome calls before claiming post-processing ran. On zero
syndromes explicitly mark the package's zero-syndrome bypass; do not call it a
failed stronger search. Retain all corrections and rescue/regression transitions.

## Management caps and interpretation

Maximum 640 decoder invocations, including adapters, initial panel, replays and
comparators. At most 16+512+48+64=640; only 13 adapters are planned. Stop before
starting any additional decode if cumulative measured process CPU time reaches
1,200 seconds or elapsed run wall time reaches 1,800 seconds. Count initialization,
imports and evaluation overhead in the run totals. Record a start journal before
each call and flush every result. A native call can overrun a between-call cap;
report any incomplete/censored coverage. These are management limits, not a
power calculation, a guarantee of finding a failure or a hardware deadline.

If the fixed panel has no failure, report inconclusive for the existence of
rare harmful patterns and stop this local search. Do not raise noise, enlarge
the panel or reduce iterations to manufacture a witness. If a logical failure
is found, save an independently checked replay packet. A successful comparator
only demonstrates recovery of that particular injection. Failure of this
comparator leaves broader repair headroom unknown.

The enriched panel estimates neither natural logical-error rate nor natural
latency quantiles. Do not treat 512 configurations of 128 supports as 512
independent circuits or trials of a noise distribution. Static compiler features
are fixed on this DEM. A successful pilot alone establishes neither predictive
generalization, a compiler decision improvement nor a new publication claim.
