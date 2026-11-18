# Supervisor assessment: one-task decoder research

18 November 2026. Independent AI advisory review of `task_specific_expert.md`, saved project reports/code and relevant primary literature. This is not human expert validation. No decoder calls, candidate computations, fitting, new sampling or manuscript work was performed. Existing frozen artifacts and manifests were not edited.

**GO for one bounded mechanism diagnosis on the existing task. HOLD a method choice and a publication claim.** I agree with the expert's focused proposal, with the interpretation limits below.

## Correction to the earlier scope requirement

A paper confined to one precisely specified decoding task does not have to demonstrate cross-family transfer or compiler benefit. Fresh independent observations from that same task can test the claim it actually makes. My earlier untouched-program requirement was too broad if applied to every decoder paper; retain it only when the claim includes transfer to other programs or families.

Finite-code, mechanism-guided decoder research is an established category. The peer-reviewed trapping-set study identifies harmful configurations and uses that understanding to improve finite-length decoders. It supports this scientific workflow, not the novelty of any mechanism we might identify or an acceptance prediction. [Trapping Sets of Quantum LDPC Codes, Quantum 5, 562 (2021)](https://quantum-journal.org/papers/q-2021-10-14-562/).

Narrow scope reduces the generalization burden; it does not remove the originality or useful-effect burden. Merely improving an intentionally weak baseline, applying known 1FV search, or repairing two inspected syndromes would remain insufficient evidence for the intended contribution.

## The appropriate task and its present evidence

Keep the accessible pinned BB144, 24-round, p=0.007, Z-check-only source circuit and noise model. Define a shot failure as any incorrect one of the twelve observed logical-Z outcomes over that window. This is a legitimate stochastic task distribution, not a claim about both-check quantum memory, logical gates, hardware or compiler decisions.

The 512 natural observations are development data. The twelve original failures are all failures observed in that finite development cohort; the two residual witnesses are not the task distribution. The selected 24 cases can support exact within-list diagnosis, but cannot estimate population rescue, regression or mechanism prevalence. The other 488 original successes have not undergone the inspected 1FV search, so no 2/512 improved error rate follows.

The closest task-matched prior already studies BB144/24-round/p=0.007, decoder disagreement and 1FV rescue. It must be a central comparison, not peripheral background. Our ten rescues establish recoverability under a known method rather than a new contribution. [Adaptive decoding through decoder disagreement](https://arxiv.org/html/2609.37629v1).

## One next task, before choosing a method

Approve a frozen **offline coverage-and-selection audit of all 24 already saved candidate sets**: baseline plus the 10,446 saved 1FV candidates per case. Use the saved algebra and original evaluation observables; do not call a decoder, enlarge the list, change scoring or attempt a repair.

Report, for each case, the covered logical signatures, minimum declared score per represented class, whether the observed correct class is present, and its margin against the best competing class when defined. Include the baseline and preserve source candidate ordering, strict-improvement policy and deterministic ties. Numerical sensitivity should be reported separately rather than silently change the source winner. Retain all twelve controls as well as all twelve failures.

The decisive question for 131/228 is whether the correct class is absent from this particular list or present but loses its score comparison. This diagnostic is feasible from saved `rf`, `free`, baseline, scores, L and observables; no uniquely known physical fault support is needed. Use the established coverage/selection framework and credit it. The samplewise decomposition applies even when the ordering is data dependent; its fixed-order distribution formulas cannot simply be imported for BP-derived orderings. [Logical-Space Theory of OSD](https://arxiv.org/html/2610.24503v1).

These outcomes have limited meanings:

- **Absent:** the finite 1FV family misses the correct class. This does not establish that the class is intrinsically unreachable or that additional generic search is a new contribution.
- **Present but loses:** the list contains the correct class without a winning representative. This does not prove model mismatch or an incorrect likelihood objective; finite representation and unavoidable stochastic ambiguity remain possible.
- **No distinct actionable pattern:** stop this proposed paper argument. Do not keep expanding searches until both witnesses become correct.

This is a diagnosis gate, not itself the proposed novelty. A subsequent mechanism claim needs an explanation or controlled intervention beyond reusing that known taxonomy. Cached final LLRs cannot establish oscillation or a trapping set. Do not select AA, damping or another dynamical method without the corresponding evidence.

## What could support a later task-specific paper

After a distinct lever is identified, freeze one intervention and test all shots in a fresh natural-noise stream from the exact same circuit distribution. Use independent seeds, preserve naturally repeated observations, and keep actual logical outcomes evaluation-only. The current 512 must not be repackaged as untouched evaluation through a random split.

Compare against an appropriate strong accessible same-task decoder, especially the known search and disagreement policy when relevant, with comparable tuning opportunity and honest end-to-end cost. If changing BP dynamics, include matched extra work and fixed damping; if claiming a history/safeguard contribution, add DIIS and the relevant close dynamic-memory method. If changing scores, include the straightforward Bernoulli log-odds control for the declared independent DEM. Method-dependent controls should follow the mechanism rather than create an unlimited comparator project.

Report paired rescues and regressions, total shot logical errors, uncertainty and actual total CPU/memory, including fallback and rejected work. Existing K500/K1000 choices derived from full enumeration have no measured standalone truncated-search speedup. A finite confirmation size must follow the desired effect and discordance uncertainty; twelve inspected failures do not supply adequate power automatically. A predeclared fixed-sample or valid sequential plan prevents sampling until significance. Insufficient evidence is inconclusive.

**Publication go condition:** an original mechanism or useful task-specific intervention, a verified explanation/ablation, and a meaningful accuracy-cost result surviving strong controls and fresh same-task confirmation. Cross-family experiments are optional unless the claim expands. **No-go condition:** only known search headroom, case-specific repair, a weak-baseline advantage, or no residual useful effect after fair controls.

The old positive structure-aware compiler claim remains unsupported. That is not a universal veto on this different research question. The best immediate action is the saved-candidate diagnosis, not a manuscript, AA implementation or another broad experiment campaign.
