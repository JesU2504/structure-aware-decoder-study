"""Declared linear/nonlinear controls, with nested group-held-out selection."""
import time
from sklearn.preprocessing import StandardScaler
from common import *


class Fitter:
    def __init__(self, data):
        self.data = data
        self.groups = np.array([r["group"] for r in data])
        self.y = np.log([[r["targets"][t] for t in TARGETS] for r in data])
        self.x = {name: np.log1p([[densities(r["features"])[c] for c in cols] for r in data]) for name, cols in SETS.items()}
        self.cache = {}

    def candidates(self, kind):
        return [(a, None) for a in ALPHAS] if kind == "linear" else [(a, g) for g in GAMMAS for a in ALPHAS]

    def path(self, kind, columns, train):
        key = (kind, columns, tuple(train))
        if key in self.cache:
            return self.cache[key]
        x = self.x[columns]
        scaler = StandardScaler().fit(x[train])
        z, ze = scaler.transform(x[train]), scaler.transform(x)
        center = self.y[train].mean(axis=0)
        yc = self.y[train]-center
        predictions = []
        if kind == "linear":
            u, s, vt = np.linalg.svd(z, full_matrices=False)
            for alpha in ALPHAS:
                coef = vt.T@((s/(s*s+alpha))[:, None]*(u.T@yc))
                predictions.append(ze@coef+center)
        else:
            for multiplier in GAMMAS:
                gamma = multiplier/z.shape[1]
                k = rbf(z, z, gamma)
                km, kg = k.mean(axis=0), float(k.mean())
                kc = k-km[None, :]-km[:, None]+kg
                values, vectors = np.linalg.eigh(kc)
                values = np.maximum(values, 0.)
                ke = rbf(ze, z, gamma)
                kec = ke-ke.mean(axis=1)[:, None]-km[None, :]+kg
                projection = vectors.T@yc
                for alpha in ALPHAS:
                    dual = vectors@(projection/(values+alpha)[:, None])
                    predictions.append(kec@dual+center)
        result = np.array(predictions)
        assert np.isfinite(result).all()
        self.cache[key] = result
        return result

    def payload(self, kind, columns, train, chosen):
        x = self.x[columns]
        scaler = StandardScaler().fit(x[train])
        z = scaler.transform(x[train])
        y = self.y[train]
        out = dict(kind=kind, columns=SETS[columns], center=scaler.mean_.tolist(), scale=scaler.scale_.tolist(), targets=[])
        if kind == "rbf":
            out["train_z"] = z.tolist()
        for t, (alpha, multiplier) in enumerate(chosen):
            center = float(y[:, t].mean())
            yc = y[:, t]-center
            if kind == "linear":
                coef = np.linalg.solve(z.T@z+alpha*np.eye(z.shape[1]), z.T@yc)
                record = dict(alpha=alpha, target_mean=center, coef=coef.tolist())
            else:
                gamma = multiplier/z.shape[1]
                k = rbf(z, z, gamma)
                km, kg = k.mean(axis=0), float(k.mean())
                kc = k-km[None, :]-km[:, None]+kg
                dual = np.linalg.solve(kc+alpha*np.eye(len(train)), yc)
                record = dict(alpha=alpha, gamma=gamma, gamma_multiplier=multiplier, target_mean=center,
                              dual=dual.tolist(), kernel_column_mean=km.tolist(), kernel_grand_mean=kg)
            out["targets"].append(record)
        return out

    def fit(self, kind, columns, train, test, bridge_cases):
        candidates = self.candidates(kind)
        inner_losses, under = [], []
        for group in sorted(set(self.groups[train])):
            valid = train[self.groups[train] == group]
            inside = train[self.groups[train] != group]
            path = self.path(kind, columns, inside)[:, valid, :]
            inner_losses.append(np.abs(path-self.y[valid][None, :, :]).mean(axis=1))
            under.append((self.y[valid][None, :, :]-path).max(axis=1))
        losses = np.mean(inner_losses, axis=0)
        maxima = np.max(under, axis=0)
        chosen_indices = np.argmin(losses, axis=0)
        chosen = [candidates[i] for i in chosen_indices]
        margins = np.exp(np.maximum(0., [maxima[chosen_indices[t], t] for t in range(2)]))
        path = self.path(kind, columns, train)
        predictions = np.stack([path[chosen_indices[t], :, t] for t in range(2)], axis=1)
        residual = predictions-self.y
        result = dict(kind=kind, feature_set=columns, chosen=chosen, margins=margins.tolist(),
             candidates=candidates, inner_losses=losses.tolist(),
             train_mae_log_group_balanced=np.mean([np.abs(residual[train[self.groups[train] == g]]).mean(axis=0)
                                                  for g in sorted(set(self.groups[train]))], axis=0).tolist(),
             heldout_mae_log=np.abs(residual[test]).mean(axis=0).tolist(),
             predicted_log=predictions[test].tolist())
        if bridge_cases:
            payload = self.payload(kind, columns, train, chosen)
            # Direct payload and path implementations must agree on the outer test.
            for index in test:
                assert np.allclose(predict_payload(payload, densities(self.data[index]["features"])), predictions[index], atol=1e-8, rtol=0)
            result["payload"] = payload
            result["bridge_predictions"] = {}
            for case in bridge_cases:
                value = predict_payload(payload, case["features"])
                elapsed = []
                for _ in range(20):
                    t0 = time.perf_counter_ns()
                    predict_payload(payload, case["features"])
                    elapsed.append(time.perf_counter_ns()-t0)
                result["bridge_predictions"][case["name"]] = dict(raw_ns=np.exp(value).tolist(),
                    padded_ns=(np.exp(value)*margins).tolist(), median_inference_wall_ns=float(np.median(elapsed)))
        return result


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    start = time.monotonic()
    verify_previous()
    paths = [ROOT/"models.py", ROOT/"common.py", ROOT/"PROTOCOL.md", ROOT/"corpus.json",
             STUDY/"learning_curves_2026-11-13/dataset.json"]
    config_path = ROOT/"model_run_config.json"
    if not config_path.exists():
        save(config_path, dict(alphas=ALPHAS, gamma_multipliers=GAMMAS, feature_sets=SETS,
             targets=TARGETS, kernel_and_targets_centered=True, bridge_timings_collected=False,
             files={str(p.relative_to(STUDY)): sha(p) for p in paths}))
    cfg = read(config_path)
    for name, expected in cfg["files"].items():
        assert sha(STUDY/name) == expected, name
    data = read(STUDY/"learning_curves_2026-11-13/dataset.json")
    bridge = read(ROOT/"corpus.json")
    fitter = Fitter(data)
    old = sorted({r["group"] for r in data if r["source"] == "pilot"})
    new = sorted({r["group"] for r in data if r["source"] == "discovery"})
    results = []
    for domain, parents in (("original", old), ("fixed_noise", new), ("mixed_noise", new)):
        allowed = np.array([r["source"] == "pilot" if domain == "original" else
                           (r["p"] == .001 if domain == "fixed_noise" else True) for r in data])
        for held in parents:
            train = np.flatnonzero((fitter.groups != held)&allowed)
            test = np.flatnonzero((fitter.groups == held)&allowed)
            relevant = [case for case in bridge if case["parent"] == held and domain ==
                        ("original" if held.startswith("old/") else "mixed_noise")]
            for feature_set in SETS:
                for kind in ("linear", "rbf"):
                    model = kind+"_"+feature_set
                    result = fitter.fit(kind, feature_set, train, test, relevant)
                    result.update(domain=domain, held=held, model=model,
                         train_names=[data[i]["name"] for i in train], test_names=[data[i]["name"] for i in test])
                    results.append(result)
            save(ROOT/"model_checkpoints.json", results)
            print(json.dumps(dict(domain=domain, held=held, outer_models=len(results), elapsed_seconds=time.monotonic()-start)), flush=True)
    summary = []
    for domain in ("original", "fixed_noise", "mixed_noise"):
        for model in sorted({r["model"] for r in results}):
            rows = [r for r in results if r["domain"] == domain and r["model"] == model]
            for t, target in enumerate(TARGETS):
                summary.append(dict(domain=domain, model=model, target=target, held_groups=len(rows),
                    heldout_error_factor=float(np.exp(np.mean([r["heldout_mae_log"][t] for r in rows]))),
                    train_error_factor=float(np.exp(np.mean([r["train_mae_log_group_balanced"][t] for r in rows]))),
                    groups={r["held"]: r["heldout_mae_log"][t] for r in rows}))
    predictions = {case["name"]: {} for case in bridge}
    for result in results:
        for name, prediction in result.get("bridge_predictions", {}).items():
            predictions[name][result["model"]] = dict(**prediction, held=result["held"], domain=result["domain"])
    assert all(len(p) == 6 for p in predictions.values())
    save(ROOT/"bridge_predictions.json", predictions)
    save(ROOT/"model_summary.json", dict(post_hoc_development=True, rows=summary,
         outer_models=len(results), elapsed_seconds=time.monotonic()-start,
         frozen_old_predictors_updated=False, config_sha256=sha(config_path)))
    print(json.dumps([r for r in summary if r["target"] == "p95_ns"], indent=2), flush=True)


if __name__ == "__main__":
    main()
