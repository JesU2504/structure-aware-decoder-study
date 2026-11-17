"""Structural screens and separate sklearn reproduction of sensitivity fits."""
from pathlib import Path
import hashlib
import json
import os
import sys
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[k] = "1"
import numpy as np
import scipy.sparse as sp
from scipy.stats import binom
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
LEARNING = STUDY/"learning_curves_2026-11-13"


def read(path):
    return json.loads(path.read_text())


def main():
    sys.path.insert(0, str(STUDY))
    import study
    import stim
    matrix_screen = []
    paths = [("pilot", p) for p in sorted((STUDY/"circuits").glob("*.npz"))]
    paths += [("stress", p) for p in sorted((STUDY/"stress_gate/circuits").glob("*.dem"))]
    for source, path in paths:
        if source == "pilot":
            a = np.load(path)
            h = sp.csc_matrix((a["h_data"], a["h_indices"], a["h_indptr"]), shape=a["h_shape"])
            l = sp.csc_matrix((a["l_data"], a["l_indices"], a["l_indptr"]), shape=a["l_shape"])
        else:
            h, l, _, _ = study.convert(stim.DetectorErrorModel(path.read_text()))
        signatures = {}
        singles, pairs = [], []
        for col in range(h.shape[1]):
            detectors = tuple(h.indices[h.indptr[col]:h.indptr[col+1]].tolist())
            logical = tuple(l.indices[l.indptr[col]:l.indptr[col+1]].tolist())
            if not detectors and logical:
                singles.append(col)
            if detectors in signatures and signatures[detectors][0] != logical:
                pairs.append([signatures[detectors][1], col])
            else:
                signatures[detectors] = (logical, col)
        matrix_screen.append(dict(name=path.stem, source=source, undetected_single_mechanisms=len(singles),
                                  equal_detector_support_different_logical_pairs=len(pairs),
                                  examples=dict(singles=singles[:3], pairs=pairs[:3])))
    # Order-statistic coverage under the explicitly conditional IID model.
    coverage = {}
    for n in (768, 6000):
        lo = int(binom.ppf(.025, n, .95))
        hi = int(binom.ppf(.975, n, .95))+1
        value = float(binom.cdf(hi-1, n, .95)-binom.cdf(lo-1, n, .95))
        assert value >= .95
        coverage[n] = value
    data = read(LEARNING/"dataset.json")
    cfg = read(LEARNING/"run_config.json")
    groups = np.array([r["group"] for r in data])
    index = {r["name"]: i for i, r in enumerate(data)}
    raw = {}
    for row in data:
        raw[row["name"]] = [np.load((STUDY/"results"/f"session_{s}"/(row["name"]+".npz")) if row["source"] == "pilot"
                                   else (STUDY/"stress_gate/results/discovery"/f"session_{s}"/(row["name"]+".npz")))["latency_ns" if row["source"] == "pilot" else "wall_ns"] for s in range(3)]
    max_difference, max_inner_difference = 0.0, 0.0
    jobs_checked, fits_checked = 0, 0
    for output in read(ROOT/"sensitivity_checkpoints.json"):
        scenario = output["scenario"]
        labels = []
        for i, row in enumerate(data):
            sessions = raw[row["name"]]
            if scenario.startswith("session_"):
                values = sessions[int(scenario.rsplit("_",1)[1])]
            elif scenario.startswith("equal_precision_"):
                draw = int(scenario.rsplit("_",1)[1])
                values = np.concatenate([np.random.default_rng(np.random.SeedSequence([20261113, draw, i, s])).choice(v, 256, replace=False)
                                         if row["source"] == "pilot" else v for s, v in enumerate(sessions)])
            else:
                values = np.concatenate(sessions)
            labels.append([values.mean(), np.quantile(values, .95)])
        y = np.log(labels)
        for job in output["jobs"]:
            test = np.array([index[n] for n in job["test_names"]])
            train = np.array([index[n] for n in job["train_names"]])
            assert set(train).isdisjoint(test)
            assert job["held_group"] not in set(groups[train])
            for model, saved in job["models"].items():
                errors = np.abs(np.array(saved["predicted_log"])-y[test]).mean(axis=0)
                assert np.allclose(errors, saved["heldout_mae_log"], atol=1e-12, rtol=0)
            jobs_checked += 1
        if scenario not in ("pooled", "session_0", "equal_precision_00", "equal_precision_05"):
            continue
        job = output["jobs"][0]
        train = np.array([index[n] for n in job["train_names"]])
        test = np.array([index[n] for n in job["test_names"]])
        for model, columns in cfg["models"].items():
            x = np.log1p([[row["features"][c] for c in columns] for row in data])
            losses = []
            for alpha in cfg["alphas"]:
                inner_errors = []
                for group in sorted(set(groups[train])):
                    inside = train[groups[train] != group]
                    valid = train[groups[train] == group]
                    fit = make_pipeline(StandardScaler(), Ridge(alpha=alpha, solver="cholesky"))
                    fit.fit(x[inside], y[inside])
                    inner_errors.append(np.abs(fit.predict(x[valid])-y[valid]).mean(axis=0))
                losses.append(np.mean(inner_errors, axis=0))
            losses = np.array(losses)
            saved = job["models"][model]
            max_inner_difference = max(max_inner_difference, float(np.max(np.abs(losses-saved["inner_losses_by_alpha"]))))
            selected = np.array(cfg["alphas"])[np.argmin(losses, axis=0)]
            assert np.array_equal(selected, saved["selected_alphas"])
            predicted = []
            for t, alpha in enumerate(selected):
                fit = make_pipeline(StandardScaler(), Ridge(alpha=alpha, solver="cholesky"))
                fit.fit(x[train], y[train,t])
                predicted.append(fit.predict(x[test]))
            difference = float(np.max(np.abs(np.stack(predicted,axis=1)-saved["predicted_log"])))
            max_difference = max(max_difference, difference)
            fits_checked += 1
    assert max_difference < 1e-8 and max_inner_difference < 1e-8
    result = dict(passed=True, internal_only=True, sensitivity_jobs_metrics_checked=jobs_checked,
                  separate_sklearn_nested_fits=fits_checked, max_log_prediction_difference=max_difference,
                  max_inner_loss_difference=max_inner_difference,
                  iid_order_statistic_coverage=coverage, matrices_screened=len(matrix_screen),
                  undetected_single_mechanism_cases=[r for r in matrix_screen if r["undetected_single_mechanisms"]],
                  two_mechanism_signature_cases=[r for r in matrix_screen if r["equal_detector_support_different_logical_pairs"]],
                  matrix_screen_is_not_full_circuit_distance_or_fault_tolerance_proof=True,
                  matrix_details=matrix_screen)
    (ROOT/"checks.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k != "matrix_details"},indent=2))


if __name__ == "__main__":
    main()
