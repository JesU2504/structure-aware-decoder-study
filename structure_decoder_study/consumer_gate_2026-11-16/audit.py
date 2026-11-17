"""Audit against raw stored observations; no sampling, decoder import or fitting."""
from pathlib import Path
import hashlib
import json
import math
import statistics
import numpy as np
from scipy.stats import beta, binom

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
GATE = STUDY / "validation_gate_2026-11-13"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = read(ROOT / "replay.json")
    predictions = read(GATE / "bridge_predictions.json")
    corpus = {r["name"]: r for r in read(GATE / "corpus.json")}
    for relative, expected in result["sources"].items():
        assert sha(STUDY / relative) == expected, relative
    profile_cost, profile_upper, qualified = {}, {}, set()
    profile_files = evaluation_files = 0
    for name in corpus:
        wall, init, failures, evaluated = [], 0, 0, 0
        for session in range(3):
            p = GATE / "results" / f"session_{session}" / "profiling" / (name + ".npz")
            meta = read(p.with_suffix(".json"))
            assert sha(p) == meta["file_sha256"]
            with np.load(p) as data:
                wall.extend(int(v) for v in data["wall_ns"])
            init += meta["init_wall_ns"]
            profile_files += 1
            p = GATE / "results" / f"session_{session}" / "evaluation" / (name + "__whole30.npz")
            assert sha(p) == read(p.with_suffix(".json"))["file_sha256"]
            with np.load(p) as data:
                failures += int(data["logical_z_failure"].sum())
                evaluated += len(data["logical_z_failure"])
            evaluation_files += 1
        assert len(wall) == 192 and evaluated == 1536
        profile_cost[name] = sum(wall) + init
        rank = next(i for i in range(192) if binom.cdf(i, 192, .95) >= 1-.05/19)
        profile_upper[name] = sorted(wall)[rank]
        quality_upper = 1. if failures == evaluated else float(beta.ppf(1-.05/19, failures+1, evaluated-failures))
        if quality_upper <= .01:
            qualified.add(name)
    assert qualified == set(result["cohorts"]["retrospective_quality_screen_10"]["names"])
    assert len(qualified) == 10 and len(result["rows"]) == 108
    legacy = read(STUDY / "novelty_feasibility_2026-11-16/feasibility.json")
    for row in result["rows"]:
        names = result["cohorts"][row["cohort"]]["names"]
        budget, model = row["budget_ms"]*1e6, row["model"]
        selected = {n for n in names if predictions[n][model]["raw_ns"][1] <= budget}
        admitted = {n for n in selected if profile_upper[n] <= budget}
        assert selected == set(row["profiled_names"])
        assert admitted == set(row["admitted_names"])
        uniform = {n for n in names if profile_upper[n] <= budget}
        assert set(row["lost_uniform_admissions"]) == uniform-admitted
        overhead_key = "full_stable_ns" if "graph" in model else "base_density_ns"
        full = sum(profile_cost[n] for n in names)
        filtered = sum(profile_cost[n] for n in selected) + sum(
            corpus[n]["feature_timing"][overhead_key]+predictions[n][model]["median_inference_wall_ns"] for n in names)
        assert math.isclose(full/1e6, row["uniform_partial_ms"], abs_tol=1e-10)
        assert math.isclose(filtered/1e6, row["filter_partial_ms"], abs_tol=1e-10)
        if row["cohort"] == "all_19":
            previous = next(r for r in legacy["frozen_filter_controls"]
                            if r["budget_ms"] == row["budget_ms"] and r["model"] == model)
            assert set(previous["admitted_names"]) == admitted
            assert math.isclose(previous["partial_replay_wall_ms"], filtered/1e6, abs_tol=1e-10)
    training = read(STUDY / "learning_curves_2026-11-13/dataset.json")
    raw_service_by_source = dict(pilot=0, discovery=0)
    raw_samples_by_source = dict(pilot=0, discovery=0)
    label_files = 0
    for row in training:
        values = []
        for session in range(3):
            if row["source"] == "pilot":
                p = STUDY / "results" / f"session_{session}" / (row["name"] + ".npz")
                key = "latency_ns"
            else:
                p = STUDY / "stress_gate/results/discovery" / f"session_{session}" / (row["name"] + ".npz")
                key = "wall_ns"
            with np.load(p) as data:
                values.extend(int(v) for v in data[key])
            label_files += 1
        assert len(values) == row["shots"]
        assert math.isclose(sum(values)/len(values), row["targets"]["mean_ns"], rel_tol=1e-12)
        raw_service_by_source[row["source"]] += sum(values)
        raw_samples_by_source[row["source"]] += len(values)
    for row in result["historical_training_label_service"]:
        assert row["physical_samples"] == raw_samples_by_source[row["source"]]
        assert math.isclose(row["represented_decoder_wall_seconds"], raw_service_by_source[row["source"]]/1e9, rel_tol=1e-12)
    old = {r["name"]: r for r in read(STUDY / "corpus.json")}
    for component, saved in result["historical_original_construction"].items():
        values = [r[component] for r in old.values()]
        assert saved["records"] == len(values) == 78
        assert math.isclose(saved["total_ms"], sum(values)/1e6, abs_tol=1e-10)
        assert math.isclose(saved["median_ms"], statistics.median(values)/1e6, abs_tol=1e-10)
    original_metadata = [read(STUDY / "results" / f"session_{s}" / (name + ".json"))
                         for s in range(3) for name in old]
    for component, saved in result["historical_original_timing_metadata"].items():
        values = [r[component] for r in original_metadata]
        assert saved["records"] == len(values) == 234
        assert math.isclose(saved["total_ms"], sum(values)/1e6, abs_tol=1e-10)
        assert math.isclose(saved["median_ms"], statistics.median(values)/1e6, abs_tol=1e-10)
    assert len(result["potential_exact_circuit_cache_matches"]) == 3
    for match in result["potential_exact_circuit_cache_matches"]:
        before = STUDY / "circuits" / (match["original_name"] + ".stim")
        now = GATE / "circuits" / (match["bridge_name"] + ".stim")
        assert before.read_bytes() == now.read_bytes()
        assert sha(now) == match["circuit_sha256"]
        assert math.isclose(old[match["original_name"]]["circuit_build_ns"]/1e6,
                            match["historical_circuit_build_ms"], abs_tol=1e-10)
    at_two = next(r for r in result["rows"] if r["cohort"] == "all_19" and r["budget_ms"] == 2 and r["model"] == "linear_base6")
    illustrated = result["historical_illustrations"]
    build = sum(old[m["original_name"]]["circuit_build_ns"] for m in result["potential_exact_circuit_cache_matches"])/1e6
    assert math.isclose(build, illustrated["three_reference_circuit_build_ms"], abs_tol=1e-10)
    assert math.isclose(illustrated["fraction_if_only_three_historical_build_costs_are_added_to_both_ledgers"],
                        at_two["partial_saved_ms"]/(at_two["uniform_partial_ms"]+build))
    assert illustrated["batches_to_repay_represented_label_service_at_historical_partial_saving"] == math.ceil(
        sum(raw_service_by_source.values())/1e9/(at_two["partial_saved_ms"]/1000))
    assert all(r["profiled_cases"] == r["tasks"] for r in result["rows"] if r["budget_ms"] == 5)
    counts = {}
    paths = ["artifact_manifest.json", "artifact_manifest_2026-11-13.json",
             "artifact_manifest_2026-11-15.json", "artifact_manifest_2026-11-16.json",
             "validation_gate_2026-11-13/manifest.json", "supervisor_review_2026-11-16/manifest.json",
             "supervisor_review_2026-11-16/cross_domain_manifest.json",
             "novelty_feasibility_2026-11-16/manifest.json", "next_stage_design_2026-11-16/manifest.json"]
    for relative in paths:
        p = STUDY / relative
        entries = read(p)["files"]
        for name, expected in entries.items():
            assert sha(p.parent / name) == expected, (relative, name)
        counts[relative] = len(entries)
    contract = read(ROOT / "contract_assessment.json")
    assert contract["stage_0_complete"] and not contract["gate_0_passed"]
    record = dict(date="2026-11-16", passed=True, new_decoder_calls=0, new_model_fits=0,
        profile_files_checked=profile_files, independent_evaluation_files_checked=evaluation_files,
        training_label_files_checked=label_files, raw_training_samples_checked=sum(raw_samples_by_source.values()),
        raw_training_timed_service_seconds=sum(raw_service_by_source.values())/1e9,
        replay_rows_checked=len(result["rows"]), previous_manifests_verified=counts,
        replay_sha256=sha(ROOT / "replay.json"), audit_source_sha256=sha(Path(__file__)),
        note="Numerical/provenance verification; not external review or proof of statistical assumptions.")
    (ROOT / "audit.json").write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(json.dumps(record,indent=2))


if __name__ == "__main__":
    main()
