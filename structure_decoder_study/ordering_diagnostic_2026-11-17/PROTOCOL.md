# Ordering diagnostic — 17 November 2026

Explain the stopped baseline reconstruction using the installed ldpc 2.4.1
sorting implementation and the same fixed 24 cached observations. No native
BP/OSD decode, physical sampling, stronger candidate search, model fit or source
patch is part of this diagnostic. The earlier headroom attempt stays stopped.

## Evidence before execution

The official PyPI 2.4.1 source archive was SHA256-verified; its OSD Cython wrapper
matches the installed wrapper byte for byte. The archive omits `sort.hpp` even
though `osd.hpp` includes it. A separate pinned GitHub reference is therefore
corroborative, not asserted to prove all wheel build inputs.

The installed binary exports `ldpc::sort::cmp`. Its disassembly compares the
first double in each record and returns zero for equal values. Its sorting
routine creates 16-byte records (double at offset0, int index at offset8),
initializes indices in ascending order, and calls the platform qsort. The
pinned reference implements that same pattern. NumPy's source reconstruction
instead explicitly uses a stable sort. No explicit secondary index key is
present in the native comparison.

## Frozen diagnostic

Freeze source/binary hashes, this protocol, diagnostic code and the prior
24-case selection before computing any new ordering. Use the exact installed
exported comparator via ctypes and the same process's system qsort on a
reviewed 16-byte C-compatible record. No C++ vector or decoder object layout
will be accessed. Verify struct size/alignment/field offsets, finite values,
ascending result and permutation coverage with controlled small arrays first.
Repeat each qsort ordering twice to check reproducibility in this environment.

Compare stable Python order with this native-sort-equivalent order for all24
cached float64 LLR vectors. Derive ordering solely from implementation and
LLRs, never logical labels or rescue outcomes. Never try alternative tie orders
until one produces a preferred correction.

For each order, call the pinned pure-Python baseline reconstruction. The source
API accepts values used only for ordering; supply explicit unique rank priorities
for the native-derived order and assert the returned ordering equals it exactly.
This is a declared ordering adapter, not modified BP beliefs and not a new decoder.

Validate every reconstructed baseline against all1800 detector equations,
independent rank1794 of its pivot columns, and its cached native correction.
Record differing columns, tie groups and baseline equality. Check all 24 cases
without dropping mismatches; none of these checks authorizes a 1FV search.

Run the ctypes probe in a child process with a 120-second wall timeout; a crash
or ABI/adaptor discrepancy stops this diagnostic. No assumptions extend beyond
the recorded macOS arm64 binary/libc environment. Retain all outputs and audit
them independently. A match demonstrates that the implementation-derived
ordering suffices on this fixed panel; it does not reveal the decoder object's
hidden pivot set or establish arbitrary-version/platform equivalence.
