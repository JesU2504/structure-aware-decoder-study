# Focused related-work record

Checked 12 November 2026. This is a bounded primary-source screen, not a priority
certificate. Statements about absence refer only to inspected material.

| Work / source | What it already supplies | Consequence for this study |
|---|---|---|
| [PACE, sections 5.1 and 7.6](https://arxiv.org/html/2608.11719v1) | Decoder-aware TCNOT scheduling, volume-based feasibility, DEM composition, and a documented single-to-multi-patch performance extrapolation. | Scheduling and DEM reuse are prior work. Test additional structure beyond strong size/sparsity baselines. |
| [Triage, section V-D](https://arxiv.org/html/2605.04459v1) | Finite-pool scheduling and calibrated latency jitter depending on distance/noise. | Generic queues and stochastic decoder latency are prior work. |
| [Localized statistics decoding](https://arxiv.org/abs/2406.18655) and [published article](https://doi.org/10.1038/s41467-025-63214-7) | Reliability-guided local decoding, on-the-fly elimination, cluster-dependent complexity and a parallel formulation. | Cluster-dependent cost is known. Investigate cheap *pre-execution* features and decision value. Do not equate the package's serial execution with the theoretical parallel formulation. |
| [A Case for Elastic Quantum Error Correction Decoders, arXiv:2406.17995v4](https://pages.cs.wisc.edu/~amolavi/files/eurosys26.pdf), especially section 7.4 | Capacity planning, task allocation, spatial/temporal windows, and sensitivity to lognormal latency tails. The current author-hosted PDF has this title despite search metadata using another title. | Tail-aware allocation is already established. The inspected tail study measures a memory-code PyMatching distribution; our proposed missing-information question concerns different circuit-derived task structures. [Public artifact](https://github.com/satvikmaurya/decoder-resources) is a possible later fixed scheduling harness, not validated here. |
| [CUDA-Q Logical](https://research.nvidia.com/publication/2026-09_cuda-q-logical-retargetable-compilation-fault-tolerant-quantum-computing), September 2026 | Retargetable FTQC compilation with schedule-derived resources, typed QEC artifacts, DEM composition, and classical-control interfaces. | Preserving compiler-visible structure and replacing aggregate estimates are broad existing ideas. Our narrower candidate concerns measured decoder service-time prediction and its incremental decision value. Relevant alternative source of future realistic workloads; not installed here. |
| [BP+BP+OTF](https://www.nature.com/articles/s41534-026-01292-1) | Decoder graph sparsification and runtime reduction under circuit-level noise. | Sparsity is a serious cost driver and a mandatory baseline. |
| [GreenPeas, v2](https://arxiv.org/html/2604.16613v2), [public code](https://github.com/abbrazi/GreenPeas) | GPU JIT DEM construction, adaptive-circuit decoding, and configurable correlation levels trading accuracy against speed. | Constructing richer error models and studying their cost/accuracy tradeoff are prior work. Count error-model construction overhead and freeze correlation assumptions; our candidate contribution is incremental prediction for compiler choices. GPU tooling is not required for the CPU entry pilot. |
| [TMCBS](https://github.com/basilthebeagles/tmcbs), [associated article](https://doi.org/10.1038/s41467-026-75693-3) | Public multi-block logical-circuit builders and decoder integration. | Use pinned circuits and independently check conversion/metrics. Stage 1 uses its logical-Z detector sector, with explicit scope limits. |
| [NV-Fusion latency guide](https://nvidia.github.io/cudaq-qec/performance/nv_fusion_latency_user_guide.html) | Measured streaming-tail latency for a windowed matching decoder. | Monolithic full-block CPU service time is different from streaming response latency. Our entry pilot cannot claim the latter. |

The remaining contribution hypothesis is therefore specific: static,
circuit-derived structural features add predictive information after dimensions,
nonzeros, and expected activity, and the information improves choices among
legal schedules at controlled operational risk. The present pilot does not yet
establish that hypothesis.
