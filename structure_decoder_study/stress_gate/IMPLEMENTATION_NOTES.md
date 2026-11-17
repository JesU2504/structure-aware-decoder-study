# Implementation qualifications

- The initial source-fragment assembler passed literal circuit comparison for
  all 78 old inputs before new timing. The boundary module's first import attempt
  resolved the old pilot's `analyze.py` because the shared source loader changes
  sys.path. This was corrected with an explicit file-based import before boundary
  preparation or sampling. No boundary observations were collected by that failed
  attempt.
- The confirmation metadata import-name issue and actual late snapshot timing
  are documented separately. The model and measurement code were not changed.
- The installed ldpc Cython/generated C++ source includes a questionable
  zero-syndrome fast-path flag without an explicit initialization in the displayed
  function. This source observation is not a proof about the exact wheel build
  or an observed functional failure. All measured corrections, including zero
  syndromes, passed parity checks. We benchmark the pinned binary as observed,
  assume no particular zero-syndrome shortcut, and make no claim that the backend
  is formally verified. Future version/architecture reproduction should explicitly
  check this path and record any upstream fix in a separate campaign.
- Native LSD elapsed-counter units are not established by the installed binding
  files. Explicit Python CPU/wall clocks are used for timings; that raw counter
  is retained only as an uninterpreted diagnostic.
- The CPU clock may return zero for an empty sub-microsecond control due to
  quantization. The wall-clock wrapper overhead is recorded and not subtracted.
