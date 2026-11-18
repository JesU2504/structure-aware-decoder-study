# Next task: bounded integration, then a scientific decision

## Objective and exit criterion

Integrate the validated kernel-owned runner with the raw-first optimizer
adapter. Demonstrate that the combined implementation preserves/classifies
native returns and failures under a fresh bounded nonresearch entry.

This is enabling work for research. Completion is a reviewed implementation,
a passed or honestly failed frozen entry, independently audited evidence and
a clear next decision. It is not a commitment to keep running until a pass,
rerun real cases, produce a decoder improvement or write a paper.

## First session

1. Read CLAUDE.md, the research handoff and ledger.
2. Verify the public snapshot with both tools/verify.py and
   tools/verify_progress.py. These consume saved data only.
3. Inspect current owner.py/runner.py and the earlier transport/worker/audit.
   Identify test-only dispatch versus reusable process ownership/transport.
4. Record the actual environment. Prior successful runner tests used Darwin;
   wait4/posix_spawn require a suitable Unix environment. A different host is
   a new environment, not proof the old host's recorded hashes are invalid.
5. Create a new branch and a new versioned implementation/output directory.
   Do not change frozen historical source or rerun in historical output paths.

## Read these source files

All paths in this list are relative to the repository's
`structure_decoder_study/` directory.

- `runner_repair_2026-11-18/owner.py`: the only owned worker reaper.
- `runner_repair_2026-11-18/runner.py`: process creation, descriptors, interim
  telemetry, bounded confirmation and cleanup. It currently dispatches stdlib
  controls; expose a narrow approved worker-launch interface for integration.
- `runner_repair_2026-11-18/audit.py` and POSTCHECK: checks and scope limits.
- `adapter_entry_2026-11-18/transport.py`: raw-first capture and per-mode warnings.
- Its `worker.py`, `model_helpers.py` and `result_guard.py`: mathematical helper
  and persistence integration, with the failed run preserved as a counterexample.
- `reference_integration_protocol_2026-11-18/PROTOCOL.md`: original intended
  scientific invariants. Its explicit-Z entry control is superseded for a new
  kernel-owned design; do not pretend the old protocol changed or passed.

## Nonnegotiable implementation invariants

- One component owns every exact-positive-PID wait4 reap, including cleanup.
  No competing Popen.poll/wait for that worker, wildcard reaper or aggregate
  RUSAGE_CHILDREN accounting. The ps query may own its separate subprocess.
- After kernel reaping, a PID can be reused. Mark it released before validating
  usage and never signal/query/reap it again because metadata is bad.
- ECHILD/foreign PID means lost ownership, not successful exit. PID0 yields
  no usable status or usage. Keep live errors sticky across later completion.
- Preserve source-specific interim and final usage. CPU/RSS APIs may have
  different rounding/timing/units. A candidate exit state requires actual
  owned kernel confirmation; zero telemetry cannot erase prior cost.
- Cleanup covers every step immediately after successful spawn, including
  failures before metadata/state initialization. Track all descriptors from
  creation; keep masks/defaults and parent SIGCHLD assumptions explicit.
- Keep a nonraising signal ledger active through raw/provisional persistence.
  Restore the previous handler, then finalize a stable ledger/report.
- Save the raw returned array and minimal identity metadata BEFORE warning,
  status or mathematical interpretation. The old probe.solve() did not do
  this; do not reintroduce its warning-first assertion path.
- Preserve mathematical helper semantics, integrality and the1e-7 pre-rounding
  tolerance. Validate exact equations after rounding; never repair a bad vector.
- Warning expectations differ: parity uses threads/random_seed/
  mip_feasibility_tolerance, while MIS uses threads/random_seed. A warning
  error leaves raw data intact and remains a validation failure.
- Separate process outcome, payload availability and independent vector
  validity. Expected-infeasible toy status2 is a passing control expectation;
  it is not successful inference for a known-feasible real model.

## Proposed finite native entry

Write and review a new prospective protocol before any optimizer call. A lean
starting proposal is eight worker cases with at most seven optimizer attempts:

| Cases | Calls | Purpose |
|---|---:|---|
| Four existing parity toys |4| Exhaustive mathematical adapter checks, including inconsistent rows |
| Fixed MIS timeout without incumbent |1| Return/no-payload handling |
| Fixed MIS timeout with valid incumbent |1| Preserve and independently validate returned data |
| Controlled SIGXCPU during optimizer API interval |1| Preserve returned payload and distinct signal classification |
| Controlled persistence signal with labeled mock |0| Guarded raw/provisional/final ordering and restoration |

Use the existing fixed toy definitions and MIS n200/seed2026111801/density.08
settings as the starting specification. Previous MIS time limits were0/.15
seconds with presolveFalse. Parity toy options were2 seconds/1000 nodes;
other declared options must remain explicit. Do not choose fixture parameters
after viewing confirmation results. If a required branch is unavailable on
a new environment, report a coverage gap rather than silently retuning.

The proposed total native-entry ceiling is120 controller seconds, at least
11 seconds remaining before another ordinary8-wall-second child, CPU10 and
RSS1GiB thresholds, with explicit OS requests and bounded cleanup allowances.
These are prospective defaults to confirm against concrete integration code,
not an already approved launch or an instantaneous-cap guarantee.

The runner's separate12 stdlib tests already cover lifecycle/resource controls.
If integration changes that core, declare/budget appropriate regression tests
before launching them. Do not automatically repeat the old13-control native
suite or require catching a rare Z string. Count all extra workers and optimizer
starts. Branch optimizer attempts begin at19; a complete seven-call entry would
bring that branch count to26, not create seven real quantum observations.

## Review, execution and stopping

Review concrete code, fixtures, environment identities and independent audit
before freeze. An independent agent/reviewer is preferred when available;
document same-agent review as such. AI review must not be called human review.

Run the fixed batch once. Preserve raw arrays, complete-file hashes, native
attempt/return journals, signal/handler records, kernel ownership evidence,
resource observations, classifications and unattempted cases. Stop on any
unexpected monitoring, validation or containment failure. Pure mocked debugging
may continue, but a second native batch needs a separately versioned reviewed
protocol and explicit finite budget; no hidden retries or post-hoc pass rule.

Audit imports no runtime/model helpers. Verify the frozen identities, exact
toy constraints/optima, mode-specific warnings, raw-first order, ledger and
restoration, signal API interval, owned reaping, usage/units, censoring and
actual counts. A timestamp inside the optimizer API interval is not proof of
the exact native instruction at signal generation.

## After engineering: decide what advances publication

Do not turn entry success into automatic solves of131/228. Their prior native
logs already showed no incumbent near60 seconds. Perfect transport would
recover metadata but is unlikely by itself to produce a competitive correction.

Produce a short scientific decision memo before more real computation:

1. What uncertainty would the next experiment resolve?
2. Which competing explanations does it distinguish, and what result would
   reject the proposed explanation?
3. Why should the proposed method produce useful evidence within a finite budget?
4. What is distinct from the closest task/search/coverage prior work?
5. If it succeeds on development cases, what fresh paired evaluation and strong
   baselines would establish a practical same-task result without an oracle?

If these answers are weak, stop that framing or choose a better justified
method. Do not keep optimizing infrastructure, increasing timeouts or adding
neural models to obtain a positive-looking outcome.

## Deliverables

A new versioned code directory, reviewed frozen protocol, independent audit,
all attempts/results, readable status report and the scientific decision memo.
Report actual workers/optimizer calls, environment, failures and practical limits.
No manuscript yet. Publish a curated sanitized update when instructed and verify
the remote commit; do not upload unrelated workspace or credentials.
