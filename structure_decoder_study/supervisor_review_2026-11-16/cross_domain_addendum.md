# Cross-domain methods: AI supervisor addendum

**16 November 2026, Tokyo.** I am the same separate AI supervisor reviewer, not a human professor or external peer reviewer. This addendum reconsiders the earlier framing. It preserves `review.md` and all frozen evidence. I checked primary sources and performed a read-only policy replay: **zero new decoder measurements and zero model fits**.

## The proposed strategy is scientifically sound

**Yes. Importing a successful idea from another field is a legitimate research strategy, and it can support a paper without inventing a new ML algorithm.** The contribution can be identifying an important QEC problem, adapting an established method to its constraints, and establishing when it works through convincing experiments. Even a simple imported method can yield a valuable result.

My earlier review placed too much emphasis on a “distinctive method” and placement-selection benefit. Those are possible contributions, not mandatory forms of novelty. The proposed novelty veto should be a short exercise in specifying the contribution and its closest overlap, not a demand to prove that nobody has used a related algorithm before exploring it. Nor does a strong simple baseline close transfer research: it can become the inexpensive first stage of a useful system.

The earlier negative conclusion still applies to the **tested added-graph p95 proposal**. It does not apply to every way of importing performance engineering into QEC. Likewise, always-burst trivializes current *placement ranking*, but not absolute service-cost prediction. A planner still needs to know how much CPU capacity that chosen placement consumes, whether a service budget is met, and when to distrust its estimate.

A mean-model improvement could therefore matter through capacity estimation even when every selector chooses the same placement. For a specified stable workload, arrival rate times mean worker occupancy informs utilization; finite pools, waiting times, and feedback deadlines require additional modeling. We should test that consumer explicitly instead of assuming that a smaller prediction error factor implies either usefulness or uselessness.

## Three candidate families, ranked for this project

### 1. Decision-sensitive calibration with selective profiling — most promising

The source-field idea is to retain an inexpensive cost model, identify estimates whose errors could change a consequential decision, and spend extra measurement effort selectively. In databases, Wu et al. show that calibrated optimizer models can be competitive and investigate refining estimates before execution. Progressive optimization adds checkpoints and triggers expensive reconsideration when estimates threaten plan validity. These are methodological precedents, not QEC results. [Wu et al., ICDE 2013](https://www.microsoft.com/en-us/research/publication/predicting-query-execution-time-are-optimizer-cost-models-really-unusable/), [Markl et al., SIGMOD 2004](https://db.cs.berkeley.edu/cs286/papers/robust-sigmod2004.pdf).

Our adaptation would decide **which circuit-derived tasks need physical-syndrome profiling before resource admission**, rather than replace the decoder or re-optimize a running SQL plan. It fits the evidence: the nonlinear base is cheap and often adequate, historical padding can overreject, and direct profiling is available but costs work. The research question becomes whether selective measurement improves the resource/risk/measurement-cost frontier.

This does not require graph features to win. Their value would be tested as one possible measurement-allocation signal, alongside base-model uncertainty and noise-support diagnostics. It is a different hypothesis from “topology necessarily improves p95 regression.”

### 2. Mechanism-informed empirical performance prediction — plausible, less immediately decisive

[SATzilla](https://arxiv.org/abs/1111.2249) exemplifies empirical hardness modeling: inexpensive instance characteristics predict algorithm performance for a specified objective, with hierarchical models for heterogeneous instance classes. The transferable principle is to model distinct execution regimes instead of treating all runtime as one smooth response.

For BP+LSD, distinguish zero syndromes, BP convergence, and fallback work. A compile-time predictor would estimate their probabilities and conditional costs from H, priors, and allowed static information. BP iterations and cluster statistics can supply training/diagnostic labels; future realized syndrome or execution statistics cannot be disguised as compile-time inputs.

This might explain why p95 is predictable while means remain sensitive to rare LSD work. However, selected slow-shot replays do not estimate fallback-cluster frequencies, zero-syndrome native flags need masking, and the small corpus cannot support many component models. Moreover, LSD already studies noise-sensitive clusters, unconditional timings, and long tails. Mechanism awareness itself is therefore insufficient novelty; it must improve calibrated resource estimates or measurement efficiency. [LSD v2, Appendix C.4](https://arxiv.org/html/2406.18655v2).

### 3. Per-instance decoder/configuration portfolios — weakest present fit

SATzilla's portfolio idea selects among complementary solvers. Here that could mean choosing decoder settings or implementations under a logical-quality constraint. The first prerequisite is genuine complementarity, not a learned selector.

BP100 has higher point p95 in all nineteen bridge configurations and no established accuracy advantage; it is not presently a compelling “strong expert.” Standard component decomposition should be applied where appropriate rather than learned as a novel choice. A useful portfolio would need alternatives with reproducible, quality-aware crossover benefits.

QEC selection is also occupied: neural ensemble decoding already classifies syndromes to component decoders, decoder switching escalates from a fast decoder using reliability information, and PACE selects graphlike versus unmatchable backends from window structure. [Sheth et al., 2020](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.101.032338), [Decoder Switching](https://arxiv.org/html/2510.25222), [PACE v1, §4.1](https://arxiv.org/html/2608.11719v1). A static circuit-level cost/quality portfolio could differ, but “SATzilla for QEC” would not establish that difference.

## The precise transfer I recommend investigating

Choose **selective pre-execution profiling for decoder resource admission**. Borrow the decision-sensitive measurement principle, not the terminology or a source-field theorem. A short physical-shot profile is a noisy measurement of the *same* decoder, not a lower-fidelity decoder whose accuracy may be substituted freely. In particular, BP30 is not a proven low-fidelity surrogate for BP100, and truncating expensive calls changes the estimand and potentially the accuracy semantics.

The QEC-specific work is substantial: preserve physical syndrome/observable sampling; separate logical quality from timing misses; group complete parent programs; handle noise shifts with identical H/L; account for decomposition, detector conventions, ordering, and warm versus cold operation; and charge measurement/setup overhead. Public circuits pose no intrinsic privacy problem here. Differential privacy or federated learning would need an actual motivation; expensive runtime labels, not confidential data, are the immediate constraint.

The closest systems overlap remains important. Triage already calibrates stochastic latency, and elastic decoders already study capacity sharing with tails. [Triage v1, §V-D](https://arxiv.org/html/2605.04459v1), [Elastic decoders v4](https://arxiv.org/pdf/2406.17995v4). The possible contribution is narrower: demonstrating **when scarce profiling should replace a static estimate, and whether this improves a quality-aware admission/capacity decision at measured total cost within a stated domain and calibrated policy**. The deadband rule below is not already safe or established as novel. I have not established priority for the proposed comparative result.

## One small test: a zero-shot selective-profiling replay

Before considering the earlier sixteen-parent trial, test whether this imported hypothesis has any useful headroom. The existing bridge has frozen parent-excluded predictions, independent 192-shot profiling streams, and separate 1,536-shot evaluations. These are sufficient for a development feasibility replay without fitting anything.

I ran a minimal first pass using this fixed rule on all nineteen configurations:

1. Accept when the frozen RBF density8 **padded** p95 prediction fits the budget.
2. Reject when its **raw** prediction exceeds the budget.
3. Otherwise consult the existing profiling p95 upper bound and admit only if that bound fits.

The raw/padded bracket is an empirical heuristic, **not a confidence interval**. Historical padded predictions already failed under noise transfer in the earlier stress experiment; changing to the newer fitted base does not give unprofiled model acceptance an inherited safety guarantee. This rule was formulated after the data had been inspected; it is **post hoc headroom analysis**, not a preregistered policy test.

At the inherited **2 ms** budget, it reproduces uniform profiling's entire admitted set while profiling **10 of 19 configurations**, using **39.49% of the recorded profiling wall service time**. Among the ten retrospectively quality-screen-qualified configurations, both policies have five admissions, zero confident false admissions, and one confident conservative rejection. The selective policy's corresponding all-configuration counts are five admissions, zero confident false admissions, and four confident conservative rejections. This shows possible measurement-cost headroom; it does not establish controlled risk.

The complete inherited sweep is below; all counts cover nineteen configurations. Details, including quality-screened counts, are in [cross_domain_replay.json](cross_domain_replay.json).

| Budget ms | Configurations profiled | Profiling wall service / uniform | Selective / uniform admissions | Same admitted set? |
|---:|---:|---:|---:|---|
| 0.25 | 0 | 0% | 0 / 0 | Yes |
| 0.5 | 0 | 0% | 0 / 0 | Yes |
| 1 | 0 | 0% | 1 / 1 | Yes |
| 2 | 10 | 39.49% | 5 / 5 | Yes |
| 4 | 7 | 45.34% | 17 / 16 | No |
| 5 | 0 | 0% | 19 / 17 | No |
| 8 | 0 | 0% | 19 / 17 | No |
| 16 | 0 | 0% | 19 / 18 | No |
| 32 | 0 | 0% | 19 / 18 | No |

At 4 ms all ten qualified candidates are admitted. At 5 ms and above the gate admits every configuration, including poor-quality ones. Thus this is not an accuracy policy, and 2 ms must not become a retrospectively invented deployment requirement.

**Consumer and controls.** The consumer is an offline planner deciding whether a task meets a specified per-call service budget with a 5% miss tolerance. This is a CPU service primitive, not a full FTQC safety condition. Compare against the frozen nonlinear base with and without padding, graph16, uniform profiling, and a conservative reject policy. Report false admissions, feasible rejections, unresolved truth, useful admissions, profiling calls, and total preparation cost together. A reject-all policy cannot win merely by producing no false admissions.

**Units and uncertainty.** There are nineteen configurations but only seven bridge parent groups, four of them previously inspected calibration parents. The evaluations' saved multiplicity-adjusted binomial miss intervals determine confident errors; crossing 5% remains unresolved. Parent-cluster resampling and leave-one-context summaries can describe sensitivity, but cannot make seven related groups or three processes representative of a deployment population. Quality screening is retrospective and stays separate from the timing policy. None of these parents becomes fresh again because a new imported framework is used.

**Overhead and stopping.** This replay costs seconds and no shots or fits. Its 39.49% figure excludes feature extraction, construction, decoder initialization, warmup, inference, and training amortization; it is not a 60.51% system speedup. The next bounded analysis is to finish that cost ledger and uncertainty/sensitivity audit for this same rule, without searching more gates. Stop this particular transfer hypothesis if the apparent gain disappears after charging costs, relies entirely on unresolved truth or one parent, or simply buys fewer admissions. If headroom survives, freeze this hypothesis and design a small independent admission study around its actual consumer. Do not automatically run the previous placement-focused sixteen-parent design.

The mean/throughput signal remains worth recording, but this first test uses bounded deadline-exceedance indicators because their uncertainty is more tractable than an unbounded heavy-tailed mean. A mean-capacity extension needs its own workload horizon and uncertainty treatment; clipping or robustifying means must not silently change the claimed target.

## What could justify a paper

A paper could be justified by an established method solving a consequential QEC problem through a nontrivial adaptation, a convincing comparison with cheap controls, and a reproducible account of success and failure on independent programs. New algorithmic machinery is optional; new knowledge and defensible evidence are necessary. A strong empirical boundary result can also matter if it answers a live design question.

Replacing ridge with a fashionable regressor, borrowing a name, or reporting another favorable score on these development parents would not meet that standard. Conversely, using a simple nonlinear base inside a successful selective-profiling system would be a positive transfer result, not a failure to invent a sophisticated model. My revised recommendation is to pursue that sharply specified possibility through the cheap replay/cost audit first, while keeping the original negative results intact. There is no novelty or publication guarantee.
