# Runner repair: kernel-owned lifecycle and final accounting

18 November 2026. New stdlib-only engineering version; all earlier failed
protocols remain frozen. No optimization, decoder, circuit sampling or model
fitting. This stage does not repeat the stopped13-control native entry.

## Design

os.posix_spawn launches each exact owned PID. KernelChild alone performs every
normal, pending-exit and cleanup reap using wait4(owned_PID,WNOHANG), obtaining
status and per-child usage. There is no Popen/poll/wait competitor for the worker,
no wildcard reaper and no aggregate RUSAGE_CHILDREN. The interim ps query uses
subprocess.run for its own separate query child only. Parent SIGCHLD must be
SIG_DFL; custom/ignored handlers are rejected before spawn. Child masks are
cleared and TERM/INT/XCPU defaults reset before Python startup.

PID0 means no final evidence: ignore its status and usage. Exact owned PID with
terminal status releases ownership BEFORE resource validation; bad usage then
censors accounting and cannot justify a stale PID signal. ECHILD/foreign PID
means lost ownership, not normal exit; no further signal/query to that PID.
Repeated final polls are cached. Kernel CPU/RSS and rounded interim ps maxima
remain separately named; equality across their sampling/units is not assumed.

Known live samples with a counter reset or zero RSS stay invalid after exit.
Z, explicit ?E and absent-PID samples can enter a bounded .5-second exit-
confirmation phase with no further ps queries. Only actual owned wait4 reaping
and valid final usage confirm completion. Timeout remains a monitoring failure.
Zero interim accounting never resets a maximum. Unsupported states or malformed
live observations remain invalid. Kernel final CPU/RSS can reveal a crossed
budget after normal exit; that process is censored without a fictional kill.

A try/finally starts immediately after successful spawn and owns cleanup before
launch metadata or setup work. All stdin/log descriptors are closed; temporary
descriptors are kept above stdio before posix_spawn DUP2/CLOSE actions. Same-owner
TERM/.5s then KILL/.5s cleanup is bounded; unreaped/lost ownership blocks further
children and is reported. Abrupt parent death is outside this demonstration.

## Fixed controls, once after concrete AI supervisor preflight/freeze

| Control | Expected observation |
|---|---|
| normal_exit | Kernel-confirmed exit0 and final usage |
| nonzero_exit | Kernel-confirmed exit7, separate nonordinary outcome |
| cpu_work | Natural exit after.1CPU work, nonzero final CPU |
| final_CPU_over_budget | Control-only kernel sampling until natural exit after.12CPU; final CPU>=.05 censors, no kill claim |
| parent_wall | Sleep5 with.15-wall threshold; owned TERM exit |
| parent_CPU | Spin with.25CPU threshold; owned TERM exit |
| parent_RSS | Fixed96MiB allocation attempt,64MiB threshold/baseline below; owned TERM exit |
| TERM_to_KILL | Worker records installed TERM ignore; wall.3 triggers TERM timeout then owned KILL exit |
| setup_failure | Deliberate post-spawn OSError, owned cleanup and final usage |
| exit_candidate_confirmed | Actual live/barrier evidence, separately labeled synthetic ?E sample, release barrier, actual kernel exit |
| live_counter_reset | Deliberate live R/CPU0 after positive samples; stays censored through owned TERM/reap |
| exit_candidate_timeout | Deliberate ?E while child stays alive; confirmation expires, censored and TERM/reap |

The final-only CPU control deliberately suppresses ps CPU observation until
exit, retaining a wall4 watchdog and OS request[5,6]. This replaces an arbitrary
fixed observation delay and tests final-accounting logic without a timing race.
The exit-candidate controls do not claim natural reproduction of macOS ?E.
Actual valid source queries and corrupted counterparts are retained separately.

At most12 children,90 controller seconds,8-second admission reserve; no
calibration, retries or parallel workers. Defaults CPU3/wall4 seconds/RSS256MiB;
dedicated controls use the lower thresholds above. Every child requests OS CPU
[5,6], without relying on proved hard enforcement. Poll.01 seconds, ps timeout.5,
exit grace.5 and signal waits.5 each. Record actual response/overshoot; these are
polling triggers, not instantaneous guarantees. Any unexpected test outcome
stops remaining controls; preexisting outputs block a rerun.

Before execution, fake-only checks cover PID0 garbage, exact/foreign PID,
ECHILD, bad final usage after reaping, nonterminal status, cached ownership,
SIGCHLD, source/units and malformed telemetry. They launch no workers. The
independent saved-output audit imports none of the owner/runner/control helpers.
It checks identities, wait4 chronology/final usage, resource/cleanup outcomes,
controlled-fault provenance and actual counts. Require postreview before claims.

A pass supports this runner core on the recorded Darwin environment. It does
not validate the optimizer adapter, real cases131/228, all platforms/races,
instantaneous containment, decoder improvement or publication novelty. Relevant
optimizer-attempt count stays19. After validation, update the user-authorized
public GitHub mirror with sanitized code, results and honest current status.

Primary APIs: [Python wait4](https://docs.python.org/3.12/library/os.html#os.wait4),
[posix_spawn](https://docs.python.org/3.12/library/os.html#os.posix_spawn),
[resource accounting](https://docs.python.org/3.12/library/resource.html).
