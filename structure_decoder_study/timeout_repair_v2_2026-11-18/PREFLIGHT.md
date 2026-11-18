# Independent AI supervisor preflight — V2

18 November 2026. Internal AI review by `/root/timeout_repair_supervisor`,
not human expert validation. Read-only review; no optimizer or research calls.

**GO for the frozen nine-scenario V2 synthetic confirmation**, conditional on
freeze hash gates, the completed independent audit and final postcheck.

The reviewer independently checked all 119 V1 whole-manifest files and all 30
prior reference-probe manifest files. V1 remains failed: its OS hard-CPU test
continued to about 7.9 CPU seconds until the wall guard. Its manifest SHA256 is
773ba4312938d81f167963e9d4932a9922d150e54731ed0206062fbb563ff729.
The reviewer confirmed the unchanged worker.py/result_guard.py hashes.

The parent monitor has a one-second query timeout, post-query wall check,
strict owned-PID sample validation and fail-closed errors. It keeps raw CPU
tokens, timestamps and PID evidence. CPU budgets are 3 seconds for the hard
fixture and 10 for others, alongside wall/RSS monitoring; termination uses
SIGTERM then optional SIGKILL, and finally cleanup reaps an active child.
Independent audit requires observed CPU crossing [3,3.5] seconds, first
termination within .1 seconds of that sample, matching spin telemetry and
correct censoring, plus graph/result/restoration/injection checks.

Preflight caught an edge case: the first parser accepted a zero-day prefix
with an invalid clock format because it tested the numeric day count rather
than prefix presence. Before freeze it was corrected to track prefix presence;
both zero-prefix invalid cases were added. Initial unit output is retained as
unit_result_initial.json; final unit_result.json has five valid parser examples,
twelve invalid parser examples, four malformed monitor examples and censoring
checks. The reviewer reread the fix and final checks. No optimizer was run to
make this correction.

The reviewer confirmed five additional synthetic optimizer API attempts and
nine children, at most twelve attempts/twenty children across V1+V2, and
<=120 measured cumulative controller seconds. Recorded V1 execution used
12.409363166 seconds, so V2's 85-second stage ceiling fits. No retries,
research-case reruns or budget escalation are approved by this preflight.

A pass would establish controlled return preservation and parent CPU/wall
containment on this machine. It would not prove OS hard-limit enforcement,
an RSS-limit crossing, historical signal origin, every race/platform, solver
tractability, decoder improvement or publication novelty. V1 stays failed
and preserved regardless of the V2 result.
