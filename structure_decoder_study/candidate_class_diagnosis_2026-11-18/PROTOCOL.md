# Frozen saved-list mechanism diagnosis — 18 November 2026

## Question, scope and attribution

For the fixed24 inspected BB144/r24/p=.007/Z-check-only memory cases, does the
existing baseline-plus-1FV list contain the observed correct logical class?
When present, does its best available representative lose the fixed source
selection? Diagnose all twelve original failures and twelve fixed controls.
The candidate sets, decoder, priors, scoring, source ordering, actual observations
and source-selected outputs stay unchanged. No new decoder calls, physical
samples, search expansion, repair, score intervention or model fitting.

This is post hoc diagnosis of selected development data. It cannot estimate
population mechanism prevalence or establish a new error rate. Coverage versus
selection is known [logical-space OSD methodology](https://arxiv.org/html/2610.24503v1),
not a new contribution. Its samplewise interpretation is used; fixed-order
distribution formulas are not applied to BP-dependent orderings.

## Integrity and preflight

Freeze this protocol, all scripts, case selection and prior snapshots before
real-case class computation. Verify the completed headroom manifest and exact
case IDs. Reuse H,L,priors, native references, saved gates, delta/free/rf/direct
scores and saved selected corrections from the completed cached-order experiment.
Preserve previous artifacts. Test dependent-row toy algebra, class bit order,
duplicate-class grouping, absence/null reporting, positive ties, near-zero
source choices and baseline inclusion before real diagnosis.

## Candidate identity and exact selection

Index0 is the baseline e0. Indexj+1 is the saved candidate for free[j], in the
saved source order. There are10447 list members per case:10446 nonbaseline
candidates plus e0; 250728 members total,250704 nonbaseline. Count multiplicities
in this constructed list, not distinct physical explanations or posterior mass.

Use ABSOLUTE logical labels L(c), with authoritative L-row order: rowi is biti
of a12-bit unsigned code. Decode/round-trip the code independently. Transform
the observed true logical vector using the same convention. The primary method
uses L(e0) xor (Lpiv*rf mod2) xor Lfree for existing candidates. The independent
audit reconstructs complete saved vectors and applies int64 H and L directly.

Preserve the ACTUAL SAVED source correction. Verify it against strict-positive
delta improvement and first-argmax selection: maxdelta<=0 returns candidate0;
otherwise choose firstargmax(delta)+1. Raw direct-score argmin is not a replacement
for that rule. All24 existing saved outcomes must reproduce, including the
no-change/near-zero controls. Truth is used only for offline diagnosis; no
oracle-selected repair is produced.

## Class summaries and margins

Use the saved independently checked direct scores, with baseline score freshly
computed under the unchanged sum(log(1/p)) weights. For every represented class,
report count, minimum raw score, first exact raw-minimum position, source-best
delta representative/position and its raw score. Report source delta ties and
raw near-minimum classes separately. Independent full-vector scores must agree
within atol1e-8+rtol1e-12; do not retune tolerance.

For the observed true class t, report its presence/count and minimum raw score
when present. Let C be the minimum raw score among other represented classes.
Define gap=true_min-C; positive favors a competitor. If true class is absent,
true score and gap are JSON null with an explicit reason, never infinity or0.
If no competitor exists, competitor and gap are null with a separate reason.
For numerical sensitivity use symmetric tol=1e-8+1e-12*max(abs(a),abs(b)).
Outside that tolerance, the sign of the true/competitor gap must agree with
the saved source logical winner. Near ties keep the source choice and are
flagged, not resolved using truth.

Assign one result: source_success; correct_class_absent_from_saved_list; or
correct_class_present_but_not_selected. A present-but-losing class does not
prove an incorrect score or noise model: its available representative may be
uncompetitive, and individual stochastic outcomes can defeat optimal inference.
Absence says only that this particular1FV list misses the class. No assertion
about other candidates, physical fault supports, trapping sets, BP dynamics,
likelihood calibration or intrinsic uncorrectability follows.

## Execution, independent audit and stop rules

One primary process, followed by a separate independent audit. Each has its own
600CPU/900wall-second/1GiB child-RSS operational budget. Monitor CPU limits,
wall/RSS and abnormal exits. Polling is not hard instantaneous containment.
Every incomplete/invalid/resource-stopped result stays unresolved. Never expand
budgets or change scoring after inspecting outcomes. Retain per-case output,
journal, subprocess records and explicit list coverage.

The audit imports no primary grouping/helper code. It rebuilds every saved
candidate in batches<=128, checks all1800 H equations, computes12 logical bits,
full-vector weighted scores, class counts/minima, source selection and all
reported margins independently. A floating raw-minimum index may differ when
equivalent scores round differently; require saved-score index identity and
numeric minimum agreement, without asserting unique raw minima. All12 controls
and10 already rescued cases must have correct-class coverage.

Verify original snapshots remain unchanged and ask the AI supervisor to inspect
design, code and completed audit before reporting the scientific conclusion.
Do not choose an intervention automatically. If the diagnosis yields only a
known limitation without a distinct actionable lever, stop that paper argument.
