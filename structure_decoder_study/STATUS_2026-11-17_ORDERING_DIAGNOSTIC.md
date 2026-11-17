# Ordering diagnostic completed — 17 November 2026

See [results](ordering_diagnostic_2026-11-17/RESULTS.md),
[protocol](ordering_diagnostic_2026-11-17/PROTOCOL.md) and
[audit](ordering_diagnostic_2026-11-17/audit.json).

The exact installed comparator plus platform qsort, using the implementation's
record layout and ascending initial indices, reproduced all24 cached native
corrections. Stable Python order reproduced23, with case51 the sole mismatch.
Independent validation checks the differences occur only inside exact LLR ties,
all1800 syndrome equations, pivot ranks and old snapshot integrity.

No new native decoder/BP calls, shots or candidate searches were performed.
The original stable-branch headroom experiment stays stopped. The result accounts
for its observed ordering incompatibility on this fixed macOS arm64 panel,
without claiming hidden-pivot or general platform equivalence, a logical rescue,
compiler benefit or publication novelty.
