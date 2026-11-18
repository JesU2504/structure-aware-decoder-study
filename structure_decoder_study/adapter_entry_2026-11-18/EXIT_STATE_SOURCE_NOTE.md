# Read-only investigation after the failed entry

18 November 2026. This note does not modify the frozen state allowlist or
reclassify the failed entry. No additional optimizer or process experiment.

The saved sequence is a positive live R sample, then `?E` with zero CPU/RSS
while both owned polls still return None, then owned reaping with exit0 about
.00024 seconds later. The final toy report predates the unknown sample.
This is evidence of an exit transition; it is not an allowed Z observation
under the frozen protocol. Our manual-derived state model was incomplete for
this environment, and its safe rejection correctly blocked the suite.

Apple's public ps source helps explain a possible output path. The state printer
uses Z for its zombie case; otherwise it uses a Mach state table. It appends E
when its exit flag is set and the sampled process status is not zombie.
([Apple print.c, pinned commit](https://github.com/apple-oss-distributions/adv_cmds/blob/6bed8737a34dbb54782a18f47dccf933a9967a12/ps/print.c#L444-L465))
The companion source initializes a default state index that maps to `?`, with
specific thread states replacing that default when available.
([Apple tasks.c, pinned commit](https://github.com/apple-oss-distributions/adv_cmds/blob/6bed8737a34dbb54782a18f47dccf933a9967a12/ps/tasks.c#L27-L45))

**Inference, not established local binary provenance:** this source provides
a plausible unknown-Mach-state plus exiting-flag explanation for `?E`. We have
not matched this commit to the installed ps binary, proved its precise kernel
sampling sequence or established that `?E` means zombie. The commit is
6bed8737a34dbb54782a18f47dccf933a9967a12, queried read-only from Apple's repository.
Neither zero accounting nor later normal exit retroactively passes the gate.

The supervisor recommends a separate stdlib-only ownership design: use one
exact-owned-PID reaper to obtain kernel exit status and per-child final resource
usage, with ps retained as interim telemetry. Python exposes this via wait4.
([Python wait4](https://docs.python.org/3.12/library/os.html#os.wait4))
Do not mix Popen.poll/wait and wait4, and do not use aggregate RUSAGE_CHILDREN
because ps queries also create children. A new prospective stdlib-only gate
should test this design before another optimizer entry. Final usage would
improve accounting; it would not prove instantaneous resource containment.
The current failed run remains frozen and is not resumed.
