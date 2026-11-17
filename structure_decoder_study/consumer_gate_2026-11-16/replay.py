"""Read-only consumer-gate cost recovery and development sensitivity replay."""
from pathlib import Path
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
GATE = STUDY / "validation_gate_2026-11-13"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    analysis = read(GATE / "bridge_analysis.json")
    predictions = read(GATE / "bridge_predictions.json")
    corpus = {x["name"]: x for x in read(GATE / "corpus.json")}
    old = read(STUDY / "corpus.json")
    training = read(STUDY / "learning_curves_2026-11-13/dataset.json")
    actual = {x["name"]: x for x in analysis["summaries"] if x["setting"] == "whole30"}
    cohorts = dict(all_19=list(actual), retrospective_quality_screen_10=[n for n in actual if actual[n]["screen_qualified"]])
    costs = {n: x["timed_decode_wall_ns"] + x["init_wall_ns"] for n, x in analysis["profiling"].items()}
    rows = []
    for label, names in cohorts.items():
        baseline = sum(costs[n] for n in names)
        for budget in sorted({r["budget_ms"] for r in analysis["budget_sweep"]}):
            uniform = {n for n in names if analysis["profiling"][n]["p95_upper_ns"] <= budget * 1e6}
            for model in sorted(next(iter(predictions.values()))):
                selected = [n for n in names if predictions[n][model]["raw_ns"][1] <= budget * 1e6]
                admitted = {n for n in selected if n in uniform}
                key = "full_stable_ns" if "graph" in model else "base_density_ns"
                overhead = sum(corpus[n]["feature_timing"][key] + predictions[n][model]["median_inference_wall_ns"] for n in names)
                partial = sum(costs[n] for n in selected) + overhead
                rows.append(dict(cohort=label, budget_ms=budget, model=model, tasks=len(names),
                    profiled_cases=len(selected), profiled_names=selected,
                    uniform_admitted=len(uniform), admitted=len(admitted), admitted_names=sorted(admitted),
                    lost_uniform_admissions=sorted(uniform-admitted),
                    uniform_partial_ms=baseline/1e6, filter_partial_ms=partial/1e6,
                    partial_saved_ms=(baseline-partial)/1e6, partial_saved_fraction=1-partial/baseline))
    construction = {}
    for component in ("circuit_build_ns", "dem_build_ns", "convert_ns"):
        values = [x[component] for x in old]
        construction[component] = dict(records=len(values), minimum_ms=min(values)/1e6,
            median_ms=statistics.median(values)/1e6, maximum_ms=max(values)/1e6, total_ms=sum(values)/1e6)
    historical_setup = {}
    metadata = [read(STUDY / "results" / f"session_{s}" / (row["name"] + ".json"))
                for s in range(3) for row in old]
    for component in ("decoder_init_ns", "sampling_ns", "decode_loop_wall_ns"):
        values = [row[component] for row in metadata]
        historical_setup[component] = dict(records=len(values), median_ms=statistics.median(values)/1e6,
                                           total_ms=sum(values)/1e6)
    matches = []
    for name in actual:
        digest = sha(GATE / "circuits" / (name + ".stim"))
        for row in old:
            if digest == row["circuit_sha256"]:
                matches.append(dict(bridge_name=name, original_name=row["name"], circuit_sha256=digest,
                    historical_circuit_build_ms=row["circuit_build_ns"]/1e6,
                    historical_dem_build_ms=row["dem_build_ns"]/1e6,
                    historical_conversion_ms=row["convert_ns"]/1e6))
    labels = []
    for source in sorted({r["source"] for r in training}):
        subset = [r for r in training if r["source"] == source]
        labels.append(dict(source=source, rows=len(subset), physical_samples=sum(r["shots"] for r in subset),
            represented_decoder_wall_seconds=sum(r["shots"]*r["targets"]["mean_ns"] for r in subset)/1e9))
    selected_row = next(r for r in rows if r["cohort"] == "all_19" and r["budget_ms"] == 2 and r["model"] == "linear_base6")
    build_ms = sum(m["historical_circuit_build_ms"] for m in matches)
    label_seconds = sum(r["represented_decoder_wall_seconds"] for r in labels)
    result = dict(date="2026-11-16", post_hoc_development_only=True, new_decoder_calls=0, new_model_fits=0,
        cohorts={k:dict(tasks=len(v), names=v) for k,v in cohorts.items()}, rows=rows,
        historical_original_construction=construction, historical_original_timing_metadata=historical_setup,
        original_sampling_cost_excludes_warmup=True,
        original_loop_cost_includes_timed_decode_service_and_correction_diagnostics=True,
        potential_exact_circuit_cache_matches=matches,
        exact_match_is_not_proof_of_valid_performance_cache=True,
        historical_training_label_service=labels,
        historical_illustrations=dict(
            three_reference_circuit_build_ms=build_ms,
            filter_saved_ms_at_2ms=selected_row["partial_saved_ms"],
            fraction_if_only_three_historical_build_costs_are_added_to_both_ledgers=
                selected_row["partial_saved_ms"]/(selected_row["uniform_partial_ms"]+build_ms),
            represented_training_service_seconds=label_seconds,
            batches_to_repay_represented_label_service_at_historical_partial_saving=
                math.ceil(label_seconds/(selected_row["partial_saved_ms"]/1000)),
            warning="Cross-context arithmetic only; neither a measured end-to-end speedup, optimized-compiler bound, minimum training cost nor demonstrated deployment break-even."),
        sources={str(p.relative_to(STUDY)):sha(p) for p in
            (ROOT/"PROTOCOL.md",Path(__file__),GATE/"bridge_analysis.json",GATE/"bridge_predictions.json",GATE/"corpus.json",
             STUDY/"corpus.json",STUDY/"study.py",STUDY/"learning_curves_2026-11-13/dataset.json")})
    (ROOT / "replay.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(linear_2_and_5=[r for r in rows if r["model"] == "linear_base6" and r["budget_ms"] in (2,5)],
                         historical_illustrations=result["historical_illustrations"],training_labels=labels),indent=2))


if __name__ == "__main__":
    main()
