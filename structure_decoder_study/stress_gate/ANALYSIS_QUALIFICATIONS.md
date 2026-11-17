# Censoring and provenance qualifications

The frozen analysis correctly suppresses wall/CPU miss and p95 confidence intervals
for censored cases. One derived field, `logical_z_interval`, was inadvertently
populated even for stopped/censored samples. That interval must not be used as a
population accuracy bound. Reviewed copies of the summaries mask it and explicitly
label stopped-sample fractions/means as descriptive only. No timing data, model
coefficients, selection rule, or complete-case result is changed.

`review_results.py` creates those qualified copies, collects phase-specific noise
comparisons, and records a clock-only overhead diagnostic after timing. It does
not subtract overhead or refit any model. Primary frozen analysis files remain
available and their original hashes remain verifiable.

The confirmation dependency snapshot was recorded after launch following an import
failure; see `CONFIRMATION_PROVENANCE_NOTE.md`. The prefix declaration itself was
written before launch. No external preregistration or independent peer review is
claimed.

The statistics-enabled mechanism runs select slow shots. They cannot estimate
population cluster frequencies. Standalone BP/LSD replay includes separate API
boundaries and weight copying, so stage-time fractions are diagnostic proxies,
not an exact instrumented partition of the integrated API call. All combined
and instrumented corrections were checked against the integrated result.

The CPU cap sums measured API-call CPU, excluding construction, warmup, sampling,
and result checking. It is checked after a decode returns; one expensive native
call can overshoot the nominal cap. Partial data are retained. The cap is a
research resource limit, not a decoder execution timeout or a hardware guarantee.
