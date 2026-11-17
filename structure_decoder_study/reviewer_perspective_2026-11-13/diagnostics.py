"""Post hoc label/session sensitivity review; no decoder timing is performed."""
from pathlib import Path
from collections import defaultdict
import copy
import hashlib
import importlib.util
import json
import os
import time
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[k] = "1"
import numpy as np
from scipy.stats import binom

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
LEARNING = STUDY/"learning_curves_2026-11-13"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")


def describe(values):
    return dict(minimum=float(np.min(values)), median=float(np.median(values)),
                p90=float(np.quantile(values, .9)), maximum=float(np.max(values)))


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    start = time.monotonic()
    manifests = {}
    for path in (STUDY/"artifact_manifest.json", STUDY/"artifact_manifest_2026-11-13.json",
                 STUDY/"stress_gate/manifest.json", STUDY/"fit_diagnostic_2026-11-13/manifest.json",
                 LEARNING/"manifest.json"):
        files = read(path)["files"]
        for name, expected in files.items():
            assert sha(path.parent/name) == expected, (path, name)
        manifests[str(path.relative_to(STUDY))] = len(files)
    spec = importlib.util.spec_from_file_location("learning_runner_for_review", LEARNING/"run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = read(LEARNING/"dataset.json")
    arrays = {}
    precision = []
    for row in data:
        sessions = []
        correlations = []
        for session in range(3):
            if row["source"] == "pilot":
                path = STUDY/"results"/f"session_{session}"/(row["name"]+".npz")
                values = np.load(path)["latency_ns"]
            else:
                path = STUDY/"stress_gate/results/discovery"/f"session_{session}"/(row["name"]+".npz")
                values = np.load(path)["wall_ns"]
            assert len(values) == (2000 if row["source"] == "pilot" else 256)
            sessions.append(values)
            logs = np.log(values.astype(float))
            correlations.append(float(np.corrcoef(logs[:-1], logs[1:])[0, 1]))
        arrays[row["name"]] = sessions
        pooled = np.concatenate(sessions)
        n = len(pooled)
        ordered = np.sort(pooled)
        lower_rank = int(binom.ppf(.025, n, .95))
        upper_rank = int(binom.ppf(.975, n, .95))+1
        lo = float(ordered[lower_rank-1]) if lower_rank else 0.0
        hi = float(ordered[upper_rank-1]) if upper_rank <= n else float("inf")
        p95s = [float(np.quantile(values, .95)) for values in sessions]
        means = [float(values.mean()) for values in sessions]
        assert np.isclose(np.mean(pooled), row["targets"]["mean_ns"], rtol=1e-13)
        assert np.isclose(np.quantile(pooled, .95), row["targets"]["p95_ns"], rtol=1e-13)
        precision.append(dict(name=row["name"], source=row["source"], group=row["group"],
              pooled_shots=n, pooled_p95_ns=row["targets"]["p95_ns"],
              p95_iid_order_statistic_interval=[lo, hi],
              interval_width_fraction=(hi-lo)/row["targets"]["p95_ns"],
              session_p95_ns=p95s, session_mean_ns=means,
              session_p95_max_min=max(p95s)/min(p95s), session_mean_max_min=max(means)/min(means),
              session_lag_one_log_timing_correlations=correlations,
              top_one_percent_pooled_wall_fraction=float(np.sort(pooled)[-int(np.ceil(n*.01)):].sum()/pooled.sum())))
    precision_summary = {source: {key: describe([r[key] for r in precision if r["source"] == source])
                                for key in ("interval_width_fraction", "session_p95_max_min", "session_mean_max_min", "top_one_percent_pooled_wall_fraction")}
                         for source in ("pilot", "discovery")}
    old = read(STUDY/"corpus.json")
    old_summaries = {r["name"]: r for r in read(STUDY/"results/case_summaries.json")}
    overhead = {key: describe([r[key]/1e6 for r in old]) for key in ("circuit_build_ns", "dem_build_ns", "convert_ns")}
    overhead["full_recorded_feature_ms"] = describe([r["features"]["feature_time_ns"]/1e6 for r in old])
    overhead["full_feature_time_divided_by_p95"] = describe([r["features"]["feature_time_ns"]/old_summaries[r["name"]]["p95_ns"] for r in old])
    base_x = np.log1p([[r["features"][c] for c in module.B2] for r in old])
    correlation = np.corrcoef(base_x.T)
    correlations = [{"first": module.B2[i], "second": module.B2[j], "correlation": float(correlation[i,j])}
                    for i in range(len(module.B2)) for j in range(i+1, len(module.B2))]
    save(ROOT/"precision_and_context.json", dict(previous_manifests_verified=manifests, labels=precision,
         precision_summary=precision_summary, old_pipeline_costs=overhead,
         old_log1p_base_feature_correlations=correlations,
         feature_cost_is_total_not_incremental_graph_cost=True,
         intervals_assume_iid_and_stable_context=True))
    old_groups = sorted({r["group"] for r in data if r["source"] == "pilot"})
    new_groups = sorted({r["group"] for r in data if r["source"] == "discovery"})
    scenarios = ["pooled"]+[f"session_{i}" for i in range(3)]+[f"equal_precision_{i:02}" for i in range(10)]
    outputs = []
    for scenario in scenarios:
        modified = copy.deepcopy(data)
        for index, row in enumerate(modified):
            values = arrays[row["name"]]
            if scenario.startswith("session_"):
                selected = values[int(scenario.rsplit("_",1)[1])]
            elif scenario.startswith("equal_precision_"):
                draw = int(scenario.rsplit("_",1)[1])
                selected = np.concatenate([np.random.default_rng(np.random.SeedSequence([20261113, draw, index, s])).choice(v, 256, replace=False)
                                           if row["source"] == "pilot" else v for s, v in enumerate(values)])
            else:
                selected = np.concatenate(values)
            row["targets"] = dict(mean_ns=float(selected.mean()), p95_ns=float(np.quantile(selected, .95)))
        experiment = module.Experiment(modified)
        for domain, parents in (("original", old_groups), ("expansion_fixed_noise", new_groups), ("expansion_mixed_noise", new_groups)):
            allowed = np.array([r["source"] == "pilot" if domain == "original" else
                                (r["p"] == .001 if domain == "expansion_fixed_noise" else True) for r in modified])
            jobs = []
            for held in parents:
                training = [g for g in old_groups if g != held] if domain == "original" else old_groups+[g for g in new_groups if g != held]
                jobs.append(experiment.job(domain, held, 6 if domain == "original" else 11, 0, training, allowed))
            aggregates = {}
            for model in module.MODELS:
                aggregates[model] = {target: dict(
                    error_factor=float(np.exp(np.mean([j["models"][model]["heldout_mae_log"][t] for j in jobs]))),
                    train_error_factor=float(np.exp(np.mean([j["models"][model]["train_mae_log_group_balanced"][t] for j in jobs]))))
                    for t, target in enumerate(module.TARGETS)}
            result = dict(scenario=scenario, domain=domain, aggregates=aggregates, jobs=jobs)
            outputs.append(result)
        save(ROOT/"sensitivity_checkpoints.json", outputs)
        print(json.dumps(dict(scenario=scenario, elapsed_seconds=time.monotonic()-start,
                         results={r["domain"]: {m: round(v["p95_ns"]["error_factor"],6) for m,v in r["aggregates"].items()}
                                  for r in outputs if r["scenario"] == scenario})), flush=True)
    reference = read(LEARNING/"summary.json")
    for r in outputs:
        if r["scenario"] != "pooled":
            continue
        for model, target_results in r["aggregates"].items():
            for target, result in target_results.items():
                previous = next(row for row in reference["rows"] if row["experiment"] == r["domain"]
                                and row["model"] == model and row["target"] == target
                                and row["size"] == (6 if r["domain"] == "original" else 11))
                assert np.isclose(previous["heldout_error_factor"], result["error_factor"], rtol=1e-12)
    compact = [dict(scenario=r["scenario"], domain=r["domain"], aggregates=r["aggregates"]) for r in outputs]
    save(ROOT/"sensitivity_summary.json", dict(post_hoc=True, no_new_decoder_measurements=True,
        independent_replicates=False, earlier_pooled_endpoints_reproduced=True, scenarios=compact,
        elapsed_seconds=time.monotonic()-start,
        input_hashes={str(p.relative_to(STUDY)): sha(p) for p in (LEARNING/"run.py", LEARNING/"dataset.json", ROOT/"PROTOCOL.md", ROOT/"diagnostics.py")}))
    print(json.dumps(dict(complete=True, previous_manifests_verified=manifests, precision_summary=precision_summary)), flush=True)


if __name__ == "__main__":
    main()
