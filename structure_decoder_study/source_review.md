# Source entry review

Public source: `basilthebeagles/tmcbs`, pinned commit
`c0490fa63965d8984cca89deb8826c19c46e8a3c` (10 September 2026).
Original archive and file hashes are retained under `sources/` and in
`source_manifest.json`. Third-party source is unmodified.

## Verified capabilities

- Normal `import tmcbs` works from the pinned snapshot with existing dependencies.
  Decoder backends are lazy imports; no package-initializer bypass or mocked
  dependency is needed. Tesseract is not installed or used.
- `make_builder` exposes explicit multi-block surface-code circuit construction.
- A direct public local-CNOT example at d=3 and p=0.001 constructs a 64-detector,
  245-mechanism matrix with 512 nonzeros and maximum detector arity 4.
- Upstream `test_codes.py` and `test_experiments.py` ran normally under pytest:
  **39 passed in 172.86 seconds**. These include published matrix-size references,
  circuit construction checks, and logical-Z / logical-X truth-table tests for
  the upstream non-local CNOT paths. These tests alone do not verify every custom
  circuit or its full fault-tolerance properties.

## Scientific restrictions found by inspection

`tmcbs/general_circuit_builder_surface.py` declares detectors for the Z ancilla
measurements in `extractionRound`. It subsequently measures X ancillas without
declaring the corresponding X-check detectors. Final `obsOffset` reads stored
logical Z operators. Stage 1 therefore uses a single detector sector and a
logical-Z output metric. Phase errors outside that metric are not full logical
success. A complete two-sector experiment and realistic window handling are
required before making the proposed broad FTQC compilation claim.

The public decoder helper defaults to 10,000 BP iterations and a nonzero
postprocessing order. Stage 1 explicitly uses a different fixed BP+LSD-0
configuration; it does not reproduce the paper's performance results.

## Converter review

The vendored `dem_to_check_matrices` converter represents target sets using
`frozenset` and adds priors for duplicate complete supports. For independent
duplicate Bernoulli events, exact parity combination uses p1+p2-2*p1*p2. Repeated
targets across separator hints also need modulo-2 treatment. The independent
adapter in `study.py` tests these cases without changing upstream source.

`validation.json` records whether the independent adapter and upstream converter
actually differ on the generated corpus. A synthetic edge-case discrepancy is
not evidence that the associated publication's results are wrong.

## Operational restrictions

Only the existing workspace environment is read; no dependencies are installed
into it. CPU: Apple M1 Pro, 10 cores, 16 GiB RAM, arm64 macOS. Thread environment
variables are fixed to one. The CPU has heterogeneous cores; explicit core
pinning is not provided by this macOS harness. Independent randomized sessions
measure some operational variation, but do not replace a later controlled server
benchmark. No hardware-decoder, hard real-time, memory-budget, or end-to-end
queueing claims follow from this pilot.
