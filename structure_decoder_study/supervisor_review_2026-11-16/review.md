# AI supervisor review of the decoder-cost project

Review date: **16 November 2026, Asia/Tokyo**.

**Reviewer status:** I am a separate AI reviewer asked to act as a skeptical FTQC systems/QEC research supervisor. I am not a human professor, an external peer reviewer, or an independent experimental laboratory. This is research advice, not publication certification. I reviewed saved artifacts and primary literature; I ran no new decoder measurements, changed no frozen artifact, and used no further subagents.

## Executive verdict

**Retire the current added-topology p95/compiler headline. Do not launch its large reserved-parent campaign.** Its necessary entry condition has failed: with the tested information and model classes, an inexpensive nonlinear base model predicts p95 better, and graph additions have not improved the quality-screened scheduling choices. The negative conclusion is specific to these features, workloads, models, and operational mode. It does not establish that topology is generally irrelevant.

**The project is worth a small, explicitly conditional continuation, not an open-ended rescue.** There is a credible measurement artifact, a reproducible failure of one frozen noise-transfer/admission model, and an exploratory mean-latency signal. There is not yet a demonstrated novel, useful compiler method. Stopping now, preserving the artifact as a technical report, would be a scientifically reasonable outcome.

**The immediate next step should be a two-working-day novelty and use-case veto, with zero new shots.** The primary literature already covers decoder-aware scheduling, stochastic service times, shared decoder capacity, noise-dependent LSD work, and long timing tails. A paper cannot be justified merely by combining those phrases with a regression. Require a specific residual claim and a real consumer of its predictions before collecting more data. If that veto passes, I recommend exactly one prospective fresh-parent mean-decision test, specified below. Failure ends positive cost-model development for this corpus; it does not trigger another target, feature, or benchmark pivot.

The current preference for a mean/throughput pivot is **scientifically permissible as hypothesis generation, but not yet justified as the preferred publication story**. It becomes outcome-driven drift if the project promotes the favorable mean score while suppressing the p95 failure, the stronger base controls, uncertainty, or trivial decision baselines.

## What I checked independently

I read the original paper plan; the initial, stress, learning-curve, and validation protocols/findings; both earlier assessments; the 15 November status; the validation model/bridge/audit JSON; and the implementation of `models.py`, `common.py`, `analyze_bridge.py`, `bridge.py`, and `prepare.py`. I also examined parent composition and frozen predictions rather than taking the status recommendation as a premise.

My read-only recomputation from the bridge's raw NPZ arrays reproduced all **59,904 evaluation decoder-call** mean-wall, p95-wall, mean-CPU, and logical-failure summaries exactly (maximum numerical difference zero). This checks the summaries, not the physical model. The saved model audit reports 186 checked outer records and 18 separate sklearn reproductions; its largest log-prediction discrepancy is approximately 3.8e-12. Inspection of the fitting code agrees with its principal claims: training-only standardization, centered RBF training/evaluation kernels, target centering, group-held-out inner selection, and outer-parent exclusion. I found no obvious fatal arithmetic or split implementation defect in these parts.

The coordinating assistant separately reverified the inventories in [evidence_integrity.json](evidence_integrity.json): the original 905 entries, 13 November 1,458 entries, 15 November 1,964 entries, and validation-gate 437 entries match. This is another internal consistency check, not outside reproduction. The existing replay/parity audits are substantial evidence of artifact integrity, but neither hashes nor agreement between two code paths proves all scientific assumptions.

Additional calculations from existing outputs are reported below. They are explicitly **post hoc review diagnostics**, not new confirmatory experiments. The placement baseline is also recorded in [decision_baseline_check.json](decision_baseline_check.json).

## Supported conclusions and their boundaries

| Claim | Assessment |
|---|---|
| The pinned public pipeline produces nontrivial circuit-derived tasks, and recorded corrections/summaries are internally consistent. | Well supported for the stated detector sector and checks. Computational-basis checks, Pauli conjugation checks, circuit/DEM consistency, and syndrome parity checks cover different obligations; none alone establishes full fault tolerance. |
| Volume/counts can miss substantial service-time variation. | Supported on this corpus. The original sparsity/activity model is much stronger than volume. The reported maximum spreads compare different logical programs and do not themselves establish added topology information or same-program speedup. |
| The selected graph summaries improve p95 beyond an adequate base model. | Not supported. The stronger nonlinear comparison currently points the other way. This is an unsuccessful tested feature/model proposal, not a theorem that graph information is unnecessary. |
| A frozen single-noise model plus historical padding can falsely admit new noise conditions, including one condition inside all six raw marginal ranges. | Supported as selected, repeatedly measured counterexamples under the stated stable-context/IID reference model. It is not a population failure-rate estimate. H/L are unchanged while probabilities change, so these cases do not identify missing static topology as the cause. |
| Extra graph information improves mean prediction in some settings. | A credible exploratory signal, with important heterogeneity and label uncertainty. It has not yet changed a demonstrated useful decision. |
| The project improves a compiler's useful FTQC choices. | Unproven. Current placements have equal extraction rounds and instruction/TICK counts; quality eligibility is retrospective; no quantum-duration, queue, memory, or system reaction-time benefit has been shown. |
| BP100 or ordinary component decomposition changes the research conclusion. | BP100 does not provide a cheap obvious repair on this bridge; decomposition does provide an important established baseline on the memory reference. Neither validates the graph predictor or establishes a globally best decoder configuration. |

The strongest stress counterexamples have approximately 7–12% logical-Z failure. They remain valid cost-model counterexamples, but should not be the centerpiece of a claim about useful FTQC schedule admission. A simple regression trained at one physical noise rate failing at another is also a weak novelty claim without a distinctive decision or methodological result.

### The strongest present comparison

These are `exp(mean absolute log error)`, balanced over the declared held-out groups. They are prediction error factors, **not runtime speedups, percentages of correct predictions, uncertainty intervals, or admission guarantees**.

| Evaluation domain | Target | RBF base6 | RBF density8 | RBF graph16 |
|---|---|---:|---:|---:|
| Original seven groups | p95 | 1.02942 | 1.03077 | 1.07649 |
| New parents, fixed noise | p95 | 1.04165 | 1.03970 | 1.05093 |
| New parents, mixed noise | p95 | 1.04518 | 1.04216 | 1.05755 |
| New parents, fixed noise | Mean | 1.11793 | 1.12021 | 1.11758 |
| New parents, mixed noise | Mean | 1.11339 | 1.11476 | 1.09400 |
| Seven-group calibration bridge | p95 | 1.15565 | 1.09400 | 1.13334 |
| Seven-group calibration bridge | Mean | 1.07351 | 1.09155 | 1.05270 |

The graph-versus-density p95 ranking is broad rather than a single outlier: graph16 is worse in all seven original groups, eight of twelve fixed-noise new parents, and ten of twelve mixed-noise new parents. On the bridge it is worse in all four new parents. These counts are descriptive; overlapping trained models and related parent generators are not independent trials.

The mean result should be preserved just as carefully. Graph16 beats density8 in eight of twelve mixed-noise parents, but only six of twelve fixed-noise parents. Its fixed-noise advantage over base6 is effectively a tie at this precision. The bridge's all-new-parent mean factors are 1.08400 / 1.08366 / 1.07192 for base6 / density8 / graph16. A post hoc restriction to its eight low-noise new configurations retains a graph signal: 1.10418 / 1.10628 / 1.08172. Thus poor-quality high-noise cases alone do not explain every favorable mean comparison. These restrictions are diagnostics, with no fresh-test or significance claim.

### Prediction gains have not become mean decision gains

In **all eight current bridge parent-by-noise pairs**, burst has the lower point mean and lower point p95. In the four pairs with two quality-screened alternatives, every frozen nonlinear mean predictor chooses burst in all four. The linear graph predictor misses one; the other linear mean predictors choose all four. Consequently, the current nonlinear graph mean score has not improved mean selection over either nonlinear base or a zero-model **always choose midpoint burst** heuristic.

This exposes a weak decision benchmark. It does not prove burst dominance outside it: the earlier discovery corpus includes a small p95 reversal for q4_P05 at d5/w10/p=0.001 (spread approximately 1.759 ms, burst 1.792 ms), whose uncertainty must be respected. Nor does choosing burst establish that it meets an accuracy constraint or a service budget. Ranking and admission are different questions.

For p95, nonlinear base6 and density8 match all four measured point oracles, versus three for graph16. One of the four oracle orders is unresolved by the declared intervals. Even the conspicuous q4_P00 point contrast is not interval-resolved: spread p95 is about 1.673 ms with interval 0.899–1.712 ms; burst is about 0.416 ms with interval 0.328–1.384 ms. Four calibration choices are not a deployment success rate.

The **2 ms admission tradeoff must remain visible**. Among ten screen-qualified configurations, raw nonlinear density8 has one confident false admission, no confident conservative rejections, and seven admissions; raw graph16 has zero, one, and five. Historical padding removes the observed false admission while rejecting many feasible cases. This is neither evidence that graph is uniformly better nor grounds to erase its favorable risk count. It is an unmatched conservatism tradeoff. At 5 ms, both raw nonlinear policies admit all ten without a confident false admission. The budgets are illustrative, and unresolved truth cases are not successes.

## Why a throughput pivot is not yet earned

### Adaptive selection and effective sample size

Nested group validation appropriately protects each declared hyperparameter choice. It does not protect a research narrative selected through repeated inspection of those outer results. The stress exploration, learning curves, nonlinear baselines, target comparisons, and new proposed mean headline are all part of development. The untouched parent reserve is valuable precisely because it has not yet been used to select a story.

The corpus has many shots but few distinct programs. The 125 complete labels comprise 78 original and 47 discovery configurations. Their parent sizes range from **27** configurations for old single/repeated to **one each** for the four six-block parents; the first four new four-block parents have eight or nine. Equal-group validation is sensible but does not make this a balanced corpus. The fitting code minimizes a row-level ridge/kernel objective: it does not weight every parent equally during training. That is a disclosed modeling/design limitation, not evidence of an implementation error. Group-balanced selection/reporting and row-weighted fitting answer slightly different population questions.

Adding programs changed noise, block count, temporal extent, cohort, target precision, and regularization as well as sample count. The learning curves therefore cannot uniquely diagnose underfitting, overfitting, or an information deficit. Excluding the resource-censored discovery case is appropriate for complete-label analyses, but it restricts those conclusions to completed tasks; it supplies no evidence about the excluded expensive regime.

### Mean and quantile labels have different weaknesses

The old labels have 6,000 shots, discovery labels usually 768, and bridge labels 1,536. Earlier saved analyses put median ordinary p95 interval widths at about 1.26% versus 8.95% for old versus discovery labels. A label interval wider than an aggregate model difference does not disprove the difference; it does prevent treating tiny point gains as settled.

Means are especially demanding here. Selected extreme replay supports real decoder CPU work rather than ordinary descheduling. It does not estimate its incidence. In my bridge recomputation, the slowest approximately 1% of BP30 calls account for **30.24%** of wall service in low-noise q4_P03 spread and **22.45%** in the old cycle reference. The historical bridge mean ratios span approximately 0.909–1.381 even though there is no large uniform p95 multiplier. Fresh processes and interleaved blocks improve the design, but three processes on one heterogeneous laptop do not establish a deployment distribution or independent population-mean precision.

A mean prediction gain is not automatically a throughput gain. For a stable serial service worker, reciprocal mean service is a useful capacity quantity under the declared workload mixture. Finite jobs, shared pools, queue waits, burst arrivals, initialization, and feedback dependencies require additional accounting. In this project a finite CPU-service workload is a defensible first target; a full FTQC throughput claim is not.

### What “structure” and symmetry mean

Graph16 adds eight selected summaries, not a complete representation of topology. Three component summaries are constant for all connected discovery tasks. The other inputs largely summarize local degrees/arity. These features may proxy placement, extent, or a program family. Better prediction would not by itself show a causal graph mechanism or information-theoretic necessity.

The two density ratios are functions of base6. Their improvement in a linear model demonstrates a useful representation change without new information. In the RBF model they also change the geometry and relative weighting of the inputs. Equal model families and tuning budgets make the current comparison a fair practical control; they do not prove universal base sufficiency or isolate a unique graph-information contribution.

Removing the sampled, row-sensitive two-step feature was necessary. The 57 descriptor permutation checks establish the implemented stable summaries' invariance for those transformations. They do **not** establish decoder timing invariance. BP/LSD implementation order and tie-breaking may respond to column/row numbering. A proper runtime symmetry control must transform H, L, priors, syndromes, and correction interpretation together. Parent ideal-map canonicalization under block permutations is good protection against a class of equivalences; it is not a quotient of every noisy graph, detector-basis, schedule, or decoder-ordering equivalence.

Ordinary decomposition must precede any topology novelty claim. The bridge's memory result includes gather/merge work and remains useful evidence that this standard choice matters. A predictor should not receive credit for rediscovering that independent problems can be separated.

### Decoder, accuracy, and operational scope

BP30 is a legitimate pinned research setting. BP100 raises bridge p95 in all nineteen configurations, with median ratio about 2.964, and pooled paired logical outcomes improve 26 times and worsen 25 times. That rejects one simple repair hypothesis; it does not establish noninferiority, decoder optimality, or a competitive cost/accuracy frontier. Ordinary decomposition improves the memory reference without observed logical-outcome changes in the tested stream. One decoder and one CPU can support a clearly scoped empirical paper, provided the question is valuable within that scope.

The all-zero, logical-Z-sector, full-block experiment is also a legitimate object. It can support statements about **this software decoder's service costs on these projected tasks**. It cannot support full-Pauli error rates, sliding-window commits, real-time response, arbitrary-state accuracy, or a physical FTQC resource advantage. Later conjugation checks strengthen the legal same-CNOT-action comparison but do not create missing X-sector noise/accuracy evidence.

The one-sided 1% whole-task logical-Z screen is a useful pilot exclusion rule, not an FTQC accuracy requirement. Giving all models the same retrospective eligibility set makes their conditional ranking comparison interpretable; it does not give a compiler a deployable eligibility oracle. A future decision must be committed before evaluation and then assessed for accuracy, rather than silently discarding poor-quality selected cases.

### Overhead changes the useful competition

The optimized median base-density extraction is about 0.0391 ms and full stable extraction about 0.5786 ms. Median recorded service for the 192-shot profiling baseline is about 127.18 ms per configuration. This leaves room for cheaper model-based selection, but feature extraction alone is not the total cost: circuit lowering, DEM generation, conversion, decoder setup, inference, cache reuse, and warmup matter. A fixed placement heuristic may need to build only its selected candidate, while model or profiling selectors may need artifacts for every candidate. Charge what each policy actually needs.

Profiling must target the same objective. A p95 profiler is not the appropriate sole baseline for a mean selector. Conversely, a 192-shot sample mean can miss rare expensive work; that is an empirical tradeoff to test, not an argument for excluding profiling. At a sufficiently long future run, its small setup premium may be negligible.

## Primary literature and novelty threats

I checked the following primary sources directly during this review. This is a focused novelty audit, **not an exhaustive absence-of-prior-art claim**. The established prior facts are in the middle column; the implications in the last column are my assessment.

| Closest primary work | Established prior contribution relevant here | Consequence for this project |
|---|---|---|
| [PACE, arXiv:2608.11719v1, §§5.1, 7.6](https://arxiv.org/html/2608.11719v1) | Decoder-aware transversal-CNOT scheduling, feasibility models, and DEM/task preparation techniques are already present. Its CPU case study extrapolates measured single-patch volume fits to multi-patch tasks and explicitly excludes additional density/topology dependence. | This provides a precise modeling boundary to examine, not an unoccupied scheduling problem. Our volume proxy is not a numerical reproduction or refutation of its scheduler/case study. |
| [Triage, arXiv:2605.04459v1, §§III, V-D](https://arxiv.org/html/2605.04459v1) | Finite-resource window scheduling uses slice degree in its cost heuristics and a stochastic latency model calibrated from per-shot PyMatching measurements. | Neither graph-dependent cost language nor adding latency jitter is novel by itself. Detector-hypergraph summary prediction differs from its slice-constraint degree, but needs demonstrated incremental utility. |
| [LSD, arXiv:2406.18655v2, discussion and Appendix C.4](https://arxiv.org/html/2406.18655v2) | Reliability-guided clusters and on-the-fly factorization are the algorithmic basis. Appendix C.4 includes both Fig. 8 timings conditioned on BP non-convergence and Fig. 9 unconditional BP+LSD/OSD call timings across multiple physical noise rates, including means and long tails. The paper also motivates approximately thirty BP iterations for its studied codes. | Clusters, noise-sensitive runtime, BP30 motivation, long tails, and unconditional timing are already established. Any possible distinction here must lie in controlled held-out schedule-level cost prediction and consequential decisions, not unconditional timing itself. |
| [A Case for Elastic QEC Decoders, arXiv:2406.17995v4, §§5, 7.4](https://arxiv.org/pdf/2406.17995v4) | Capacity planning and sharing decoders are established. Its treatment includes measured PyMatching latency distributions and a lognormal tail abstraction for resource simulations. | Generic capacity/throughput or tail-aware resource provisioning is occupied. A new measured predictor must change a concrete resource tradeoff beyond that abstraction. The current PDF title differs from older indexing titles. |
| [BP+OTF / DEM sparsification](https://arxiv.org/abs/2409.01440) | Runtime-oriented graph sparsification and an almost-linear decoder design already connect graph representation, circuit-level decoding, and cost. | Sparsity is a mandatory control, and representation/decomposition can be an alternative to learning a richer predictor. This project is not a new decoder. |
| [Impacts of Decoder Latency on a Utility-Scale Quantum Computer Architecture](https://arxiv.org/html/2511.10633) | Reaction-time modeling joins decoding, communication, architectural choices, and logical-error/resource effects. | Per-call CPU latency is only one component of the decision problem. An application-level claim needs an explicit join to the rest of the pipeline. |
| [Platform-aware compilation, arXiv:2609.08908](https://arxiv.org/html/2609.08908) | Platform-dependent compilation/resource estimates include classical processing through reaction depth and stalling budgets. | Merely adding classical costs to quantum resource estimation is insufficient differentiation. A validated schedule-specific stochastic cost primitive could be narrower and distinct. |
| [CUDA-Q Logical, arXiv:2609.13388](https://arxiv.org/html/2609.13388) | Schedule-derived resource analysis, detector/observable semantics, and decoder/control contracts are explicit compiler artifacts; functional in-shot execution is distinguished from hardware timing claims. | Provenance-preserving compiler/decoder integration alone is no longer a sufficient systems headline. It reinforces the value of the current scope qualifications. |
| [Predictive Window Decoding / SWIPER, arXiv:2412.05115](https://arxiv.org/html/2412.05115) | Prediction is used to speculate across window boundaries and reduce reaction latency. | The prediction target is different from compile-time service cost, but “predictive decoding for faster programs” is too broad a novelty claim. |
| [TMCBS associated study](https://www.nature.com/articles/s41467-026-75693-3) | Circuit-level distributed transversal primitives and compiler/architecture tradeoffs are already evaluated with the public workload library. | Using this generator is reproducibility infrastructure, not a contribution. Its published distributed-operation results do not transfer automatically to this local, projected, pinned-decoder timing study. |

I did not find a directly identical, convincingly validated static-summary mean selector in this focused check. That observation is not sufficient evidence of novelty. A final claim audit must inspect relevant full texts and cited/citing work at the level of **inputs, prediction target, measurement mode, grouping, and decisions**, rather than comparing titles.

## Ranked publication paths

I rank only two paths as worth considering. Neither is currently submission-ready, and neither comes with a publication promise.

### 1. A scoped empirical benchmark and modeling-limits paper

**Defensible prospective claim:** “For a precisely specified family of circuit-derived logical-Z full-block CPU tasks, we provide an auditable benchmark showing which cost assumptions survive fresh-parent tests, where calibration/representation changes matter, and whether their differences affect candidate decisions.” Retain the failed structural p95 hypothesis and any mean result together. The contribution would be a reusable experimental result and its implications, not a claim to have discovered variable decoder cost.

**Closest work and differentiator:** LSD supplies runtime mechanisms and unconditional timing distributions; PACE supplies the task-cost modeling boundary; Triage and elastic decoders supply stochastic/resource context. A possible differentiator is controlled held-out schedule-level prediction tied to equivalent candidate choices, strong nonlinear controls, label/context uncertainty, and actual decision utility after selection overhead. Unconditional physical-shot timing alone is not a novelty gap. Whether the narrower package is new and useful enough remains open.

**Decisive minimum evidence:** the single locked test below, a compact runnable artifact with documented task/equivalence/split semantics, and reproduction by another researcher or independently administered machine. A negative fresh result may make a useful benchmark lesson; it does not automatically make a paper.

**Go:** the novelty audit identifies a specific consequential modeling question for which this artifact supplies an answer absent from the close work, and the prospective result supports a clear, limited conclusion. **No-go:** the proposed abstract reduces to “volume is insufficient,” “single-noise regression does not transfer,” “LSD has tails,” or “components help.” In that case, release a technical report/artifact and stop publication-driven expansion.

**Main risks:** limited application coverage, a one-sector generator artifact, no broad hardware claim, little new algorithmic insight, and a benchmark that few researchers need. This is the most evidence-aligned path, not necessarily the most prestigious or easiest to publish.

### 2. A new mean-service decision method, conditional on a stringent test

**Defensible prospective claim, only if earned:** “With fixed candidate generation and a fixed software/CPU service mode, stable graph summaries reduce total mean-service selection cost on unseen parent programs beyond nonlinear base, fixed-placement, and direct-profiling policies, while passing the declared logical-Z quality audit.” Describe its first application as a restricted CPU decoding workload. Do not infer accelerated online FTQC.

**Closest work and differentiator:** the close schedulers/resource models already motivate mean service and sharing. The distinct proposed contribution would be cheap *pre-execution* information that changes fresh decisions after full costs, rather than the existence of a more accurate regression score.

**Decisive minimum experiment:** exactly the test below, without adapting its features, model grid, candidate set, or target from fresh outcomes.

**Go:** a consequential, uncertainty-resolved net improvement against all strong controls, in an accuracy-qualified regime, with no domination by one exceptional parent or timing context. **No-go:** the graph model improves MAE but chooses the same schedules; a fixed heuristic matches it; profiling matches or beats its total cost; its advantage is unstable or depends on excluding selected inaccurate cases. Stop this positive-method path after that outcome.

**Main risks:** the present decision signal is absent; mean labels are expensive; the apparent gain is small and model-dependent; a strong base/profiling policy may suffice; fully charged candidate preparation may dominate. This is a legitimate new hypothesis, not the successful continuation of the old p95 claim.

I would not currently fund a third “better calibration/abstention/profiling” publication path merely to avoid stopping. Such policies are useful controls. A new contribution would require a distinctive method and a meaningful matched-risk/resource problem beyond generic recalibration. The current 2 ms tradeoff alone does not supply that problem or result.

## One recommended next study, with an initial veto

### Immediate action: two days, no decoder measurements

Write one prospective abstract and a one-page claim/prior-work table for the chosen scoped path. Identify who uses its output, the actual decoding unit, what action can change, the workload horizon, and why a fixed placement or a small profiler is inadequate. The primary-source audit above is a starting point; inspect the closest sections and their citations specifically for the claimed distinction.

**Stop here** if no credible distinction and consumer can be stated in two working days. Do not spend the untouched test reserve to search for one. A human QEC/systems researcher evaluating this claim sheet would be valuable, but this report does not represent their endorsement and no messages to others were sent.

### If that veto passes: one prospective mean-decision falsification trial

This is the only new measurement study I recommend. It is deliberately bounded and can kill the mean pivot. The following is a proposed design to freeze before opening fresh parents, not a claim that it has been performed.

**Question and scope.** Can graph16 change an economically useful candidate choice for a serial, warm CPU decoder service workload? Use the pinned BP30/LSD0 stack, fixed detector basis, full-block logical-Z tasks, and one defined CPU mode. Optimize mean wall service/worker occupancy; record CPU time as a corroborating diagnostic. Keep p95 as a mandatory secondary legacy outcome. Do not introduce an online queue, a new decoder, memory admission, or a quantum-duration claim into this trial.

Use a primary horizon of **100,000 future decoding calls** per selected candidate, representing an offline decoding campaign from its declared input stream. The two-day use-case check must justify that horizon; any change happens before the freeze. The economic score includes policy-required circuit/DEM/matrix preparation, feature/inference or profiling, initialization/warmup, and future service. Report shared sampling/checking work separately and include it in any broader end-to-end claim. Do not bill every policy for artifacts it could avoid: an always-burst policy may construct only its chosen candidate. Training is reported separately with an explicit amortization assumption.

**Held-out units and candidates.** Reserve **sixteen entirely new parent programs**, eight four-block/six-CNOT and eight six-block/eight-CNOT, at d=5, ten rounds, p=0.0003. Use seeded input-only generation and ideal-map canonicalization under simultaneous block permutations; exclude all inspected ideal-map classes. Do not inspect fresh timings while selecting parents. Hold every placement, ordering control, and noise realization of each parent together. This is generalization within this specified generator family, not unseen-application or scale transfer.

For every parent enumerate the same four legal placements: early burst, midpoint burst, late burst, and spread, keeping the exact CNOT order, rounds, and gate set. This gives **64 candidate configurations**. Freeze event-round formulas and tie-breaks before measurement. Check noiseless action and detector/DEM semantics. Fix decomposition/basis conventions in advance and target connected tasks after ordinary decomposition; any input-only scope exclusions and the deterministic replacement rule must be logged before any timing. Do not select only cases where models disagree or a heuristic loses. Such a disagreement subset may be reported separately after the representative test, with no population claim.

**Frozen controls.** Using only the current development data, freeze the existing model recipes and all parameters before fresh evaluation. The principal comparison is RBF graph16 versus **both RBF base6 and density8**, the fixed midpoint-burst heuristic, and a direct mean profiler. Keep the linear comparisons as descriptive continuity evidence; do not expand model classes or feature sets. Use the profiler's disjoint **192 physical shots per candidate** and its empirical *mean*, not its p95, to select a candidate. Selection ties have a fixed rule. Freeze every policy's choice before unsealing evaluation outcomes. No policy receives the evaluation-derived quality eligibility oracle.

**Measurement budget and precision.** Three fresh processes, 4,096 evaluation shots per candidate/process, in randomized interleaved 64-shot blocks: **786,432 evaluation shots**. Add 12,288 disjoint profiling shots and declared warmups. On four parents chosen by ID before outcomes, add two complete row/column relabelings using the same underlying physical streams, 256 evaluation shots per candidate/process/relabeling; this adds 24,576 decoder calls. Correctly transform H/L/priors/syndromes and interpret corrections back in the original frame. These ordering controls are not extra independent programs.

The overall plan remains below **850,000 decoder calls including evaluation, profiling, relabeling controls, and warmups**, one benchmark worker, and **eight measured service CPU hours**. The fixed shot budget is a maximum, not a mandate to use the CPU cap. Check resource limits after complete blocks, retain all completed observations, mark censoring, and stop the trial if the global cap is reached. A native call is not given a fictional hard timeout. A censored/unresolved trial does not pass by omitting its expensive cases. Do not top up until a favorable mean ordering appears.

**Accuracy and legal decisions.** Audit the selected candidates against a prespecified one-sided **1% whole-task logical-Z** ceiling using simultaneous upper intervals across the 64 candidates. This ceiling is an inherited pilot relevance screen, explicitly not a deployable FTQC target or a full-Pauli certificate. Report selected logical outcomes and intervals for every policy. An unqualified or unresolved selected candidate is an unsuccessful investment result, not a row to discard. Report the accuracy/cost frontier as a diagnostic, without choosing a more convenient threshold afterward. A broader FTQC paper would subsequently require the appropriate two-sector/window/feedback problem; that is a new stage justified only by a successful restricted result.

**Primary metric and uncertainty.** Compute each policy's fully charged total cost at the fixed 100,000-call horizon, averaged over the sixteen equally weighted parent jobs. Report the graph/control cost ratios, parent-by-parent regret against the finite measured candidate oracle, how often decisions differ, and the always-burst/profiler results. Preserve raw mean/p95 prediction errors as secondary metrics. Savings in a prediction error factor are never substituted for saved runtime.

Use paired parent-level resampling, with timing blocks/contexts nested within parent, to propagate workload and service-label uncertainty; keep comparisons paired across policies. For the four primary controls, prespecify simultaneous intervals, for example Bonferroni-adjusted hierarchical bootstrap intervals, and publish their assumptions. These are approximate intervals under the sampled parent/context model, not distribution-free guarantees for an unknown heavy-tailed mean. Include leave-one-context and largest-block sensitivity, the contribution of the largest 1%, and uncertainty in the finite oracle. Never treat hundreds of thousands of shots, overlapping model fits, or relabelings as independent parent replications.

**Investment go/no-go.** I propose a **5% fully charged cost reduction against each strong control**, with the simultaneous upper interval for graph/control below 0.95, as a lab investment threshold. It is not a universal publication standard; the initial use-case sheet should establish why it matters. Require all graph-selected tasks to pass the declared accuracy audit, consistent benefit direction in all three contexts, benefit on at least twelve of sixteen parents, and no single parent supplying more than half the aggregate savings. Report all controls regardless of outcome. If mean uncertainty remains too large, a relabeling effect is comparable to the purported benefit, or the criteria fail, stop the positive mean-selector path as unsupported or inconclusive at this budget. Do not respond with another round of features or more training on those now-inspected parents.

This test can change the research decision because it asks whether the only remaining favorable predictive signal survives the cheapest useful alternatives and changes fresh actions. It also distinguishes “a better mean estimator” from “a better selection method.” A negative result would close the original research direction cleanly. It would support a scoped negative/benchmark report only if the separate novelty/usefulness requirement for Path 1 is met.

## Practical publication plan and readiness

1. **Now: close the original claim.** Keep the frozen p95 results and counterexamples intact. Use a scope-accurate working description such as “Cost-model validation for a circuit-derived CPU decoding benchmark.” Write the two-day claim/use-case veto. If it fails, archive a readable technical report and artifact; stop.
2. **Only after the veto: freeze and run the single trial.** Lock the program generator, test IDs, candidate enumeration, models, quality/utility criteria, uncertainty method, and analysis code. Run a synthetic dry-run of the analysis without actual test outcomes. Record any unavoidable amendment as an amendment. A dated local protocol is useful provenance; external preregistration is not a prerequisite for valid research, but neither is local hashing an external timestamp.
3. **After one readout: choose the paper or closeout, without changing its hypothesis.** A positive result could justify a narrowly framed QEC systems/performance paper. A robust null result could justify a benchmark/methodology paper if it answers a consequential question. If neither is true, release the report and stop. Do not turn the failed trial into a third favorable target.
4. **Before submission: obtain outside scientific scrutiny and reproduction.** Have a QEC researcher assess the detector/observable and accuracy scope, and have another researcher reproduce representative artifact outputs. Package the immutable data, split IDs, model payloads, raw service traces, logical outcomes, uncertainty code, and short runnable examples. State AI involvement and human author responsibility accurately under the eventual venue's policy.

**Venue categories:** today the work fits an internal technical report or public research artifact. A quantum-computing architecture/performance workshop or a reproducibility/benchmark track may be a realistic first review setting after the scoped claim and artifact are coherent. A specialist QEC/quantum-computing journal research article requires a distinct scientific result and stronger generalization/usefulness evidence. A full architecture/compiler/systems conference paper would require a considerably more consequential method and system-level evaluation than the current four calibration choices. The present evidence is not ready for that category.

I recommend selecting no named venue or deadline yet. Readiness should determine that choice; a deadline should not determine which favorable exploratory number becomes the headline. No acceptance probabilities are claimed.

## Explicit stop rules

- **Stop the current structural p95/compiler proposal now.** Reopening it requires a new reason and independently held-out evidence, not reinterpretation of the old learning curves.
- **Stop all new measurement investment** if the two-day novelty/use-case veto cannot identify a specific valuable claim beyond the primary work above.
- **Stop the positive mean method** if the one prospective trial fails its utility, accuracy, uncertainty, heuristic/profiling, or representation-robustness criteria. An inconclusive result at the fixed budget is not a success.
- **Stop paper salvage** if the remaining contribution is only known runtime variation, generic distribution shift, standard decomposition, or a reproducible but practically unused dataset. Preserve and release it as appropriate without manufacturing a larger claim.

The strongest feature of this project is its willingness to retain adverse evidence and strengthen controls. The next research decision should preserve that discipline by allowing the answer to be “this hypothesis did not justify a paper,” rather than requiring a publication to be rescued.
