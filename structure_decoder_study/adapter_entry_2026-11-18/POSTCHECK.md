# Independent AI supervisor postcheck — failed native entry

18 November 2026. Internal read-only AI review by
`/root/timeout_repair_supervisor`; not human expert validation. The reviewer
performed no optimizer, worker or ps experiment.

**The native entry failed and must remain failed.** The first fixture produced
a valid solver result, but the monitor observed an unsupported process-state
record before confirming exit. The controller correctly stopped the suite.
A mathematically valid saved artifact is separate from successful integration.

The reviewer independently verified:

- All50 frozen input hashes and23 output hashes matched.
- Exactly one optimizer attempt and one persisted return were recorded.
- One worker ran; the remaining12 fixtures were unattempted.
- Controller execution took0.690395 seconds.
- The saved vector[1,1,1,1,0] satisfies exact binary/parity/slack constraints
  and achieves the toy's exhaustive optimum of4.
- Raw persistence, finalization, handler restoration and the empty stable
  signal ledger were retained.
- Owned reaping confirmed exit0. No termination signal was needed.
- There were zero research-case calls or physical samples.

The triggering record was `4285 ?E 0 0:00.00`, with both surrounding polls
initially reporting no exit. The next owned poll confirmed exit. The frozen
policy rejected the unknown leading state and retained that monitoring failure
after reaping, as required. It preserved earlier CPU/RSS maxima rather than
resetting them to zero.

Our preparation did not establish that its state allowlist covered every
ordinary exit transition. Apple's published source provides a plausible
explanation involving an unknown thread-derived state and an exiting-process
modifier, but is not matched to the installed ps binary's exact revision.
This does not establish Z, explain historical SIGXCPU or justify retrospective
acceptance of the unsupported record.

Do not edit the frozen acceptance rule, resume remaining fixtures or
characterize the saved toy as an entry pass. Cumulative optimizer attempts
for this branch are now19, including the previous18. Preserve the failure
and close this bounded execution.

The next debugging stage should isolate process ownership/accounting using
**stdlib-only fixtures**. A promising design uses one exact-owned-PID wait4
reaper, capturing exit status and per-child resource usage; interim ps data
remain supplementary. Python documents that wait4 returns PID/status/resource
usage. ([Python wait4](https://docs.python.org/3.12/library/os.html#os.wait4))
Ordinary Popen.poll/wait must not compete with wait4 for reaping. Review and
prospectively test fixed ordinary-exit, resource-stop and cleanup-failure
controls before another optimizer entry. Final kernel accounting improves
evidence; it does not establish instantaneous containment or excuse invalid
live measurements.

**Research cases131/228 remain inconclusive and untouched. No decoder
improvement or publication claim follows from this entry.**
