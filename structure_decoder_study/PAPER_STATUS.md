# Publication status and claim ledger

Research question: can inexpensive circuit-derived structure improve decoder
budget decisions beyond dimensions, sparsity, expected activity, and conservative
padding?

This directory contains the first experimental milestone, not a completed paper.
No venue, publication date, novelty priority, or positive result is assumed.

| Claim | Required evidence | Current status |
|---|---|---|
| Public multi-patch workload access | Pinned generator running without mocks | Passed for the restricted TMCBS corpus |
| Meaningful generated operations | Noiseless checks and logical truth tables | Passed for the custom logical-Z experiments; upstream basis tests also passed |
| Faithful matrix conversion | Exact sampled DEM reconstruction and physical-sampling consistency | Passed on the 78-case corpus |
| Volume prediction fails materially | Repeated matched-size measurements | Observed in the restricted corpus; up to 6.11x mean spread |
| Structure adds beyond sparsity/activity | Grouped held-out comparisons and controls | Not established: selected extra features worsen held-out p95; mean sensitivity is mixed |
| Benefit survives ordinary decomposition | Connected-task or actual decomposition controls | Not established; ordinary decomposition itself gives 1.57x median speedup on disconnected controls |
| Full FTQC logical accuracy | Complete detector/observable coverage and adequate failure statistics | Outstanding; present corpus is one sector |
| Deadline-risk prediction is calibrated | Independent calibration/test circuits and sufficient tails | Outstanding; current admission curves are descriptive |
| Better compilation decisions | Legal same-program candidates with different useful tradeoffs | Outstanding; present schedule variants have equal round counts |
| Net benefit after overhead | Full construction/extraction/profile accounting | Construction costs recorded; deployment comparison outstanding |
| Paper-level generality | Independent program families, realistic windows, robustness | Outstanding |

The most informative next experiment depends on Stage 1. If dimensions and
sparsity suffice, do not add model complexity simply to obtain a positive result.
If structure helps only on disconnected full matrices, test ordinary component
decomposition before investing in the topology claim. If a residual survives,
move to fuller detector coverage and realistic window boundaries, then a
controlled schedule-choice experiment.

Stage 1 and the paired controls are complete. The primary campaign has 468,000
shots; the separate decomposition control has 54,000 paired physical shots.
Independent audits passed. Slow-shot CPU/wall replay confirms that selected
half-second extremes consume decoder CPU time. This motivates careful tail-work
measurement, but does not establish a new predictive model or a paper claim.
See `findings.md` for the numerical results and `NEXT_GATE.md` for the next
bounded decision.

Any follow-up must explicitly freeze the detector basis/representation. A graph's
structure is a property of the chosen decoder input as well as the physical
circuit. Alternative legitimate detector combinations or sparsification can
change decoder cost and accuracy, and may be stronger baselines than a richer
predictor on an unnecessarily difficult representation.
