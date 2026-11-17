"""Design arithmetic from frozen records; not experiments or fitted results."""
from pathlib import Path
import hashlib
import json
import math
from scipy.stats import beta, binom

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent


def read(path):
    return json.loads(path.read_text())


def main():
    feasibility_path = STUDY / "novelty_feasibility_2026-11-16/feasibility.json"
    summary_path = STUDY / "validation_gate_2026-11-13/model_summary.json"
    dataset_path = STUDY / "learning_curves_2026-11-13/dataset.json"
    feasibility, summary, dataset = map(read, (feasibility_path, summary_path, dataset_path))
    at_two = next(r for r in feasibility["rows"] if r["budget_ms"] == 2)
    linear = next(r for r in feasibility["frozen_filter_controls"]
                  if r["budget_ms"] == 2 and r["model"] == "linear_base6")
    uniform_ms = at_two["policies"]["uniform_profile"]["partial_replay_wall_ms"]
    saved_ms = uniform_ms - linear["partial_replay_wall_ms"]
    # Illustrative sample planning. The consumer contract is intentionally open.
    tasks, contexts, looks = 32, 3, 4
    profiling_alpha, evaluation_alpha, quality_alpha = .02, .02, .01
    profiling_cell_alpha = profiling_alpha / (tasks * contexts * looks)
    evaluation_cell_alpha = evaluation_alpha / (tasks * contexts)
    quality_cell_alpha = quality_alpha / (tasks * contexts)
    power = []
    for n in (512, 1024, 2048, 4096):
        # Exact two-sided Clopper-Pearson classification at the fixed endpoint.
        accepted_counts = [k for k in range(n + 1)
                           if (1. if k == n else beta.ppf(1-evaluation_cell_alpha/2, k+1, n-k)) <= .05]
        rejected_counts = [k for k in range(n + 1)
                           if (0. if k == 0 else beta.ppf(evaluation_cell_alpha/2, k, n-k+1)) > .05]
        max_accept, min_reject = max(accepted_counts, default=-1), min(rejected_counts, default=n+1)
        power.append(dict(samples_per_task_context=n, accept_if_misses_at_most=max_accept,
            reject_if_misses_at_least=min_reject,
            probability_resolve_feasible_when_true_miss_0_03=float(binom.cdf(max_accept, n, .03)),
            probability_resolve_infeasible_when_true_miss_0_07=float(binom.sf(min_reject-1, n, .07))))
    result = dict(date="2026-11-16", design_only=True, new_decoder_calls=0, new_model_fits=0,
        actual_contract_unresolved=True,
        recovered_cost_inventory=dict(uniform_partial_ms=uniform_ms,
            linear_filter_partial_ms=linear["partial_replay_wall_ms"], linear_partial_saved_ms=saved_ms,
            historical_entire_model_job_wall_seconds=summary["elapsed_seconds"],
            historical_outer_fits=summary["outer_models"], training_examples=len(dataset),
            training_parent_groups=len({r["group"] for r in dataset}),
            warning="Full historical model-job time is neither deployment linear-fit cost nor training-label acquisition cost; do not use it as either.",
            unknown_costs=["training-label acquisition needed by a deployed model", "target-context calibration",
                "circuit/DEM/matrix preparation", "sampling", "profiling warmup", "pipeline I/O and startup",
                "actual base6-only feature cost", "deployment fitting/tuning", "cache-hit and invalidation behavior"]),
        parent_level_zero_failure_limits=[dict(independent_parents=n,
            one_sided_95_upper_failure_probability=1-.05**(1/n)) for n in (8, 12, 16, 32, 59, 60)],
        illustrative_fixed_family=dict(tasks=tasks, contexts=contexts, profiling_looks=looks,
            profiling_alpha=profiling_alpha, evaluation_alpha=evaluation_alpha, quality_alpha=quality_alpha,
            profiling_cell_two_sided_alpha=profiling_cell_alpha,
            evaluation_cell_two_sided_alpha=evaluation_cell_alpha,
            quality_cell_two_sided_alpha=quality_cell_alpha,
            minimum_zero_miss_profile_samples_to_certify_5_percent=math.ceil(math.log(profiling_cell_alpha/2)/math.log(.95)),
            minimum_zero_failure_quality_samples_to_certify_1_percent=math.ceil(math.log(quality_cell_alpha/2)/math.log(.99)),
            reference_resolution_power=power,
            warning="IID/stable-context calculations only; assumptions, target rates, task counts and sample counts are not an approved consumer contract."),
        inputs={str(p.relative_to(STUDY)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (feasibility_path, summary_path, dataset_path, Path(__file__))})
    (ROOT / "planning_calculations.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(recovered=result["recovered_cost_inventory"],
        parent_level_limits=result["parent_level_zero_failure_limits"],
        sample_planning=result["illustrative_fixed_family"]),indent=2))


if __name__ == "__main__":
    main()
