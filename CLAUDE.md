# Instructions for Claude Code

## Mission

Help develop a credible, publishable quantum-error-correction research result.
Publication is the objective, not an established outcome. Prefer a useful,
defensible finding over a complicated method or a positive-looking benchmark.
The user wants careful execution, explicit failure analysis and independent
review. Do not start a manuscript yet.

## Read before changing anything

1. [Research handoff](docs/RESEARCH_HANDOFF.md): motivation, evidence, hypotheses,
   limitations and publication criteria.
2. [Experiment ledger](docs/EXPERIMENT_LEDGER.md): what ran, what failed and what
   remains inconclusive.
3. [Next task](docs/NEXT_TASK.md): bounded optimizer-adapter integration.
4. The linked protocols, source and AI reviews relevant to your intended change.

The latest state is **passing runner core, failed earlier native entry,
inconclusive real research probes**. These are different claims. Historical
documents describe earlier checkpoints; this handoff explains their order.

## Working rules

- Preserve frozen code, data, protocols and failed results. Implement changes
  in a new versioned directory. Never rewrite an old outcome or resume a
  stopped experiment to obtain a pass.
- Verify this public snapshot with `tools/verify.py` and
  `tools/verify_progress.py`; these make no optimizer/decoder/worker calls.
  Install only the dependencies required for your task and record the actual
  imported environment. Public paths and text were sanitized: use PUBLIC_EXPORT.json
  for mirror checks, not historical machine-specific hashes.
- Before computation, specify the hypothesis, controls, frozen inputs/options,
  resource budget, attempt count, acceptance criteria and stopping rule.
  Separate exploratory development from fresh confirmation.
- Review concrete code before launching a bounded experiment and audit the
  saved evidence afterward. Use a separate reviewer/agent if available;
  identify AI review honestly. Same-agent rereading is not independent review.
- Count failed/interrupted starts and all additional optimization. Zero new
  BP/OSD/LSD calls does not mean zero decoding-related computation.
- For lengthy authorized jobs, background them with durable logs/progress and
  check about every20 minutes. Resource watchdogs remain continuous; background
  execution never extends scientific budgets. Check short-job completion promptly.
- Do not change scores, noise, task, cases, tie rules, training or budgets after
  observing results without a new explicit versioned design. Preserve all attempts.
- Keep updates understandable. Report what changed, checks, actual counts,
  failures, limitations and the next decision. Do not promise publication.

## Current scope

The next engineering task is integrating the validated kernel-owned runner with
the raw-first optimizer adapter, then a fresh bounded nonresearch entry.
Do not automatically rerun cases131/228, train models, generate more noise,
revive the original compiler claim or draft a paper. Runner success does not
resolve the scientific-value gate for another real solve.

When asked to publish updates, use a curated sanitized project export. Exclude
credentials, private directories, environments, installed binaries and unrelated
workspace content. Preserve failures and verify the remote commit. Current
public visibility is intentional; do not change it without instruction.
