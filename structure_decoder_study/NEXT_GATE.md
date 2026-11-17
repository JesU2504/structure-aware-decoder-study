# Next bounded research decision

The Stage 1 added-feature model did not earn a paper claim. A strong simple model
predicts p95 reasonably on average, while one held-out case is underpredicted by
1.79x. Genuine rare CPU-intensive decodes also make mean cost uncertain. These
facts motivate one independent validation gate, not a larger model search on
the existing corpus.

## Prerequisites before new timing

1. Obtain an independently checked circuit family with complete intended
   detector/observable coverage and a specified realistic window/commit policy.
   The current public TMCBS logical-Z sector remains a diagnostic source.
2. Freeze detector basis, DEM correlation assumptions, priors, decomposition,
   decoder parameters, and the definition of service versus response latency.
3. Construct diverse **connected decoder tasks after ordinary decomposition**.
   Include multiple genuinely different parent logical programs, rather than
   just more placements of the same small motifs.
4. Produce legal candidate schedules of the same parent programs with useful
   execution-time/decoder-load tradeoffs. Verify logical action and measure
   logical accuracy rather than assuming it is preserved by timing changes.
5. Include a simple decomposition-aware sparsity/activity predictor, a calibrated
   conservative margin, and matched-budget direct profiling as baselines.

## Measurement target

Pick the operational target from the compiler use case before fitting: mean
service for throughput, an explicit deadline exceedance probability, or a
quantile with a justified sample budget. Record process CPU and wall time in the
next harness. Use repeated sessions and an explicitly documented sampling rule
for rare expensive LSD work. Do not promote the current diagnostic p99 into a
reliability guarantee.

Explain residual cost using BP work and separately instrumented LSD cluster/
factorization work. Such execution measurements are diagnostics, not features
available to the compile-time predictor.

## A concrete continue/stop test

First evaluate the strong simple predictor on untouched parent programs. If its
remaining errors do not alter a useful schedule decision at the specified risk
level, retire the original added-topology contribution. If decisions do change,
test a small prespecified structural correction on a separate training set and
fresh test programs; require that it improve the decision over conservative
padding and profiling after total overhead is counted.

The real rare-cost observations may motivate a narrower tail-work question, but
that would require its own independent evidence. No observed pilot result is
being relabeled as proof of that alternative contribution.
