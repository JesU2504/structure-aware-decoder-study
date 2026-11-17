"""Independent read-only verification; no sampling, decoder calls or model fits."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from scipy.stats import binom

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
GATE = STUDY / "validation_gate_2026-11-13"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = read(ROOT / "feasibility.json")
    analysis = read(GATE / "bridge_analysis.json")
    predictions = read(GATE / "bridge_predictions.json")
    corpus = {r["name"]: r for r in read(GATE / "corpus.json")}
    assert len(corpus) == 19
    assert len({r["parent"] for r in corpus.values()}) == result["parent_groups"] == 7
    for path, expected in result["input_hashes"].items():
        assert sha(STUDY / path) == expected, path
    counts = {}
    paths = ["artifact_manifest.json", "artifact_manifest_2026-11-13.json",
             "artifact_manifest_2026-11-15.json", "artifact_manifest_2026-11-16.json",
             "validation_gate_2026-11-13/manifest.json",
             "supervisor_review_2026-11-16/manifest.json",
             "supervisor_review_2026-11-16/cross_domain_manifest.json"]
    for relative in paths:
        manifest = STUDY / relative
        entries = read(manifest)["files"]
        for name, expected in entries.items():
            assert sha(manifest.parent / name) == expected, (relative, name)
        counts[relative] = len(entries)
    profile_records = 0
    for name, saved in analysis["profiling"].items():
        values, initialization = [], 0
        for session in range(3):
            path = GATE / "results" / f"session_{session}" / "profiling" / (name + ".npz")
            meta = read(path.with_suffix(".json"))
            assert sha(path) == meta["file_sha256"]
            with np.load(path) as data:
                values.extend(int(x) for x in data["wall_ns"])
            initialization += meta["init_wall_ns"]
            profile_records += 1
        assert len(values) == saved["shots"] == 192
        assert sum(values) == saved["timed_decode_wall_ns"]
        assert initialization == saved["init_wall_ns"]
        # Find the least order statistic with the required binomial coverage.
        index = next(i for i in range(len(values))
                     if binom.cdf(i, len(values), .95) >= 1 - .05/19)
        assert sorted(values)[index] == saved["p95_upper_ns"]
    for row in result["rows"]:
        budget = row["budget_ms"] * 1e6
        upper = {n for n, p in analysis["profiling"].items() if p["p95_upper_ns"] <= budget}
        selected = {n for n in corpus if predictions[n]["rbf_density8"]["raw_ns"][1] <= budget}
        control = row["policies"]["filter_validate"]
        assert set(control["profiled_names"]) == selected
        assert set(control["admitted_names"]) == upper & selected
        assert set(row["policies"]["uniform_profile"]["admitted_names"]) == upper
        assert not control["unprofiled_model_accepts"]
        reference = next(r for r in analysis["budget_sweep"]
                         if r["budget_ms"] == row["budget_ms"] and r["policy"] == "profile_upper")
        assert {r["name"] for r in reference["details"] if r["admitted"]} == upper
        for policy, recorded in row["policies"].items():
            chosen = recorded["profiled_names"]
            expected = sum(analysis["profiling"][n]["timed_decode_wall_ns"] +
                           analysis["profiling"][n]["init_wall_ns"] for n in chosen)
            if policy != "uniform_profile":
                expected += sum(corpus[n]["feature_timing"]["base_density_ns"] +
                                predictions[n]["rbf_density8"]["median_inference_wall_ns"] for n in corpus)
            assert math.isclose(expected / 1e6, recorded["partial_replay_wall_ms"], abs_tol=1e-9)
    for row in result["frozen_filter_controls"]:
        model, budget = row["model"], row["budget_ms"] * 1e6
        chosen = [n for n in corpus if predictions[n][model]["raw_ns"][1] <= budget]
        accepted = {n for n in chosen if analysis["profiling"][n]["p95_upper_ns"] <= budget}
        assert len(chosen) == row["profiled_cases"]
        assert accepted == set(row["admitted_names"])
    for row in result["fixed_sample_count_reference"]:
        n, alpha = row["minimum_fixed_samples_for_finite_p95_upper"], row["per_bound_alpha"]
        assert .95**n <= alpha < .95**(n-1)
    output = dict(date="2026-11-16", passed=True, new_decoder_calls=0, new_model_fits=0,
                  previous_manifests_verified=counts, raw_profile_files_checked=profile_records,
                  budgets_checked=len(result["rows"]), frozen_filter_controls_checked=len(result["frozen_filter_controls"]),
                  feasibility_sha256=sha(ROOT / "feasibility.json"), audit_source_sha256=sha(Path(__file__)))
    (ROOT / "audit.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
