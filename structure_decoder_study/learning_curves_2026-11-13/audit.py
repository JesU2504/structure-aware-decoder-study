"""Separate sklearn checks of the custom SVD paths and nested selections."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import os
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[k] = "1"
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent


def main():
    cfg = json.loads((ROOT/"run_config.json").read_text())
    digest = hashlib.sha256((ROOT/"run_config.json").read_bytes()).hexdigest()
    for name, expected in cfg["files"].items():
        assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest() == expected
    data = json.loads((ROOT/"dataset.json").read_text())
    index = {r["name"]: i for i, r in enumerate(data)}
    groups = np.array([r["group"] for r in data])
    actual = np.log([[r["targets"][t] for t in cfg["targets"]] for r in data])
    chunks = [json.loads(p.read_text()) for p in sorted((ROOT/"checkpoints").glob("*.json"))]
    assert len(chunks) == 31
    checked, subsets = [], defaultdict(dict)
    outer_count = 0
    max_metric_difference = 0.0
    for chunk in chunks:
        assert chunk["config_sha256"] == digest
        jobs = chunk["jobs"]
        tests = {tuple(j["test_names"]) for j in jobs}
        assert len(tests) == 1
        for job in jobs:
            train = np.array([index[n] for n in job["train_names"]])
            test = np.array([index[n] for n in job["test_names"]])
            held = job["held_group"]
            assert set(train).isdisjoint(test) and held not in job["train_groups"]
            assert set(groups[train]) == set(job["train_groups"])
            allowed = np.array([r["source"] == "pilot" if job["experiment"] == "original"
                                else (r["p"] == .001 if job["experiment"] == "expansion_fixed_noise" else True) for r in data])
            assert set(train) == set(np.flatnonzero(np.isin(groups, job["train_groups"]) & allowed))
            assert set(test) == set(np.flatnonzero((groups == held) & allowed))
            assert len(train) == job["train_cases"] and len(test) == job["test_cases"]
            if job["experiment"] != "original":
                subsets[job["experiment"], held, job["order"]][job["size"]] = set(job["train_groups"])
            for model, result in job["models"].items():
                predicted = np.array(result["predicted_log"])
                error = np.abs(predicted-actual[test]).mean(axis=0)
                difference = float(np.max(np.abs(error-result["heldout_mae_log"])))
                max_metric_difference = max(max_metric_difference, difference)
                assert difference < 1e-12
                assert all(alpha in cfg["alphas"] for alpha in result["selected_alphas"])
                outer_count += 1
        # Independently reproduce the maximum-training endpoint for every group.
        checked.append(max(jobs, key=lambda j: j["size"]))
        if chunk["experiment"] == "original" and len(checked) % 2:
            checked.append(min(jobs, key=lambda j: j["size"]))
    for sizes in subsets.values():
        ordered = sorted(sizes)
        assert all(sizes[a].issubset(sizes[b]) for a, b in zip(ordered, ordered[1:]))
    max_prediction_difference, max_loss_difference = 0.0, 0.0
    selected_models_checked = 0
    for job in checked:
        train = np.array([index[n] for n in job["train_names"]])
        test = np.array([index[n] for n in job["test_names"]])
        for model, columns in cfg["models"].items():
            x = np.log1p([[r["features"][c] for c in columns] for r in data])
            losses = []
            for alpha in cfg["alphas"]:
                group_losses = []
                for group in sorted(set(groups[train])):
                    inside = train[groups[train] != group]
                    validation = train[groups[train] == group]
                    fit = make_pipeline(StandardScaler(), Ridge(alpha=alpha, solver="cholesky"))
                    fit.fit(x[inside], actual[inside])
                    group_losses.append(np.abs(fit.predict(x[validation])-actual[validation]).mean(axis=0))
                losses.append(np.mean(group_losses, axis=0))
            losses = np.array(losses)
            reference = job["models"][model]
            max_loss_difference = max(max_loss_difference, float(np.max(np.abs(losses-reference["inner_losses_by_alpha"]))))
            selected = np.array(cfg["alphas"])[np.argmin(losses, axis=0)]
            assert np.array_equal(selected, reference["selected_alphas"]), (job["held_group"], model, selected)
            predictions = []
            for target, alpha in enumerate(selected):
                fit = make_pipeline(StandardScaler(), Ridge(alpha=alpha, solver="cholesky"))
                fit.fit(x[train], actual[train, target])
                predictions.append(fit.predict(x[test]))
            predicted = np.stack(predictions, axis=1)
            max_prediction_difference = max(max_prediction_difference, float(np.max(np.abs(predicted-reference["predicted_log"]))))
            selected_models_checked += 1
    assert max_prediction_difference < 1e-8 and max_loss_difference < 1e-8
    result = dict(passed=True, internal_check_only=True, external_review=False,
                  outer_jobs=sum(len(c["jobs"]) for c in chunks), model_outer_evaluations=outer_count,
                  split_membership_and_metrics_checked=True, expansion_orders_are_nested=True,
                  fixed_outer_test_sets=True, separate_sklearn_model_reproductions=selected_models_checked,
                  max_log_prediction_difference=max_prediction_difference,
                  max_inner_loss_difference=max_loss_difference, max_saved_metric_difference=max_metric_difference)
    (ROOT/"audit.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
