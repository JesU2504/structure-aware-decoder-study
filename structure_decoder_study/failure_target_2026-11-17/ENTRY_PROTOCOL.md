# Failure-target entry check — 17 November 2026

This is an exploratory workload-access check. It is not a manuscript, a new
decoder proposal, or a reserved evaluation. The user delegated the choice of
failure type. Prefer a documented circuit-level low-weight decoding failure
over a deadline selected after inspecting measured times.

## Candidate and limits

Candidate: the Z-memory detector sector of the BB [[144,12,12]] circuit, using
the published `dem_trapping_sets` generator at commit
`b9ac6a1133e1db71a99d253e523ebca524117142`, 12 extraction rounds, p=0.001,
default `z_basis=True, use_both=False, HZH=False`.

The code's label is not our proof of circuit distance. A generator probe is not
a reproduction of a published decoding failure. Published failures of RelayBP,
ImpulseBP, or ELMS must not be attributed to our existing BP+LSD backend.
The exact published circuit, column ordering, priors, observable map, decoder
configuration and randomization still require matching.

## Bounded construction probe (declared before source execution)

- Verify all five downloaded files against their SHA256 manifest. Review imports
  and the called construction/conversion functions before importing them.
- Use the documented helper functions directly. Do not import the enumeration
  entry point or build/invoke the C++ trapping-set enumerator.
- Build only the candidate above, plus the same circuit with noise removed.
  Check CSS commutation, logical commutation and independence using a separate
  GF(2) rank routine. Do not trust the helper's `D` attribute as distance.
- Extract the un-decomposed Stim DEM. Convert it independently with parity
  semantics. Compare H, L and priors against the repository converter, preserving
  its column IDs; report duplicate-signature or conversion discrepancies.
- Validate 32 noiseless detector samples and 256 DEM samples with returned fault
  vectors, checking H e = syndrome and L e = observable flips. These are
  validation samples, not training data, decoder trials or physical Monte Carlo
  error-rate estimates. Preserve seeds, artifact hashes, environment and results.
- Allow at most 90 seconds for the probe. No decoding, training, exhaustive
  enumeration, new package installation or existing-result mutation is allowed.

## Entry decision

Construction checks alone can pass the generator-access gate. The exact-failure
reproduction gate remains open until at least one labeled fault support is tied
to the precise DEM and decoder configuration, and replayed with independently
checked syndrome and logical outcomes. Absence of a witness in an inspected
repository is an access gap, not evidence against the paper.

Before any later performance study, distinguish nonconvergence (H e_hat != s)
from a syndrome-valid logical error (H e_hat = s but L e_hat != L e). Include
successful matched controls, all attempted runs and iteration-limit sensitivity.
Ground-truth fault supports may select stress cases, but are unavailable to a
compiler or online decoder. Static circuit features cannot distinguish shots
from the same DEM. Enriched injections cannot estimate natural-noise failure
rates or latency quantiles without a separate justified sampling design.

No method-level novelty is assumed. Structural error-floor analysis and
instance-adaptive post-processing are existing work. A later experiment requires
a specific unanswered question and appropriate strong baselines first.
