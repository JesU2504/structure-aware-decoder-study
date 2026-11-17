# Headroom attempt: stopped at baseline gate — 17 November 2026

**Repair headroom remains unresolved.** The attempt stopped at its predeclared
baseline-equivalence gate. Case 51's Python-reconstructed order-zero correction
differs from the cached native OSD0 correction in four bits. No real-case 1FV
search was run, and no case was removed or substituted to bypass the mismatch.

## Risks reviewed before execution

`RISK_REVIEW.md` enumerates the main identifiable risks and responses: stale
inputs/caches, data selection and label leakage, float precision/ties, hidden
native pivot ambiguity, rank/dependent rows, packed-bit parity, candidate
coverage/scoring, resource censoring, timing scope and invalid population or
publication claims. It is not a proof that every possible error was anticipated.

The supervisor independently reviewed the source, written protocol and runner.
The implementation review caught a genuine controller bug before execution:
a saved `completed` report could have hidden an abnormal child exit. The fixed
controller requires a normal exit and complete report. Version one was preserved
in `pre_run_v1/`; the scientific inputs, 24 selected cases, algorithms and caps
were unchanged. The corrected version received GO, and version two was frozen
before real-case helper execution. No rescue outcome informed that correction.

The fixed cases were all twelve original primary failures and the first six
BP-nonconverged primary successes from each of the two original seed blocks.
The target was the pinned published **Python stable-order 1FV branch**, not
assumed access to hidden native OSD-CS pivot internals. All 24 reconstructions
had to match before any real-case search. Exact e0 agreement alone would still
not prove that Python and native pivot sets are identical.

## What actually ran

Ten completion/exit classifier checks and three controlled wall/RSS/CPU watchdog
probes passed. Packed-bit/duplicate-coordinate/word-boundary and dependent-row
toy algebra adapters passed, including source tie/no-change selection behavior.
The macOS CPU-limit probe exited with SIGXCPU; the adapter explicitly allowed
the platform's CPU-limit signals without treating them as successful work.

The first eight real baseline gates passed for cases
0, 1, 2, 3, 4, 5, 23 and 24. The ninth gate, case 51, failed exact equality.
The other fifteen selected cases were **not attempted**, not failed. The
`search/` directory is empty, and the journal contains no all-gates-passed or
real-search event. The controller correctly reports `baseline_mismatch`, with
worker exit code zero and no watchdog or infrastructure stop.

Worker computation took about 1.45 CPU seconds and 1.61 wall seconds; controller
observation lasted about 1.67 seconds. Peak child RSS was 230,883,328 bytes
(about 220.2 MiB), within the operational ceiling. This is child-process memory,
not whole-machine memory or a guarantee of instantaneous hard containment.

There were nine algebraic baseline reconstructions, zero real-case full/prefix
1FV searches, zero new native BP/decoder calls and zero new physical shots.

## Independently checked discrepancy

The changed raw DEM columns are:

| Column | Native correction | Python reconstruction | Python information-set role |
| ---: | ---: | ---: | --- |
| 938 | 0 | 1 | pivot |
| 940 | 0 | 1 | pivot |
| 949 | 1 | 0 | free |
| 1006 | 1 | 0 | free |

All four have exactly the same cached float64 BP LLR,
3.6994400041376805, and prior probability, 0.003733333333333521.
The tied group straddles the Python pivot/free boundary. The four-bit difference
has zero detector and zero logical image: H delta = 0 and L delta = 0.
Both full corrections have zero syndrome residual and the same logical vector;
both still misidentify nine actual logical-observable bits. This is **not** a
new rescue or a newly demonstrated logical error caused by tie handling.

The source surrogate scores are 454.85430452652645 (native) and
454.85430452652656 (Python), equal up to approximately 1.1e-13 numerical
roundoff. The evidence is strongly compatible with an ordering/tie ambiguity.
Native pivot ordering was not observed, however, so the exact cause and any
platform dependence remain unproven. Do not infer that the source paper's
reported error rates are invalid.

The frozen protocol required bit-identical baselines to isolate the added
search. Same syndrome, logical class and score do not justify relaxing that
rule after inspecting outcomes: differing information sets can change a later
search neighborhood. We therefore did not change sorting, replace the native
baseline or continue the headroom comparison.

## Post-experiment verification

`audit_stopped_run.py` did not call reconstruction or decoding. It verified:

- All 67 frozen file hashes, the preserved v1 source/selection and the unchanged
  scientific inputs across the pre-run amendment.
- Exact selection from the previous 512 paired observations and metadata.
- All nine saved gates, full 1800-row syndrome equations, independent pivot
  rank1794, reduced pivot identity, stable order and tie statistics.
- The four changed columns, equal LLR/prior values, H/L equivalence, logical
  outcomes and numerical scores using the saved arrays.
- Correct stop/journal/resource accounting and zero real-case searches.
- All nineteen earlier result manifests unchanged.

The audit passed. **Real full-search candidate parity and score checks were
not reached**; only their small synthetic adapters passed. This distinction is
preserved in `RISK_OUTCOME.md`. It would be incorrect to report a negative repair
result or count the fifteen unattempted gates as failures.

## Decision

The attempt is complete as a properly stopped compatibility check. It cannot
tell us whether the published 1FV branch repairs the original twelve failures.
The next bounded action, if pursued, is a saved-data/native ordering diagnostic
that explains the reconstruction discrepancy. It should precede any new search
or a separately defined experiment with an explicitly different baseline policy.
No such follow-up was executed here.

The original 12/512 native failure reproduction remains valid and unchanged.
This attempt establishes neither algorithmic uncorrectability, a new structural
mechanism, a compiler improvement nor publication novelty. The
[independent AI supervisor review](../publication_strategy_2026-11-17/supervisor_headroom_postcheck.md)
confirms the correct stop and passing audit, corroborates the saved four-column
comparison, and recommends an exact-version ordering diagnostic before any new
search. No further experiment was needed for this milestone's post-run check.
