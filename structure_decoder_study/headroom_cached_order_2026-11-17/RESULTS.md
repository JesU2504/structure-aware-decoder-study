# Known search rescues ten of twelve recorded failures

17 November 2026. New adapted Python 1FV diagnostic using saved implementation-
derived orders. This is separate from the preserved, stopped stable-order run.

**The full search repaired 10/12 recorded BP20+OSD0 failures. All twelve fixed
success controls remained correct. K500 and K1000 produced exactly the same
correction vectors as full search on every one of the 24 selected cases.**

| Search budget | Recorded failures repaired | Failures remaining | Selected success controls made incorrect |
| --- | ---: | ---: | ---: |
| First 500 free variables, secondary | 10/12 | 2/12 | 0/12 |
| First 1000 free variables, secondary | 10/12 | 2/12 | 0/12 |
| All 10446 free variables, primary | 10/12 | 2/12 | 0/12 |

These are nested choices from one candidate enumeration, not three independent
experiments. The controls were fixed by original case order, not randomly
sampled or matched to failures. All observations were inspected development data.

Rescued IDs: 23,24,51,66,167,188,249,256,260,407. Remaining failures: 131 and228,
with four and three incorrect logical bits respectively. Both remaining failures
improved the channel-prior scoring surrogate but stayed logically incorrect.
This does not establish whether another enumerated candidate could repair them,
whether deeper search would help, or whether they are intrinsically uncorrectable.

## What was checked

The pre-run plan froze 118 input files, SHA256
`f81a98641c5d831373a503e22ab3cccb4d483c49a9563f9fcbe9c415b8724739`.
The previous 24-case selection, exact priors and cached native BP/OSD vectors
were retained. Cached orders were applied through unique rank priorities only
in reconstruction. Scoring used original log(1/p) channel weights. No ctypes,
new sorting, BP/decoder calls, physical samples, training or noise changes ran.

All24 baseline corrections matched bit for bit BEFORE the first real search.
The complete journal contains 97 ordered phase events. The worker received
sanitized inputs without true observables or case roles. Source first-argmax
and strict-positive-improvement choices were preserved, with all output arrays
saved before the separate logical classification.

The independent audit imported no search helpers. It rebuilt all250704 full
candidate vectors in small batches, checked all1800 syndrome equations using
int64 arithmetic, and recomputed complete weighted-vector scores. Maximum
delta disagreement was 1.7053e-12, below the frozen1e-8 absolute plus1e-12 relative
tolerance. It verified source selection rules, prefix-score monotonicity,
ordering/pivot coverage, all saved outputs, normal exits and resource accounting.
All21 previous local result manifests remain unchanged.

Ties exist. Case167 has a best/second score gap of about1.42e-14; case407 has
an exact tie. All near-minimum candidates on these rescued cases were logically
correct. Controls4 and264 have near-zero best improvements; the source no-change
rule was retained. No case had both correct and incorrect candidates within
the declared score tolerance of its minimum. These observations do not imply
robustness to different information-set ordering or a different score objective.

## Cost and containment

The worker completed normally with15.211CPU seconds and15.616wall seconds.
Peak child RSS was595525632bytes (567.94MiB). The independent audit completed
normally with28.629CPU seconds and29.404wall seconds, peak460.05MiB. Both were
below their separately declared600CPU/900wall-second/1GiB operational ceilings;
neither watchdog reported a stop or monitor error. RSS polling is not a hard
instantaneous memory guarantee.

Per case, mean reconstruction CPU was91.55ms, full source scoring/pick90.43ms,
and in-worker candidate verification51.13ms. These phase costs exclude cached
BP/OSD work; total worker cost also includes integrity checks, adapters and I/O.
K500/K1000 were derived from full enumeration, so no separate truncated-search
latency or end-to-end speedup is measured. This Python diagnostic is not an
optimized native implementation or a hardware deadline test.

## Design and execution review

Before freezing, review found avoidable repeated NPZ decompression in the audit.
Caching the array and validating saved direct-score shape/finite values fixed
that efficiency/integrity issue before any real reconstruction. No post-outcome
code, tolerance, case-selection, budget or tie-policy change was made.

The independent audit and AI supervisor postcheck found no material execution
or design error within this declared diagnostic. This is internal AI review,
not external human peer review. Known limitations remain: selected small panel,
single H/L graph and Z-check-only circuit, implementation-specific tie order,
unobserved native pivots and a known surrogate search objective. No model was
trained here, so training duration is not an experimental variable.

## Research decision

**Feasibility GO:** verified recoverable failures now exist on this testbed.
**New-method/paper expansion NO-GO under the present framing:** this uses a known
search and does not establish a distinct structural or compiler contribution.

Do not report a new2/512 logical-error rate. Only twelve of the500 native-success
observations were searched; regression behavior on the other488 is unmeasured.
The12-control result cannot establish a population regression rate. Exact baseline
matches do not establish hidden native pivot equivalence or portability.

Preserve this reproducible testbed. Start a larger campaign only after identifying
a specific new mechanism or a consequential decision not already addressed by
prior work. A compiler claim requires varied valid circuit tasks, inputs available
to the compiler, and a demonstrated decision benefit; this run supplies none of
those. Do not automatically start routing, model training or manuscript drafting.

See [frozen protocol](PROTOCOL.md), [risk outcomes](RISK_OUTCOME.md),
[independent audit](result_audit.json), [case table](outcomes.csv) and
[AI supervisor review](../publication_strategy_2026-11-17/supervisor_cached_order_headroom_review.md).
