# Independent AI supervisor preflight

18 November 2026. Read-only review of `PROTOCOL.md`, `diagnose.py`, `audit.py` and `control.py` before freezing or running this diagnosis. This is internal AI review, not human peer review. No scientific calculation or adapter was executed by this reviewer.

**GO for this bounded offline diagnosis, conditional on the frozen hashes, runtime adapters and independent audit passing.** No material scientific-design or algebra defect remains apparent in the reviewed code. This does not approve a decoder improvement experiment or establish a new mechanism.

## Scientific contracts checked

- The fixed 24-case selection and original saved lists are retained. Each list includes the baseline plus 10,446 existing candidates, for 250,728 members total. No source decoder, generator or search helper is imported.
- Absolute classes use L-row i as bit i. Primary powers-of-two encoding and independent byte-packing encoding both have planned 4,096-code round-trip checks. The primary affine formula includes the baseline class and explicitly requires zero free bits; the audit instead reconstructs complete vectors and checks all H/L rows with int64 arithmetic.
- The selected correction is the original saved source output. Strict-positive improvement, first-maximum chronology and the zero-improvement baseline rule are preserved. Raw-score minima cannot reselect a correction. Raw and source representatives/ties are reported separately.
- True observables enter only the offline diagnosis. Class counts are explicitly not posterior masses. Missing true-class scores and undefined margins are null with a reason; a robust margin-sign disagreement stops validation. Controls and known rescues must retain true-class coverage.
- The independent audit imports no primary helper and checks every list member in bounded batches, including baseline membership, class counts/minima, source winner, margins, reported scores, input/output hashes and prior result manifests. Exact saved-score representative identity and independently recomputed numeric minima are distinguished to handle harmless floating summation differences.
- Primary and audit have separate finite CPU/wall/RSS limits. Incomplete, invalid, infrastructure-stopped and resource-stopped outcomes are unresolved. The protocol prohibits post-outcome score, tolerance, candidate or budget changes.

## Problems found and fixed before freeze

1. **Resource-cause reporting:** the first controller version would label a handled resource-stop report followed by exit 1 as an abnormal exit. The revised classifier preserves this as resource censoring while retaining completed-report-plus-exit-1 as abnormal. Audit budget checks and its CPU handler now use a typed resource exception and save a partial-count stop report. A new classifier adapter covers this path. Primary resource checks also run after each case.
2. **Audit coverage robustness:** the first audit used `zip` without an explicit row-count/order assertion and later emitted hardcoded completion totals. The revised audit verifies 24 rows and exact ID order before iteration, checks the completed verification count and diagnosis total, derives aggregate counts, and verifies the reported selected score against the saved canonical score.

I reread the revised implementations of these fixes. They affect operational accounting and independent verification, not the scientific candidate set, source choice or scoring. They were found before real execution; no claim is made that they corrupted a previous result.

## Interpretation and remaining limits

The output can establish only whether these saved lists contain each observation's correct logical class and whether the preserved source choice selects it. Correct-class absence is a property of this list. Correct-class presence with a losing score does not establish noise-model error, an incorrect likelihood objective or intrinsic uncorrectability. Neither outcome diagnoses BP oscillation or justifies AA. Coverage/selection is an existing framework, and this selected development panel supplies no population prevalence or new error rate.

After the run, require normal process records, completed per-case coverage, unchanged frozen inputs, the independent audit and a supervisor postcheck before reporting the conclusion. If a gate fails, preserve the stopped output. Do not choose an intervention automatically from the diagnosis.
