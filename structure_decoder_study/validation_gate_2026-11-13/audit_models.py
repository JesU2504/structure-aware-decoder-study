"""Separate sklearn checks of nested linear and centered-kernel controls."""
from common import *
from sklearn.preprocessing import StandardScaler, KernelCenterer
from sklearn.linear_model import Ridge
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics.pairwise import rbf_kernel


def main():
    previous = verify_previous()
    cfg = read(ROOT/"model_run_config.json")
    for name, expected in cfg["files"].items():
        assert sha(STUDY/name) == expected, name
    data = read(STUDY/"learning_curves_2026-11-13/dataset.json")
    index = {row["name"]: i for i, row in enumerate(data)}
    groups = np.array([row["group"] for row in data])
    y = np.log([[row["targets"][target] for target in TARGETS] for row in data])
    cases = read(ROOT/"corpus.json")
    records = read(ROOT/"model_checkpoints.json")
    max_prediction, max_loss, max_margin = 0., 0., 0.
    numerical, all_outer = 0, 0
    chosen_folds = {("original", "old/cycle"), ("fixed_noise", "new/q6_P00"), ("mixed_noise", "new/q4_P03")}
    for row in records:
        train = np.array([index[n] for n in row["train_names"]])
        test = np.array([index[n] for n in row["test_names"]])
        assert set(train).isdisjoint(test) and row["held"] not in set(groups[train])
        assert set(groups[test]) == {row["held"]}
        allowed = np.array([r["source"] == "pilot" if row["domain"] == "original" else
                            (r["p"] == .001 if row["domain"] == "fixed_noise" else True) for r in data])
        assert set(train) == set(np.flatnonzero(allowed & (groups != row["held"])))
        error = np.abs(np.array(row["predicted_log"])-y[test]).mean(axis=0)
        assert np.allclose(error, row["heldout_mae_log"], atol=1e-12, rtol=0)
        all_outer += 1
        if (row["domain"], row["held"]) not in chosen_folds:
            continue
        columns = SETS[row["feature_set"]]
        x = np.log1p([[densities(r["features"])[c] for c in columns] for r in data])
        candidates = row["candidates"]
        loss_by_group, under_by_group = [], []
        for group in sorted(set(groups[train])):
            inside, valid = train[groups[train] != group], train[groups[train] == group]
            scaler = StandardScaler().fit(x[inside])
            z, zv = scaler.transform(x[inside]), scaler.transform(x[valid])
            center = y[inside].mean(axis=0)
            predicted = []
            for alpha, multiplier in candidates:
                if row["kind"] == "linear":
                    fit = Ridge(alpha=alpha).fit(z, y[inside])
                    value = fit.predict(zv)
                else:
                    gamma = multiplier/len(columns)
                    kernel_center = KernelCenterer().fit(rbf_kernel(z, z, gamma=gamma))
                    kernel = kernel_center.transform(rbf_kernel(z, z, gamma=gamma))
                    evaluation = kernel_center.transform(rbf_kernel(zv, z, gamma=gamma))
                    fit = KernelRidge(alpha=alpha, kernel="precomputed").fit(kernel, y[inside]-center)
                    value = fit.predict(evaluation)+center
                predicted.append(value)
            predicted = np.array(predicted)
            loss_by_group.append(np.abs(predicted-y[valid][None, :, :]).mean(axis=1))
            under_by_group.append((y[valid][None, :, :]-predicted).max(axis=1))
        losses = np.mean(loss_by_group, axis=0)
        under = np.max(under_by_group, axis=0)
        max_loss = max(max_loss, float(np.max(np.abs(losses-row["inner_losses"]))))
        selected = np.argmin(losses, axis=0)
        assert [candidates[i] for i in selected] == row["chosen"]
        margins = np.exp(np.maximum(0, [under[selected[t], t] for t in range(2)]))
        max_margin = max(max_margin, float(np.max(np.abs(margins-row["margins"]))))
        scaler = StandardScaler().fit(x[train])
        z, zt = scaler.transform(x[train]), scaler.transform(x[test])
        outputs = []
        for target, (alpha, multiplier) in enumerate(row["chosen"]):
            center = y[train, target].mean()
            if row["kind"] == "linear":
                value = Ridge(alpha=alpha).fit(z, y[train, target]).predict(zt)
            else:
                gamma = multiplier/len(columns)
                kc = KernelCenterer().fit(rbf_kernel(z, z, gamma=gamma))
                fit = KernelRidge(alpha=alpha, kernel="precomputed").fit(kc.transform(rbf_kernel(z, z, gamma=gamma)), y[train, target]-center)
                value = fit.predict(kc.transform(rbf_kernel(zt, z, gamma=gamma)))+center
            outputs.append(value)
        max_prediction = max(max_prediction, float(np.max(np.abs(np.stack(outputs, axis=1)-row["predicted_log"]))))
        numerical += 1
    assert max_prediction < 1e-8 and max_loss < 1e-8 and max_margin < 1e-6
    assert all_outer == 186 and numerical == 18
    summary = read(ROOT/"model_summary.json")
    for value in summary["rows"]:
        selected = [r for r in records if r["domain"] == value["domain"] and r["model"] == value["model"]]
        t = TARGETS.index(value["target"])
        expected = np.exp(np.mean([r["heldout_mae_log"][t] for r in selected]))
        assert np.isclose(expected, value["heldout_error_factor"], rtol=1e-13)
    save(ROOT/"model_audit.json", dict(passed=True, internal_check_only=True, outer_metrics_and_splits_checked=all_outer,
         separate_sklearn_nested_reproductions=numerical, max_log_prediction_difference=max_prediction,
         max_inner_loss_difference=max_loss, max_margin_absolute_difference=max_margin, previous_manifests_verified=previous))
    print(read(ROOT/"model_audit.json"))


if __name__ == "__main__":
    main()
