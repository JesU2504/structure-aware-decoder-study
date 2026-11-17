"""Zero-new-shot cost/decision replay of selective profiling and a simple filter."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
GATE = STUDY/"validation_gate_2026-11-13"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    analysis = read(GATE/"bridge_analysis.json")
    predictions = read(GATE/"bridge_predictions.json")
    corpus = {r["name"]:r for r in read(GATE/"corpus.json")}
    actual = {r["name"]:r for r in analysis["summaries"] if r["setting"] == "whole30"}
    model = "rbf_density8"
    model_overhead = sum(corpus[name]["feature_timing"]["base_density_ns"]+
                         predictions[name][model]["median_inference_wall_ns"] for name in actual)
    profile_service = {name:row["timed_decode_wall_ns"] for name,row in analysis["profiling"].items()}
    profile_init = {name:row["init_wall_ns"] for name,row in analysis["profiling"].items()}
    uniform_service = sum(profile_service.values())
    uniform_partial = sum(profile_service[name]+profile_init[name] for name in actual)
    rows = []
    for budget in sorted({r["budget_ms"] for r in analysis["budget_sweep"]}):
        truth = next(r for r in analysis["budget_sweep"] if r["budget_ms"] == budget and r["policy"] == "profile_upper")
        truths = {r["name"]:r for r in truth["details"]}
        choices = {}
        for policy in ("uniform_profile", "deadband", "filter_validate"):
            profiled, admitted, model_accepted = [], [], []
            for name in actual:
                raw = predictions[name][model]["raw_ns"][1]
                padded = predictions[name][model]["padded_ns"][1]
                if policy == "deadband" and padded <= budget*1e6:
                    admitted.append(name)
                    model_accepted.append(name)
                    continue
                if policy != "uniform_profile" and raw > budget*1e6:
                    continue
                profiled.append(name)
                upper = analysis["profiling"][name]["p95_upper_ns"]
                if upper is not None and upper <= budget*1e6:
                    admitted.append(name)
            metrics = dict(admitted=len(admitted), confident_false_admissions=0,
                 confident_conservative_rejections=0, qualified_admitted=0,
                 qualified_confident_false_admissions=0, qualified_confident_conservative_rejections=0,
                 unresolved_truths=0, unresolved_admissions=0, unqualified_admissions=0)
            for name, real in truths.items():
                ci = real["interval"]
                false = bool(ci and name in admitted and ci[0] > .05)
                rejection = bool(ci and name not in admitted and ci[1] < .05)
                qualified = actual[name]["screen_qualified"]
                unresolved = not ci or ci[0] <= .05 <= ci[1]
                metrics["confident_false_admissions"] += int(false)
                metrics["confident_conservative_rejections"] += int(rejection)
                metrics["qualified_admitted"] += int(qualified and name in admitted)
                metrics["qualified_confident_false_admissions"] += int(qualified and false)
                metrics["qualified_confident_conservative_rejections"] += int(qualified and rejection)
                metrics["unresolved_truths"] += int(unresolved)
                metrics["unresolved_admissions"] += int(unresolved and name in admitted)
                metrics["unqualified_admissions"] += int(not qualified and name in admitted)
            service = sum(profile_service[name] for name in profiled)
            initialization = sum(profile_init[name] for name in profiled)
            overhead = 0. if policy == "uniform_profile" else model_overhead
            partial = service+initialization+overhead
            choices[policy] = dict(**metrics, profiled_cases=len(profiled), profiled_shots=192*len(profiled),
                 profiled_names=profiled, admitted_names=admitted, unprofiled_model_accepts=model_accepted,
                 profile_decode_wall_ms=service/1e6, profile_init_wall_ms=initialization/1e6,
                 model_features_and_inference_ms=overhead/1e6,
                 partial_replay_wall_ms=partial/1e6,
                 profile_decode_wall_fraction=service/uniform_service,
                 partial_replay_fraction=partial/uniform_partial,
                 extra_exclusive_overhead_allowance_ms=(uniform_partial-partial)/1e6)
        uniform = set(choices["uniform_profile"]["admitted_names"])
        for policy, values in choices.items():
            selected = set(values["admitted_names"])
            values["same_admitted_set_as_uniform"] = selected == uniform
            values["uniform_admissions_lost"] = sorted(uniform-selected)
            values["extra_admissions_vs_uniform"] = sorted(selected-uniform)
        rows.append(dict(budget_ms=budget, policies=choices))
    frozen_filter_controls = []
    for row in rows:
        budget = row["budget_ms"]
        reference = set(row["policies"]["uniform_profile"]["admitted_names"])
        for control in sorted(next(iter(predictions.values()))):
            selected = [name for name in actual if predictions[name][control]["raw_ns"][1] <= budget*1e6]
            accepted = [name for name in selected if analysis["profiling"][name]["p95_upper_ns"] is not None
                        and analysis["profiling"][name]["p95_upper_ns"] <= budget*1e6]
            timing_key = "full_stable_ns" if "graph" in control else "base_density_ns"
            overhead = sum(corpus[name]["feature_timing"][timing_key]+
                           predictions[name][control]["median_inference_wall_ns"] for name in actual)
            partial = overhead + sum(profile_service[name]+profile_init[name] for name in selected)
            frozen_filter_controls.append(dict(budget_ms=budget, model=control, profiled_cases=len(selected),
                admitted=len(accepted), qualified_admitted=sum(actual[name]["screen_qualified"] for name in accepted),
                partial_replay_wall_ms=partial/1e6, same_admitted_set_as_uniform=set(accepted)==reference,
                uniform_admissions_lost=sorted(reference-set(accepted)), admitted_names=accepted))
    minima = []
    for cases, budgets in ((1,1), (19,1), (64,1), (64,9)):
        alpha = .05/(cases*budgets)
        minima.append(dict(configurations=cases, budgets=budgets, family_alpha=.05,
             per_bound_alpha=alpha, minimum_fixed_samples_for_finite_p95_upper=math.ceil(math.log(alpha)/math.log(.95))))
    result = dict(date="2026-11-16", new_decoder_calls=0, new_model_fits=0,
         development_only=True, configurations=19, parent_groups=7,
         model="frozen rbf_density8", median_costs_from_previous_context=True,
         scope="Recorded three-process profiling protocol and one feature/inference computation per task; partial cost only",
         omitted_costs=["shared circuit/DEM/matrix preparation", "profiling warmup", "training amortization", "different policy artifact demand"],
         model_filter_is_not_a_full_FTQC_or_distribution_shift_certificate=True,
         rows=rows, frozen_filter_controls=frozen_filter_controls, fixed_sample_count_reference=minima,
         input_hashes={str(p.relative_to(STUDY)):sha(p) for p in
             (ROOT/"FEASIBILITY_PROTOCOL.md",ROOT/"feasibility.py",GATE/"bridge_analysis.json",GATE/"bridge_predictions.json",GATE/"corpus.json")})
    (ROOT/"feasibility.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(at_2ms=next(r for r in rows if r["budget_ms"] == 2),
                          fixed_sample_count_reference=minima),indent=2))


if __name__ == "__main__":
    main()
