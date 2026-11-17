# Bounded BB144 pilot result — 17 November 2026

**No complete-decoder failure was found on the fixed 128-pattern panel.**
The declared search is finished. This is inconclusive about rare harmful
patterns outside the panel and supplies no failure witness for a new predictor.
We did not enlarge the panel, raise noise or weaken the decoder after observing
this result.

## Executed comparison

Before any decoder call, we froze 64 connected and 64 uniformly drawn, distinct
weight-four merged-DEM-column supports, input/source hashes and all 512 initial
jobs. The independent pre-run audit checked connectedness, distinctness,
probabilities, H/L labels and coverage of all four settings. No zero-syndrome
patterns happened to be selected; they were not excluded by outcome or syndrome.

The circuit was BB144 Z-memory with 12 extraction rounds, p=0.001, 936 detectors,
12 observables and 8,784 merged fault columns. The installed ldpc 2.4.1 backend
used BP+LSD0, min-sum scale 0.625, parallel schedule, seed 0, one thread and
one-bit cluster growth. Each invocation constructed a fresh decoder.

| Decoder priors | BP iteration cap | Complete decoder correct | Invalid corrections | Syndrome-valid logical failures | BP did not converge, LSD corrected |
| --- | ---: | ---: | ---: | ---: | ---: |
| Exact parity merge | 30 | 128/128 | 0 | 0 | 47 |
| Exact parity merge | 100 | 128/128 | 0 | 0 | 45 |
| Repository additive | 30 | 128/128 | 0 | 0 | 47 |
| Repository additive | 100 | 128/128 | 0 | 0 | 46 |

These are four paired evaluations of the same 128 supports, not 512 independent
circuits or random physical-noise trials. The 185 BP-stage nonconvergences are
successful full-pipeline decodes after LSD fallback. They are not logical or
validity failures of BP+LSD.

Thirteen counted adapter calls passed before the panel. In particular, the
installed package's `always_run_lsd=True` path and its existing combination-sweep
order-two reprocessing were verified on a toy case that BP converged on, using
nonempty cluster statistics and exhaustive toy correction scoring. Full-BB
singleton adapters also verified forced processing. We selected this existing
forced-LSD comparator before outcomes, in place of the supervisor's illustrative
truncated 1FV control. No new decoder was implemented or dependency installed.

No failure cases triggered the selected replay/repair phase. Consequently this
pilot has no evidence about repair headroom on failed BB144 injections. Passing
adapter checks is not a demonstrated repair of a difficult case.

## Independent verification and sensitivity

The saved-output audit recomputed syndrome validity and logical correctness
for every one of the 525 calls, and checked its correction/BP hashes and planned
job order. A separate deterministic replay through Stim, using one raw-event
representative for each selected merged signature, confirmed H/L labels on all
128 cases. This introduced no random noise sampling or additional decoder calls.
123 of 128 patterns have nonzero true logical-observable flips, so the result
is not explained by a panel containing only zero logical labels.

The decoder returned exactly the injected four-column support in 265 of 512
panel calls; other returned supports were still syndrome-valid and logically
equivalent under the experiment's observable map. We evaluated corrections by
their syndromes and logical class, not by equality to the hidden error vector.

Increasing the BP cap changed seven returned corrections for each prior vector,
with no correctness change. Changing additive to exact priors changed one
correction at BP30 and three at BP100, again with no correctness change. This
shows a measured effect on some correction choices; it does not establish a
logical-error effect or general irrelevance of the prior approximation.

There were 525 completed decoder invocations: 13 adapters plus 512 panel calls,
zero incomplete calls and zero post-panel decoder calls. The execution process
used about 7.77 CPU seconds and 7.83 wall seconds, below the 640-call, 20-CPU-minute
and 30-wall-minute caps. Initialization and decode timings are stored separately.
They are descriptive measurements of this fresh-instance stress pilot, not warm
service benchmarks, estimates of natural p95 latency or a hardware deadline test.

All 17 previous result manifests were verified unchanged, including the prior
failure-target entry check. New artifacts preserve the fixed panel, every raw
correction, call journal, source hashes and audit. No training samples, fits,
reserved workloads or physical Monte Carlo noise samples were used.

## Decision

The feasibility gate for an exactly replayable full-decoder logical failure was
**not met**. There is no basis here for training a failure predictor, claiming
extra BP iterations repair logical errors, or asserting a compiler improvement.
The natural next research decision is whether a distinct, practically useful
cost-modeling question exists in the prior task-level evidence. This pilot does
not justify another failure search under altered settings. Reproducing another
published backend's exact failure would be a separately scoped replication,
with its own access/settings requirements and unestablished publication novelty.

This result neither contradicts published trapping-set failures of different
decoders nor proves BP+LSD correct on all weight-four supports. The panel was a
small, enriched structural stress sample; it did not enumerate trapping sets,
certify circuit distance, estimate a natural logical-error rate or test
generalization across circuit families.
