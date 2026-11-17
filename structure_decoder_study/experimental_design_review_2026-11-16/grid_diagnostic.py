"""One symmetric grid sensitivity on inspected data; no decoder work."""
from pathlib import Path
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"
import hashlib
import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
import numpy as np
from sklearn.preprocessing import StandardScaler, KernelCenterer
from sklearn.linear_model import Ridge
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics.pairwise import rbf_kernel

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
GATE = STUDY / "validation_gate_2026-11-13"
sys.path.insert(0, str(GATE))
spec = importlib.util.spec_from_file_location("review_frozen_models", GATE / "models.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, obj):
    path = ROOT / name
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def predict_unseen(fitter, row, train, feature_rows):
    """Same stable factorization, without using any bridge target labels."""
    x = fitter.x[row["feature_set"]]
    scaler = StandardScaler().fit(x[train])
    z = scaler.transform(x[train])
    incoming = np.log1p([[engine.densities(f)[c] for c in engine.SETS[row["feature_set"]]] for f in feature_rows])
    ze = scaler.transform(incoming)
    center = fitter.y[train].mean(axis=0)
    yc = fitter.y[train] - center
    output = []
    if row["kind"] == "linear":
        u, s, vt = np.linalg.svd(z, full_matrices=False)
    for t, (alpha, multiplier) in enumerate(row["chosen"]):
        if row["kind"] == "linear":
            coef = vt.T @ ((s / (s*s + alpha)) * (u.T @ yc[:, t]))
            prediction = ze @ coef
        else:
            gamma = multiplier / z.shape[1]
            k = engine.rbf(z, z, gamma)
            km, kg = k.mean(axis=0), k.mean()
            kc = k - km[None, :] - km[:, None] + kg
            values, vectors = np.linalg.eigh(kc)
            ke = engine.rbf(ze, z, gamma)
            kec = ke - ke.mean(axis=1)[:, None] - km[None, :] + kg
            dual = vectors @ ((vectors.T @ yc[:, t]) / (np.maximum(values, 0.) + alpha))
            prediction = kec @ dual
        output.append(prediction + center[t])
    return np.stack(output, axis=1)


def main():
    assert not (ROOT / "grid_results.json").exists(), "Preserve completed diagnostic"
    try:
        os.nice(10)
    except OSError:
        pass
    inputs = [ROOT/"GRID_DIAGNOSTIC_PROTOCOL.md", Path(__file__), GATE/"models.py", GATE/"common.py",
              GATE/"model_checkpoints.json", GATE/"bridge_predictions.json", GATE/"corpus.json",
              STUDY/"learning_curves_2026-11-13/dataset.json"]
    original_alpha, original_gamma = list(engine.ALPHAS), list(engine.GAMMAS)
    grids = dict(original=dict(alpha=original_alpha, gamma=original_gamma),
                 extended=dict(alpha=[10.**n for n in range(-8, 7)], gamma=[10.**n for n in range(-4, 3)]))
    config = dict(date="2026-11-16", development_only=True, new_decoder_calls=0, grids=grids,
                  fit_wall_cap_seconds=300, inputs={str(p.relative_to(STUDY)):sha(p) for p in inputs})
    save("grid_config.json", config)
    data = read(STUDY/"learning_curves_2026-11-13/dataset.json")
    legacy = read(GATE/"model_checkpoints.json")
    old_bridge = read(GATE/"bridge_predictions.json")
    bridge = read(GATE/"corpus.json")
    index = {r["name"]:i for i,r in enumerate(data)}
    all_rows, reports = [], {}
    maxima = dict(original_predictions=0., original_inner_losses=0., original_bridge_predictions=0., sklearn_selected_predictions=0.)
    selected_checks = []
    start = time.monotonic()
    for label, grid in grids.items():
        engine.ALPHAS, engine.GAMMAS = grid["alpha"], grid["gamma"]
        fitter = engine.Fitter(data)
        current, bridge_predictions = [], {}
        for number, before in enumerate(legacy):
            if time.monotonic()-start > config["fit_wall_cap_seconds"]:
                save("grid_partial.json", dict(complete=False, reason="wall cap", rows=all_rows+current))
                raise RuntimeError("Stopped at declared wall cap; results incomplete")
            train = np.array([index[n] for n in before["train_names"]])
            test = np.array([index[n] for n in before["test_names"]])
            assert not set(train) & set(test)
            assert not set(fitter.groups[train]) & set(fitter.groups[test])
            row = fitter.fit(before["kind"], before["feature_set"], train, test, [])
            row.update(grid=label, domain=before["domain"], held=before["held"], model=before["model"],
                       train_names=before["train_names"], test_names=before["test_names"])
            if label == "original":
                assert row["chosen"] == [tuple(x) for x in before["chosen"]]
                maxima["original_predictions"] = max(maxima["original_predictions"],
                    float(np.max(np.abs(np.array(row["predicted_log"])-before["predicted_log"]))))
                maxima["original_inner_losses"] = max(maxima["original_inner_losses"],
                    float(np.max(np.abs(np.array(row["inner_losses"])-before["inner_losses"]))))
            relevant = [c for c in bridge if c["parent"] == row["held"] and row["domain"] ==
                        ("original" if row["held"].startswith("old/") else "mixed_noise")]
            if relevant:
                values = predict_unseen(fitter, row, train, [c["features"] for c in relevant])
                for c, value in zip(relevant, values):
                    bridge_predictions.setdefault(c["name"], {})[row["model"]] = np.exp(value).tolist()
                    if label == "original":
                        maxima["original_bridge_predictions"] = max(maxima["original_bridge_predictions"],
                            float(np.max(np.abs(value-np.log(old_bridge[c["name"]][row["model"]]["raw_ns"])))) )
            current.append(row)
            if (number+1) % 6 == 0:
                print(json.dumps(dict(grid=label, outer_models=number+1, elapsed_seconds=round(time.monotonic()-start,2))), flush=True)
        all_rows.extend(current)
        summaries = []
        for domain in ("original", "fixed_noise", "mixed_noise"):
            for model in sorted({r["model"] for r in current}):
                rows = [r for r in current if r["domain"] == domain and r["model"] == model]
                for t,target in enumerate(engine.TARGETS):
                    summaries.append(dict(domain=domain, model=model, target=target, held_groups=len(rows),
                        heldout_error_factor=float(np.exp(np.mean([r["heldout_mae_log"][t] for r in rows]))),
                        train_error_factor=float(np.exp(np.mean([r["train_mae_log_group_balanced"][t] for r in rows]))),
                        alpha_at_min=sum(r["chosen"][t][0] == grid["alpha"][0] for r in rows),
                        alpha_at_max=sum(r["chosen"][t][0] == grid["alpha"][-1] for r in rows),
                        gamma_at_min=sum(r["chosen"][t][1] == grid["gamma"][0] for r in rows),
                        gamma_at_max=sum(r["chosen"][t][1] == grid["gamma"][-1] for r in rows),
                        chosen=[dict(held=r["held"],alpha=r["chosen"][t][0],gamma=r["chosen"][t][1]) for r in rows]))
        reports[label] = dict(summary=summaries, bridge_predictions_ns=bridge_predictions)
        if label == "extended":
            for domain in ("original", "fixed_noise", "mixed_noise"):
                for model in sorted({r["model"] for r in current}):
                    candidates = [r for r in current if r["domain"] == domain and r["model"] == model]
                    row = min(candidates, key=lambda r:(r["chosen"][1][0], r["chosen"][1][1] or 0., r["held"]))
                    train=np.array([index[n] for n in row["train_names"]]);test=np.array([index[n] for n in row["test_names"]])
                    scaler=StandardScaler().fit(fitter.x[row["feature_set"]][train])
                    z=scaler.transform(fitter.x[row["feature_set"]][train]);ze=scaler.transform(fitter.x[row["feature_set"]][test])
                    error=0.
                    for t,(alpha,gamma) in enumerate(row["chosen"]):
                        y=fitter.y[train,t];center=y.mean()
                        if row["kind"] == "linear":
                            separate=Ridge(alpha=alpha,solver="svd").fit(z,y).predict(ze)
                        else:
                            kernel=rbf_kernel(z,z,gamma=gamma/z.shape[1]);kc=KernelCenterer().fit(kernel)
                            separate=KernelRidge(alpha=alpha,kernel="precomputed").fit(kc.transform(kernel),y-center).predict(
                                kc.transform(rbf_kernel(ze,z,gamma=gamma/z.shape[1])))+center
                        error=max(error,float(np.max(np.abs(separate-np.array(row["predicted_log"])[:,t]))))
                    maxima["sklearn_selected_predictions"]=max(maxima["sklearn_selected_predictions"],error)
                    selected_checks.append(dict(domain=domain,model=model,held=row["held"],max_log_prediction_difference=error))
    save("grid_checkpoints.json", all_rows)
    passed=max(maxima[k] for k in maxima if k.startswith("original")) < 1e-7 and maxima["sklearn_selected_predictions"] < 1e-5
    result=dict(complete=True,development_only=True,new_decoder_calls=0,new_physical_samples=0,
                outer_model_evaluations=len(all_rows),selected_independent_sklearn_target_fits=2*len(selected_checks),
                elapsed_seconds=time.monotonic()-start,grids=reports,numerical_checks=dict(passed=passed,maxima=maxima,selected=selected_checks),
                config_sha256=sha(ROOT/"grid_config.json"))
    save("grid_results.json",result)
    print(json.dumps(dict(complete=True,outer_models=len(all_rows),numerical_checks=result["numerical_checks"],elapsed_seconds=result["elapsed_seconds"])),flush=True)


if __name__ == "__main__":
    main()
