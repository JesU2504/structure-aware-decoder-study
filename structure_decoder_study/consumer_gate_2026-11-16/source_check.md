# Primary-source consumer check

Accessed 16 November 2026. Focused method inspection, not an exhaustive search.
These papers support related decisions; none was verified here as a consumer
of our particular selective-characterization policy.

| Source inspected | Actual decision and contract | Consequence for this project |
|---|---|---|
| [PACE v1](https://arxiv.org/html/2608.11719v1), §§5.1–5.3, 6.1, 7.6 | Select a short schedule from a bounded spacing family; every window must satisfy preparation, memory and decoding-path constraints. The arrival interval is commit length times extraction-round duration; the setup uses distance times 1 ms. Calibration averages five warmed runs. | A table over our mixed-program fixture is not that schedule-selection job. Its latency abstraction is not our specified 5% p95-miss contract. |
| [Triage v1](https://arxiv.org/html/2605.04459v1), §§III, V-D/E | Dispatch shared decoder resources. A lognormal jitter model is calibrated with 15K PyMatching shots per setting. | Demonstrates a real calibration activity, but does not provide our uncached candidate stream, profiling-cost bottleneck or CPU BP+LSD accuracy/timing requirements. |
| [DART-Q v1](https://arxiv.org/html/2605.09142v1), §§III-B, V-B/E | Admit live jobs according to backlog; the workload service proxy is explicitly not an absolute runtime predictor. | Live queue admission is not evidence of demand for our offline measurement-purchase workflow. |
| [Delfosse et al.](https://arxiv.org/html/2310.15313), §§4–6 | Runtime/failure measurements inform decoder, distance and stopping-time selection. | A real offline measurement consumer, but our schedule-fixture filters have not been connected to its objective or cost burden. |

The local pinned TMCBS source and our existing circuit tests establish access
to circuit-derived inputs. They do not establish an integrated compiler trace
with cache misses, costs and requirements. Focused searches for PACE/Triage
implementations did not yield a verified integration for this gate. A dated
author comment about release plans surfaced in search, but its direct page
was inaccessible; it is not used to claim current code unavailability. Search
absence is not a finding that code does not exist.

Inference used only as a sensitivity point: applying the cited distance-times-
round-time formula at our d=5 with a 1 ms round gives 5 ms. This is not a
reproduction of the paper's hardware, window pipeline, latency statistic or
fault-tolerance setting. It does not make our 5% timing-tail allowance valid.
Both 2 and 5 ms already belong to the frozen diagnostic sweep; neither was
added after this source check.
