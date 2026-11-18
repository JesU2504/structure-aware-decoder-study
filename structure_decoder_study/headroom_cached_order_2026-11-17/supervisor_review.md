# AI supervisor review: completed cached-order headroom diagnostic

17 November 2026. Separate AI review of design, implemented worker/audit,
frozen hashes, execution records and saved independent-audit results. I made
no reconstruction, search, native decoder or sampling calls. This is internal
AI supervision, not external human peer review.

**Verdict: the bounded technical objective passes. The adapted 1FV search
repairs ten of the twelve verified baseline failures, with no regressions in
the twelve selected success controls. No material design or execution mistake
was found in the reviewed path. This is not yet a new publication contribution.**

## Design and execution checks

The new experiment explicitly uses the saved implementation-derived ordering;
it does not retroactively resume the failed stable-order experiment or claim
hidden native pivot equivalence. Unique rank priorities determine ordering only.
The original channel priors and `sum(log(1/p))` surrogate determine candidate
scores. The search worker's prepared inputs exclude true observables and case
roles; logical labels enter only the subsequent independent audit.

The same twelve failures and twelve predetermined controls were frozen without
new physical samples, native decoder calls or parameter changes. I independently
verified the 118 frozen input hashes. Frozen setup SHA256:
`f81a98641c5d831373a503e22ab3cccb4d483c49a9563f9fcbe9c415b8724739`.

Before freezing, review identified avoidable repeated decompression of the full
saved reconstruction array inside the audit's chunk loop. Caching that array
and adding direct-score shape/finite checks removed an audit-resource risk;
these changes did not alter scientific cases, search or scoring. The earlier
controller abnormal-exit correction was retained. No outcome-driven fix or
budget expansion was made after execution started.

All 24 native-baseline reconstructions passed before any real-case search.
The journal contains the complete ordered gate/search sequence. Worker and
independent audit both exited normally without monitoring errors or censoring.
Worker costs were approximately 15.21 CPU seconds and 15.62 wall seconds, peak
child RSS 595,525,632 bytes. The separate audit used approximately 28.63 CPU
seconds and 29.40 wall seconds, peak RSS 482,394,112 bytes. Both stayed within
their declared limits. Verification cost is not decoder service time.

The audit uses explicit full candidate vectors, int64 H arithmetic and weighted
scores rather than importing the source helpers. It checked all 250,704
candidate vectors against all 1,800 detector rows, baseline identity, pivot
rank, ordered coverage, source first-maximum/strict-positive selection and
prefix score monotonicity. The largest delta/direct-score discrepancy was about
1.71e-12, below the frozen tolerance. All twenty-one earlier manifests remain
unchanged. These saved checks support the reported result; this review did not
rerun the 250,704-vector computation itself.

## What the result establishes

Full search, K500 and K1000 each repaired the same ten cases:
23, 24, 51, 66, 167, 188, 249, 256, 260 and 407. Cases 131 and 228 remain wrong.
All twelve selected native-success controls remain correct. The correctness
outcomes agree across these budgets on this panel; that is not general decoder
equivalence or monotonic logical accuracy with search depth.

Near-score ties occurred. The audit examined all computed candidates within
the frozen tolerance of the minimum; none of the 24 cases had competing correct
and incorrect logical classes in that window. This includes rescued cases 167
and 407 and near-zero-improvement controls 4 and 264. It supports the observed
logical classifications against these local numerical ties, not arbitrary
ordering, platform or candidate-family robustness.

The output therefore supplies observed recoverable failure pairs. It does not
show bounded-distance correction, maximum-likelihood decoding, physical-fault
weight or the impossibility of repairing the two remaining cases.

## Research decision

**Close the feasibility milestone successfully, then stop automatic expansion.**
Do not describe this as a new natural error rate of 2/512: the other 488 native
successes were not searched and their possible regressions are unknown. The
selected controls do not estimate population regression probability or provide
a causal matched comparison. The data are inspected development observations
from one Z-check-only memory task, not an independent validation corpus.

The known stronger-search mechanism, its rescue headroom and a local ordering
compatibility correction do not yet justify a new router, decoder or compiler
paper. The present method/publication proposal remains **no-go until a distinct,
falsifiable claim is identified**. Any later compiler claim needs varied valid
tasks, inputs available at compilation time and a consequential decision that
improves. This result does not supply those missing pieces. Preserve the checked
testbed; require that new question before another data or training campaign.
