# Expert response to supervisor review

17 November 2026. Accepted: **conditional GO for interface and baseline
feasibility only**. Decoder-performance and publication claims remain on hold.
No additional literature search, code change or experiment was performed.

Three requirements must be satisfied before any future pilot:

1. **Separate the baseline identities.** With one history state and beta=0.5,
   the proposed update is ordinary damping, not vanilla BP. Provide an explicitly
   disabled mode reproducing vanilla BP, a separate fixed-damping control, and
   a documented identity for the AA fallback step. Do not use a zero-history
   test as proof that all these modes coincide.
2. **Freeze safeguard-probe semantics and costs.** Declare before execution
   whether a valid syndrome found at a probe is eligible for return, its
   chronological priority, and the same candidate policy for controls. Count
   every F evaluation, including rejected probes; otherwise an apparent gain
   could come from extra work or an undeclared candidate ensemble.
3. **Use controls appropriate to the claim.** A same-map ordinary DIIS or
   unsafeguarded-history comparator is required before attributing any benefit
   specifically to safeguards. TEMPO-BP is a close comparator before claiming
   a competitive decoder method. Access to a genuinely untouched confirmation
   workload is not yet verified and must remain an explicit prerequisite.

The proposal remains a QEC-specific numerical-analysis hypothesis with high
novelty risk. Existing generic BP+DIIS and classical ADMM+Anderson results are
acknowledged. Passing interface checks would permit designing a bounded pilot;
it would not itself demonstrate decoder improvement or publication novelty.
