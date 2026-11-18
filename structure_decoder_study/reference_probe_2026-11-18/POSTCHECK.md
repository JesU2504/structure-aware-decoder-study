# Independent AI supervisor postcheck: reference probe

18 November 2026. Read-only review of the frozen protocol/code, two process records and logs, stop reports, invocation journal and independent audit. This is internal AI review, not human peer review. No optimization, decoder call, new sample or scientific calculation was executed by this reviewer.

**Integrity/bookkeeping PASS; scientific result INCONCLUSIVE for both cases.** The planned two attempts occurred without retries or outcome-driven changes. Neither returned a usable Python solver result or a validated cheaper correct-class witness. This does not resolve whether a competitive correct-class representative exists outside the saved list.

## What happened

| Case | Recorded elapsed child CPU | Recorded child wall | Peak child RSS | Outcome |
| --- | ---: | ---: | ---: | --- |
| 131 | 62.118 s | 63.037 s | 201,801,728 bytes | SIGXCPU handled while `highs.run()` was returning; stopped |
| 228 | 61.596 s | 62.197 s | 192,970,752 bytes | Same return-path interruption; stopped |

Both native logs report their solver time limit, an infinite primal bound and no incumbent. Both Python tracebacks enter the installed SIGXCPU handler inside the SciPy/HiGHS call. The handler raised the typed budget exception; each child exited 1. The controller preserved both stops and attempted the fixed second case as allowed. It detected no wall/RSS watchdog stop or monitoring failure.

The generic stop message says “Child CPU resource limit,” but the saved measurement is approximately 62 elapsed CPU seconds (`process_time() - START_CPU`), whereas RLIMIT_CPU concerns absolute process CPU. START_CPU and the active resource limit at failure were not logged. **Unexpected SIGXCPU with recorded elapsed CPU near 62 seconds is established; the exact limit interaction is not.** Neither reaching the requested 90-second limit nor a limit violation/misfire is proved. The earlier suggested threading explanation was withdrawn and is unsupported. Requested `threads=1` and this timing record do not establish a native threading root cause.

No `solver_returned` event, raw result metadata or incumbent array reached the worker's reporting stage. Consequently no new correction could undergo parity/cost verification. The literal log bounds, approximately 495.603 and 428.543, are numerical diagnostics only; they are not exclusion certificates or usable returned results.

## Design, execution and audit assessment

The mathematical scope remains coherent: fixed cases, unchanged full parity model/score, integral slack, known feasible correct-class input vectors, current full-1FV wrong thresholds, oracle-assisted logical target and a one-sided witness rule. The log confirms 12,240 binary variables, 1,812 integer auxiliaries and zero continuous variables. No evidence here establishes a parity-formulation or input-consistency error.

The operational outcome exposes a **validation gap**. Entry tests checked tiny optimal/infeasible solves and invalid returned arrays, but did not exercise the anticipated solver-time-limit return path. That integration path failed on both real attempts. This is not a demonstrated mathematical decoder failure or a training issue. It also is not evidence that a full 90-CPU-second witness search was completed. The precise underlying software/environment cause has not been diagnosed.

The bounded containment and preservation rules worked: no retry, increased budget, changed score, new method or additional real case followed the stops. Preserving the original frozen code rather than patching and silently rerunning was appropriate.

The independent audit completed normally, exit 0, in approximately 0.802 CPU/1.472 child-wall seconds with 75,087,872 bytes peak RSS. It verified frozen/output hashes, known feasible vectors, source-reference identity, invocation chronology and 23 prior result manifests. Its PASS validates the stopped-run records and lack of exclusion claims; it does not validate unavailable solver outputs or supply an optimization answer.

There were four completed tiny entry optimizations and two started real reference-optimization calls. The real journal contains two starts and no Python-return events. No new BP/OSD/LSD call or physical shot occurred. These were nevertheless additional decoding-related optimization attempts, not zero computation.

## Scientific interpretation

The earlier checked result is unchanged: correct-class candidates exist in both saved 1FV lists, but their best listed scores lose by large margins. This probe neither finds an outside-list competitive representative nor rules one out. It does not distinguish limited representation from minimum-individual-error scoring ambiguity, establish model mismatch, diagnose BP dynamics, or justify AA/rescoring. An infinite logged primal bound does not contradict known mathematical feasibility; it reports failure to obtain an incumbent in that solver attempt.

The probe's negative branch was explicitly disabled. It would be incorrect to convert timeout/signal censoring, numerical dual estimates or unavailable incumbents into intrinsic uncorrectability, a global optimum claim or evidence against a new decoder. There is no population error-rate result, online repair or publication novelty here.

## Next disposition

**Hold further real-case reference solves and performance expansion.** Do not raise caps or change solver settings merely because these attempts were inconclusive.

If this reference route is retained, the next bounded task should be a timeout/signal integration diagnosis on a nonresearch fixture, preserving this run. Exercise time-limit returns with and without an incumbent. Record absolute CPU, START_CPU, user/system CPU and active resource limits before/after the call, plus signal origin where available. Demonstrate that the worker can retain a returned result or correctly label interruption without assuming its cause. This is an infrastructure gate, not another attempt to solve cases 131/228. No such test is executed or authorized by this report. If it cannot be resolved within a small finite engineering scope, pause this reference route rather than build a new certifier or broaden the optimization project.

Task-specific research remains academically possible, but neither this probe nor the saved-list taxonomy establishes an original actionable intervention. A later method campaign still requires a distinct label-blind mechanism, strong fair controls and fresh same-task confirmation. A manuscript or a larger benchmark is not the next step.
