# Runner core repaired and checked with twelve stdlib controls

18 November 2026. **All12 fixed process controls passed**, followed by the
independent saved-output audit and AI supervisor postcheck. No optimizer,
decoder, research observation or new physical sample was used.

## Repair

The worker is launched with os.posix_spawn. One exact-PID wait4 owner collects
its exit status and final per-child CPU/peak-RSS usage in normal execution,
pending-exit confirmation and cleanup. No Popen worker, competing reaper,
wildcard PID wait or aggregate child accounting is used. Interim ps measurements
remain separately identified; they do not decide that a worker has exited.

A terminal-looking or absent-PID sample requires actual kernel confirmation.
Live counter resets remain censored even if the worker later exits. Once
kernel reaping releases a PID, invalid usage cannot justify another signal or
query against it. Post-spawn exceptions and descriptor setup have owned cleanup.

## Fixed outcomes

| Control | Observed result |
|---|---|
| normal_exit | Kernel exit0 and final usage |
| nonzero_exit | Kernel exit7, kept separate |
| cpu_work | Exit0; kernel CPU.124795 seconds |
| final_CPU_over_budget | Exit0; kernel CPU.14425 exceeds.05; censored, no kill |
| parent_wall | Wall threshold triggered TERM; exit-SIGTERM |
| parent_CPU | Interim CPU.25 triggered TERM; kernel CPU.25541 retained separately |
| parent_RSS |64MiB threshold crossing after allocation; TERM and final kernel peak112754688 bytes |
| TERM_to_KILL | Declared TERM timeout followed by KILL; exit-SIGKILL |
| setup_failure | Deliberate post-spawn exception; owned TERM/reap and final usage |
| exit_candidate_confirmed | Labeled synthetic ?E after actual live evidence; barrier release and real kernel exit0 |
| live_counter_reset | Labeled live CPU reset stays censored through TERM/reap |
| exit_candidate_timeout | Labeled exit candidate without exit times out; censored and TERM/reap |

The suite ran once, in2.610720958 controller seconds under its90-second ceiling.
There were12 worker launches and32 preceding fake-only checks, with no
calibration or retries. The controlled exit-confirmation case illustrates
why source-specific records matter: interim CPU.14, final user/system sum
.139078, kernel peak11976704 bytes and a retained terminal-unavailable flag.
These sources were not forced to agree.

The ?E and live-reset controls deliberately mutate recorded interim observations;
their actual source queries and mutations are saved separately. They validate
the declared policy with real process exits, not natural reproduction of ?E.

## Independent review and limits

The audit imports no runner/owner/controller helper. It verifies all28 frozen
inputs and79 output files, exact-PID final reaping, wait chronology, raw interim
sample reconstruction, retained source-specific maxima, controlled-fault
provenance, resource crossings, TERM/KILL causality, final usage and actual
counts. The AI supervisor independently accepted this bounded runner-core
result. Earlier failed protocols are preserved unchanged.

Supported scope is the tested Darwin lifecycle/accounting/cleanup paths.
Optimizer-adapter integration, all platforms/races, abrupt parent-death
containment and instantaneous resource caps remain unvalidated. These are
process tests, not a decoder improvement or publication novelty claim.

No optimizer attempt was added; the branch total remains19. Cases131/228 stay
inconclusive and untouched. Next integrate this core into a new versioned native
adapter and independently validate that integration before another scientific
probe. Do not resume the stopped native entry or infer a useful real-case
solver outcome from these tests.

Evidence: [plan](PLAN.md), [offline checks](offline_checks.json),
[execution](execution.json), [independent audit](audit_result.json),
[AI supervisor postcheck](POSTCHECK.md), [final checks](final_checks.json).
Freeze SHA256:
`bfde4c57be5d039a74a9160e744d68d92bf7dbfc8d120ec8494166b10b7687c7`.

The public mirror update is recorded separately in publication_2026-11-18.
