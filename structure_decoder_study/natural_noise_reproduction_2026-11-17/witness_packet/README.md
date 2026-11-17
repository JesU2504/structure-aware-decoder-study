# Reproducible natural-noise logical failure: case 23

This packet contains one audited BB144 Z-memory observation from the public
24-round, p=0.007 source circuit. Seed 2026111731, zero-based sample index 23,
Stim 1.16.0. The circuit extracts Z checks only.

With ldpc 2.4.1 BP20+OSD0, the returned correction satisfies all detectors but
misidentifies six of the twelve logical-Z observable bits. It was reproduced
on a fresh decoder in the experiment's predeclared replay phase. The saved
call files include primary, controls, fresh replays and forced comparisons.
See `packet.json` for configurations, versions, file hashes and call IDs.

`observation.npz` contains the cached syndrome and simulator logical labels.
These labels are for external scoring, not decoder input. No unique raw DEM
event support or physical gate-fault support is asserted for this observation.

For manual replay, use the pinned environment, change to this packet directory,
and run the following Python. This snippet is provided for convenience; the
recorded fresh-instance replay is the executed verification for this milestone.
The final saved-output audit made no additional decoder calls.

```python
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"

import numpy as np
from scipy.sparse import load_npz
from ldpc import BpOsdDecoder

h = load_npz("H.npz").tocsr()
l = load_npz("L.npz").tocsr()
p = np.load("priors.npy")
shot = np.load("observation.npz")
decoder = BpOsdDecoder(
    h, error_channel=p.tolist(), max_iter=20,
    bp_method="ms", ms_scaling_factor=0.625, schedule="parallel",
    omp_thread_count=1, random_schedule_seed=0,
    input_vector_type="syndrome", osd_method="OSD_0", osd_order=0,
)
correction = decoder.decode(shot["syndrome"]).copy()
print("syndrome residual:", np.count_nonzero(h @ correction % 2 != shot["syndrome"]))
print("wrong logical bits:", np.count_nonzero(l @ correction % 2 != shot["actual"]))
# Recorded expected result: syndrome residual 0, wrong logical bits 6.
```

A future successful repair of this observation would demonstrate that one
recovery only. The packet establishes neither bounded-distance decoding nor a
new method, a hardware deadline, or a compiler scheduling improvement.
