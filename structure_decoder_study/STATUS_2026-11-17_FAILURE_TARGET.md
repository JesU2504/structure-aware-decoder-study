# Failure target selected conditionally — 17 November 2026

See [the target decision](failure_target_2026-11-17/TARGET_DECISION.md) and
[entry protocol](failure_target_2026-11-17/ENTRY_PROTOCOL.md).

The user delegated the choice of decoder failure. Prefer a documented low-weight
logical decoding failure in circuit-level BB144 memory as a diagnostic target.
Exact failure reproduction and a distinct publication question remain gates.
This is not a claim that BP+LSD shares published RelayBP/ImpulseBP/ELMS failures.

A bounded pinned-generator probe verified CSS/logical conditions, noiseless
behavior and detector/observable reconstruction: 32 noiseless circuit samples
and 256 DEM validation samples; zero decoder calls or training samples.

The probe preserved one failed check: the public helper adds priors for duplicate
fault signatures, while exact independent-event parity merging differs on 1,584
of 8,784 columns (max relative difference 0.150808%). Independent saved-artifact
checks confirm the discrepancy; its effect on decoding is unknown. The other
19 checks pass. Prior study conversion already uses exact parity merging.

All six public repository commit trees were inspected, without locating an exact
labeled BB144 failure witness. Public generator access is established; exact
published-failure replay is not. Public RelayBP and adaptive qLDPC decoder
repositories were located, but neither was installed or executed in this check.

Important overlap: structural error-floor estimation and risk-guided adaptive
post-processing already exist. Reproducing a failure is a baseline, not novelty.
Do not start a large training or enumeration campaign before a specific unanswered
correctness–cost question and reproducible witnesses are available.

The independent audit verified all 16 prior result manifests unchanged. No
manuscript draft or reserved evaluation was produced or used.
