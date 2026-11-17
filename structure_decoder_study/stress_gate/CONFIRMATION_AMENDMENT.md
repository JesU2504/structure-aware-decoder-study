# Fixed-prefix safeguard before fresh confirmation

13 November 2026, after discovery analysis and **before** confirmation sampling.
The original protocol and full-run analysis remain unchanged.

Discovery includes one CPU-censored large task. The selected confirmation set
also includes a large task for which 1,000 calls may reach the existing CPU cap.
To preserve a valid fixed-sample risk diagnostic if a later portion is censored,
add an explicitly secondary analysis of the **first 256 shots of each of the
three fresh sessions** for every selected case. The prefix length is fixed now,
before its outcomes are collected. Do not use arbitrary stopped sample lengths
to claim binomial coverage.

If any session ends before 256 calls, label that case insufficient for the
prefix analysis. For complete prefixes, report pooled exact-binomial intervals
with alpha=0.05/6 and session intervals with alpha=0.05/18, under the same IID/
measurement-context qualifications as the primary analysis. Inclusion requires
having observed the fixed prefix; do not claim conditional coverage given
completion or generalize to a population of programs. Keep all selected cases,
including incomplete cases, in the reporting family.

This does not make censored full-run means or p95 estimates unbiased. The full
1,000-shot target, CPU cap, model coefficients, six selected cases, and primary
analysis are unchanged. Prefix confirmation is labeled secondary and adversarial.
