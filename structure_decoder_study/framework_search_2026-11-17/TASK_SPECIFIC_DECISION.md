# Decision: investigate one task before choosing an intervention

18 November 2026. Internal AI expert and supervisor advice. No new decoder,
candidate enumeration, fit, physical sample or manuscript in this review.

**A task-specific mechanism and improvement study is a legitimate research
direction. It does not require a universal decoder or cross-family transfer.**
The contribution still needs useful new knowledge and evidence on uninspected
observations of the declared task. Prior work and strong baselines remain
relevant even when the task is narrow.

## Concrete task and prospective question

Use the accessible, source-matched BB[[144,12,12]] memory experiment:24 rounds,
circuit-level depolarizing noise p=.007 and the existing Z-check-only schedule.
Pin the generator, model and CPU decoder configuration. This is not a full
two-sector experiment, a logical gate or a compiler application.

Candidate question, conditional on diagnosis:

> Which recurring mechanism limits the specified decoder on this memory task,
> and can an intervention targeting that mechanism improve final logical-error
> performance at a declared computational cost on fresh observations?

This is a question, not a supported positive claim. Known 1FV search already
repairs10/12 inspected baseline failures. Closely related published/preprint
work already studies this exact task, so that recovery result is groundwork.

## One next diagnostic

Audit all24 ALREADY SAVED candidate sets, including failures and success controls,
without new decoding or expanded search. Determine the logical classes represented
by each baseline plus10446 candidates and their best declared scores. Classify
the two remaining cases131/228:

- No correct-class member in this exact candidate list: a list-coverage limit.
- Correct-class member present but not selected: compare representatives, margins,
  objective and fixed tie rule.

The second outcome does not by itself prove the score or noise model is wrong;
a finite list may lack a competitive representative, and stochastic observations
can defeat an optimal decoder. The first says nothing about corrections outside
this list. The taxonomy is established prior work and must be credited.

Do not commit to Anderson acceleration unless later trajectory evidence motivates
it. Its message-state interface work is a separate conditional route. The two
residual failures are not evidence of oscillation or a dominant population mode.

## What would support a later paper

Use the current512 observations for development. After choosing and freezing a
distinct intervention, evaluate whole fresh natural-noise streams of this SAME
task in paired comparisons. Count rescues and regressions, all outcomes and full
CPU costs, with sufficient prespecified precision and finite resource limits.
Compare against strong applicable same-task methods, including known1FV/search
controls where relevant, rather than only an intentionally weak baseline.

Independent new seeds can establish within-task replication. Other codes,
schedules or noise rates are needed to support corresponding transfer/robustness
claims, not as universal prerequisites for a narrowly stated result. Improving
two known witnesses alone is insufficient. If the mechanism and intervention
reduce to established work without a useful new finding, stop that paper framing.

## Academic precedent and boundaries

The peer-reviewed [quantum trapping-set study](https://quantum-journal.org/papers/q-2021-10-14-562/)
supports the mechanism-led scientific workflow. IBM's [Gross-code workshop paper](https://research.ibm.com/publications/decoding-the-gross-code)
shows interest in specific-code decoding. Neither establishes our novelty or
predicts acceptance. [Adaptive-qLDPC](https://arxiv.org/html/2609.37629v1) is a
particularly close exact-task prior; [logical-space OSD theory](https://arxiv.org/html/2610.24503v1)
already formalizes coverage versus selection.

The original positive structural-cost/compiler claim remains on hold. The new
narrow study should be assessed on its own evidence and stated scope.

Read the [expert assessment](task_specific_expert.md) and
[supervisor assessment](task_specific_supervisor.md).
