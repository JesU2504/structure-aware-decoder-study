# Ordering discrepancy accounted for — 17 November 2026

**The implementation-derived ordering reproduces all 24 cached native OSD0
corrections. Stable Python ordering reproduces 23; only case 51 differs.**
No BP/OSD decode, physical sample or stronger 1FV search was run in this diagnostic.
The previously stopped headroom experiment remains preserved and stopped.

The PyPI ldpc2.4.1 archive was verified against its official SHA256. Its OSD
Cython wrapper matches the installed wrapper exactly. The archive omits the
sort header, so a separately pinned upstream reference and the installed binary
were inspected rather than pretending the archive proves all build inputs.

The binary's exported comparator ignores the index when reliability values tie.
Its sorting function constructs 16-byte double/index records and invokes platform
qsort. The diagnostic used that exact installed comparator and process libc
qsort with verified size, alignment and field offsets. It did not access a C++
vector or decoder object. Controlled ABI/comparator probes passed.

The comparator-derived order was computed twice per case and was repeatable in
this environment. Unique rank priorities supplied that explicit order to the
unchanged Python baseline reconstruction; the priorities were only an ordering
adapter, not modified BP beliefs. The rule came from the implementation before
outcomes, with no tie-permutation search or access to actual logical labels.

An independent saved-output audit checked both orders, all1800 syndrome equations,
rank1794 of every information set, and exact cached correction equality. The
two orderings differ only within exact reliability ties. All twenty previous
result manifests remain unchanged.

This accounts for the observed case-51 compatibility problem on the fixed
panel: preserving the native implementation's tie order restores its correction.
It does not reveal hidden native pivot sets, prove arbitrary-platform/version
equivalence, repair a logical failure or establish a new method. Native qsort
tie behavior is not a portable stable-sort contract.

A future headroom experiment using this implementation-derived ordering would
have an explicitly different adapter from the published stable-order Python
branch. It needs its own declared target and checks; this result does not
retroactively pass or resume the earlier frozen experiment.
