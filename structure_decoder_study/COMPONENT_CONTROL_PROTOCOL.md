# Post hoc paired connected-component control

Motivation: the primary feature model did not improve held-out prediction, but
the corpus includes fanout/repeated pairs with exactly equal dimensions, nonzeros,
prior sums, and expected detector activity. They differ in component structure.
Before treating this as novel topology-dependent cost, test the standard remedy
of independently decoding disconnected components.

This is a post hoc diagnostic, not a replacement confirmatory experiment. Freeze
this protocol and the control implementation before collecting its fresh data.

Use all 18 fanout/repeated cases (d=3,5,7; early/spread/late). Retain the same physical
circuits, noise, matrix convention, BP/LSD parameters, hardware, and one-sector
limitations. Use three randomized serial sessions, each with 1,000 fresh physical
shots per case and a distinct component-control seed namespace. Both execution
forms receive exactly the same syndromes. Warm each decoder on 32 separate shots.

Joint: decode the complete H as in the primary campaign.
Split: find connected components of the bipartite H graph, construct a decoder
for each nonempty detector/fault component, and sum sequential per-component API
service times. No parallelism or zero-syndrome bypass is added. Logical-only
variables use their independent MAP value; priors in this corpus are below 0.5.
Preserve global within-component row/column ordering. Alternate execution-form
order per shot. Assemble corrections and evaluate logical outputs outside timing.

Report paired mean and p95 service, iteration-weighted nonzero work, all syndrome
consistency checks, and logical-Z failures for both forms. Independent-component
factorization does not guarantee identical heuristic decoder accuracy; do not
hide or assume away differences. Single-component fanout cases are timing controls.
Component preparation and matrix conversion are excluded from warm service but
must be reported as setup costs.

Save raw paired observations and correction checkpoints, plus implementation and
protocol hashes. Do not interpret improved componentwise execution as a new
decoder algorithm or an original decomposition method. If it explains the mean
differences, prioritize a simple decomposition-aware baseline in any future paper.
