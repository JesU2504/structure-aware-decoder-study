# Clarification after the cross-domain-methods question

16 November 2026. Read the separate AI supervisor's
[cross-domain addendum](supervisor_review_2026-11-16/cross_domain_addendum.md).
The earlier review and all frozen artifacts are preserved.

The reviewer explicitly agrees that transferring an established method can be
a legitimate publishable contribution without inventing a new ML algorithm.
Its earlier emphasis on a distinctive method and placement-ranking benefit was
too narrow if interpreted as a mandatory form of novelty. A strong base model
can be a component of a useful transferred system. Always-burst only trivializes
current ranking; absolute budget/capacity prediction remains a possible consumer.

The leading imported idea is decision-sensitive calibration/selective profiling
from performance engineering and database optimization: use a cheap cost model
first, and spend actual measurement effort where it can change a resource
decision. The prospective contribution is QEC-specific adaptation and independently
validated decision/cost value, not a new regressor or a renamed known algorithm.
Priority for the specific application remains unestablished.

The reviewer made a post hoc zero-new-shot, zero-fit replay on existing data.
At the diagnostic 2 ms budget, one raw/padded/profile rule matches uniform
profiling's admitted set while profiling ten of nineteen configurations. It uses
39.49% of recorded profiling decoder-call wall service, excluding setup, warmup,
feature/inference, and training costs. The full inherited budget sweep and its
disagreements are retained. Historical padding is not a confidence interval and
has no inherited noise-shift safety guarantee; no deployment or system speedup
claim is supported by this replay.

The immediate next work is the bounded existing-data replay/cost/sensitivity
audit for this one hypothesis, including strong simple controls. A particularly
important control is a model-as-filter policy that profiles every proposed
admission, rather than allowing historical padding alone to accept it. Its
profiling-cost and lost-feasible-admission tradeoff would need evaluation under
the same sampling assumptions. This control is a coordinating-assistant
recommendation, not an already validated policy.

If credible headroom survives, freeze an independent admission study tailored
to the actual consumer. Do not automatically run the previous sixteen-parent
placement/mean trial. The added-graph p95 hypothesis remains unsupported, and
no new decoder measurement or model fit was performed for this addendum.
