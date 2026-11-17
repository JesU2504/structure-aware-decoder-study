# Methods audit after supervisor request — 16 November 2026

See [the methods audit](experimental_design_review_2026-11-16/METHODS_AUDIT.md).
The separate AI reviewer independently confirmed a tuning-boundary concern,
then hit a usage limit before completing its report. The coordinating assistant
completed the self-audit and diagnostic; this is not external peer review.

Direct ridge/kernel solutions rule out insufficient optimization epochs for
those fits. They do not rule out insufficient data, representation bias or
poor tuning. All 31 original graph-RBF p95 fits chose the minimum alpha; 29
also chose the smallest gamma. This should have been investigated earlier.

A predeclared bounded wider-grid sensitivity reproduced 186 original evaluations
and ran 186 extended ones on inspected development data. It improved fixed-noise
graph p95 error factor from 1.05093 to 1.04275; density8 is 1.04002. Aggregate
p95 rankings were not reversed, inspected bridge predictions worsened, and
some new boundary selections persist. Full tuning adequacy remains unresolved.

A post hoc arithmetic feature-family selector, using training-only inner losses,
can choose the base or graph family. It selects density8 for p95 in all 31 folds
under both grids. This is not a test of every structural representation.

Earlier weaknesses include approximate-feature row dependence and original
motif-equivalence grouping; later stable features and merged groups address
them. Remaining limits include small/related program groups, unequal target
precision, timing-context assumptions, difficult-case censoring, retrospective
quality choices, repeated development use, sector scope and unproven usefulness.

The correct outcome is a checked exploratory study, not a settled rejection of
structural information or a publication-ready compiler method. The consumer gate
remains a scoped do-not-advance decision for the profiling proposal.

Next: use corrected claims in domain-expert scoping; require an actual decision
and accessible representative workload before a prospective comparison. No new
decoder calls, physical samples or reserved parents were used here. There were
372 outer model evaluations and 36 separate sklearn target-fit checks.
The diagnostic audit passed and all 15 previous snapshots remain unchanged.
