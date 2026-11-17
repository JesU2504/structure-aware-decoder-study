"""Post hoc fit/generalization diagnostic on the unchanged 78-case pilot.

No decoder measurements, feature search, hyperparameter selection, or updates to
the frozen deployment predictor. All compared models use the archived alpha=1.
This diagnoses compatibility with overfitting; it does not identify a unique
cause or replace fresh validation.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    frozen_manifest = json.loads((STUDY / "artifact_manifest.json").read_text())["files"]
    mismatches = [name for name, expected in frozen_manifest.items()
                  if not (STUDY / name).is_file() or sha(STUDY / name) != expected]
    if mismatches:
        raise RuntimeError(f"Original artifact changed: {mismatches}")
    spec = importlib.util.spec_from_file_location("archived_analysis", STUDY / "analyze_v2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = json.loads((STUDY / "corpus.json").read_text())
    summaries = json.loads((STUDY / "results/case_summaries.json").read_text())
    assert [r["name"] for r in records] == [r["name"] for r in summaries]
    outputs = {}
    max_solver_difference = 0.0
    solvers = set()
    for grouping in ("original_motifs", "single_repeated_merged"):
        groups = np.array([("single_repeated" if grouping == "single_repeated_merged"
                            and r["case"]["family"] in ("single", "repeated")
                            else r["case"]["family"]) for r in records])
        outputs[grouping] = {}
        for target in ("mean_ns", "p95_ns"):
            y = np.log([r[target] for r in summaries])
            outputs[grouping][target] = {}
            for name in ("B2_sparsity_activity", "B3_structure"):
                columns = module.MODELS[name]
                x = np.log1p([[r["features"][c] for c in columns] for r in records])
                folds = []
                for group in sorted(set(groups)):
                    test = groups == group
                    train = ~test
                    scaler = StandardScaler().fit(x[train])
                    xt, xv = scaler.transform(x[train]), scaler.transform(x[test])
                    fit = Ridge(alpha=1.0).fit(xt, y[train])
                    reference = Ridge(alpha=1.0, solver="svd").fit(xt, y[train])
                    difference = float(np.max(np.abs(fit.predict(xv) - reference.predict(xv))))
                    max_solver_difference = max(max_solver_difference, difference)
                    solvers.add(fit.solver_)
                    residual_train = fit.predict(xt) - y[train]
                    residual_test = fit.predict(xv) - y[test]
                    singular = np.linalg.svd(xt, compute_uv=False)
                    folds.append(dict(held_group=str(group), train_cases=int(train.sum()),
                                      test_cases=int(test.sum()), solver=fit.solver_, n_iter=fit.n_iter_,
                                      train_rmse_log=float(np.sqrt(np.mean(residual_train**2))),
                                      heldout_rmse_log=float(np.sqrt(np.mean(residual_test**2))),
                                      train_mae_log=float(np.mean(np.abs(residual_train))),
                                      heldout_mae_log=float(np.mean(np.abs(residual_test))),
                                      effective_df_including_intercept=float(1 + np.sum(singular**2/(singular**2+1))),
                                      svd_solver_max_log_prediction_difference=difference))
                outputs[grouping][target][name] = dict(
                    feature_count=len(columns), columns=columns, alpha=1.0, folds=folds,
                    mean_fold_train_rmse_log=float(np.mean([r["train_rmse_log"] for r in folds])),
                    mean_fold_heldout_rmse_log=float(np.mean([r["heldout_rmse_log"] for r in folds])),
                    mean_fold_train_error_factor=float(np.exp(np.mean([r["train_mae_log"] for r in folds]))),
                    family_balanced_heldout_error_factor=float(np.exp(np.mean([r["heldout_mae_log"] for r in folds]))))
    assert max_solver_difference < 1e-9
    archived_tuning = json.loads((STUDY / "results/robustness.json").read_text())
    tuning_summary = {
        subset: {target: {model: data["family_balanced_multiplicative_error"]
                          for model, data in models.items()}
                 for target, models in archived_tuning[subset].items()}
        for subset in ("full", "connected")}
    result = dict(post_hoc=True, decoder_timings_collected=False, original_files_checked=len(frozen_manifest),
                  original_files_unchanged=True, pilot_configurations=len(records),
                  original_motif_groups=len({r["case"]["family"] for r in records}),
                  features_are_selected_summaries_not_full_connectivity=True,
                  input_hashes={str(p.relative_to(STUDY)): sha(p) for p in
                                (STUDY/"analyze_v2.py", STUDY/"corpus.json", STUDY/"results/case_summaries.json",
                                 STUDY/"results/robustness.json")},
                  observed_solvers=sorted(solvers), max_auto_vs_svd_log_prediction_difference=max_solver_difference,
                  fixed_alpha_diagnostics=outputs, archived_nested_regularization=tuning_summary,
                  limitations=["Training errors are resubstitution errors, not estimates of generalization.",
                               "Small related motif corpus; merging two labels does not establish independent applications.",
                               "No learning curve, nonlinear-model comparison, or new held-out corpus in this diagnostic.",
                               "A train/held-out gap is compatible with overfitting and domain shift; it is not a unique diagnosis."])
    (ROOT/"results.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(dict(solvers=result["observed_solvers"],
                         max_auto_vs_svd_log_prediction_difference=max_solver_difference,
                         diagnostics={grouping: {target: {name: {k: v for k,v in data.items() if k.startswith("mean_fold") or k=="family_balanced_heldout_error_factor"}
                                                           for name,data in models.items()}
                                                for target,models in targets.items()}
                                      for grouping,targets in outputs.items()},
                         archived_nested_regularization=tuning_summary), indent=2))


if __name__ == "__main__":
    main()
