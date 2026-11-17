"""Incremental, nested group-holdout ridge experiments. See PROTOCOL.md."""
from pathlib import Path
import hashlib
import itertools
import json
import os
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
import numpy as np
from sklearn.preprocessing import StandardScaler
import importlib.metadata

ALPHAS = np.array([.0001, .001, .01, .1, 1., 10., 100., 1000., 10000.])
TARGETS = ["mean_ns", "p95_ns"]
B2 = ["distance", "n_detectors", "n_faults", "nnz", "prior_sum", "expected_activity"]
B3 = B2 + ["row_degree_var", "col_degree_var", "row_degree_p95", "col_degree_p95",
           "hyperedge_fraction", "components", "largest_component_fraction",
           "component_size_second_moment", "two_step_mean"]
MODELS = {"B2": B2, "B3": B3, "B3_stable": B3[:-1]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def check_manifests():
    result = {}
    for path in (STUDY/"artifact_manifest.json", STUDY/"artifact_manifest_2026-11-13.json",
                 STUDY/"stress_gate/manifest.json", STUDY/"fit_diagnostic_2026-11-13/manifest.json"):
        files = read(path)["files"]
        failures = [name for name, expected in files.items()
                    if not (path.parent/name).is_file() or sha(path.parent/name) != expected]
        if failures:
            raise RuntimeError(f"Changed artifacts in {path}: {failures}")
        result[str(path.relative_to(STUDY))] = len(files)
    return result


def canonical(q, gates):
    matrix = np.eye(q, dtype=np.uint8)
    for c, t in gates:
        matrix[t] ^= matrix[c]
    return min(matrix[np.ix_(p, p)].tobytes().hex() for p in itertools.permutations(range(q)))


def prepare():
    if (ROOT/"run_config.json").exists():
        return
    verified = check_manifests()
    sys.path.insert(0, str(STUDY))
    import study
    import stim
    old = read(STUDY/"corpus.json")
    old_summary = {r["name"]: r for r in read(STUDY/"results/case_summaries.json")}
    new = read(STUDY/"stress_gate/corpus.json")
    new_summary = {r["name"]: r for r in read(STUDY/"stress_gate/results/discovery_summaries_reviewed.json")}
    data, excluded, features_checked = [], [], []
    map_groups = {}
    for source, corpus, summaries in (("pilot", old, old_summary), ("discovery", new, new_summary)):
        for row in corpus:
            summary = summaries[row["name"]]
            if summary.get("censored", False):
                excluded.append(dict(name=row["name"], reason="Resource-censored discovery target"))
                continue
            case = row["case"] if source == "pilot" else row
            q = case["blocks"]
            key = (q, canonical(q, row["gates"]))
            if source == "pilot":
                family = case["family"]
                group = "old/" + ("single_repeated" if family in ("single", "repeated") else family)
                features = row["features"].copy()
                targets = {target: summary[target] for target in TARGETS}
            else:
                assert row["canonical_map"] == key[1]
                group = "new/" + row["program"]
                dem_path = STUDY/"stress_gate/circuits"/(row["name"]+".dem")
                assert sha(dem_path) == row["dem_sha256"]
                h, l, priors, _ = study.convert(stim.DetectorErrorModel(dem_path.read_text()))
                features = study.features(SimpleNamespace(**{k: case[k] for k in ("blocks", "rounds", "distance")}), h, l, priors)
                for col in B2:
                    assert np.isclose(features[col], row["features"][col], rtol=1e-11, atol=1e-10), (row["name"], col)
                features.pop("feature_time_ns", None)
                features_checked.append(row["name"])
                targets = {"mean_ns": summary["mean_wall_ns"], "p95_ns": summary["p95_wall_ns"]}
            if key in map_groups:
                assert map_groups[key] == group, (key, map_groups[key], group)
            map_groups[key] = group
            assert all(np.isfinite(features[c]) and features[c] >= 0 for c in B3)
            data.append(dict(name=row["name"], source=source, group=group, p=case["p"],
                             blocks=q, distance=case["distance"], rounds=case["rounds"],
                             features={c: features[c] for c in B3}, targets=targets,
                             shots=summary["shots"], logical_z_failure_fraction=(summary.get("logical_z_failure_fraction")
                                 if source != "pilot" else summary["logical_z_failures"]/summary["shots"])))
    assert len(data) == 125 and len(features_checked) == 47
    save(ROOT/"dataset.json", data)
    save(ROOT/"preparation.json", dict(previous_manifests_verified=verified, excluded=excluded,
         static_features_recomputed=len(features_checked), base_features_crosschecked=True,
         no_ideal_map_equivalence_crosses_groups=True,
         groups={g: dict(cases=sum(r["group"] == g for r in data),
                        fixed_noise_cases=sum(r["group"] == g and r["p"] == .001 for r in data))
                 for g in sorted({r["group"] for r in data})}))
    paths = [ROOT/"PROTOCOL.md", ROOT/"run.py", ROOT/"dataset.json", ROOT/"preparation.json",
             STUDY/"study.py", STUDY/"corpus.json", STUDY/"results/case_summaries.json",
             STUDY/"stress_gate/corpus.json", STUDY/"stress_gate/results/discovery_summaries_reviewed.json"]
    save(ROOT/"run_config.json", dict(date="2026-11-13", post_hoc=True, alphas=ALPHAS.tolist(),
         models=MODELS, targets=TARGETS, expansion_orders=10, expansion_sizes=[0, 2, 4, 6, 8, 11],
         original_sizes=[2, 3, 4, 5, 6], packages={n: importlib.metadata.version(n) for n in ("numpy", "scipy", "scikit-learn", "stim")},
         files={str(p.relative_to(STUDY)): sha(p) for p in paths}))


class Experiment:
    def __init__(self, data):
        self.data = data
        self.groups = np.array([r["group"] for r in data])
        self.y = np.log([[r["targets"][t] for t in TARGETS] for r in data])
        self.x = {m: np.log1p([[r["features"][c] for c in cols] for r in data]) for m, cols in MODELS.items()}
        self.cache = {}
        self.svd_fits = 0

    def path(self, model, train, evaluate):
        scaler = StandardScaler().fit(self.x[model][train])
        z = scaler.transform(self.x[model][train])
        ze = scaler.transform(self.x[model][evaluate])
        center = self.y[train].mean(axis=0)
        u, s, vt = np.linalg.svd(z, full_matrices=False)
        weights = s[None, :]/(s[None, :]**2 + ALPHAS[:, None])
        coefficients = np.einsum("pk,ak,kt->apt", vt.T, weights, u.T@(self.y[train]-center))
        self.svd_fits += 1
        return np.einsum("np,apt->ant", ze, coefficients) + center[None, None, :]

    def fit(self, model, train):
        key = (model, tuple(train))
        if key not in self.cache:
            losses = []
            training_groups = sorted(set(self.groups[train]))
            assert len(training_groups) >= 2
            for inner in training_groups:
                validation = train[self.groups[train] == inner]
                inside = train[self.groups[train] != inner]
                predicted = self.path(model, inside, validation)
                losses.append(np.abs(predicted-self.y[validation][None, :, :]).mean(axis=1))
            losses = np.mean(losses, axis=0)  # alpha x target; equal inner groups
            chosen = np.argmin(losses, axis=0)
            paths = self.path(model, train, np.arange(len(self.data)))
            predicted = np.stack([paths[chosen[t], :, t] for t in range(len(TARGETS))], axis=1)
            error = predicted-self.y
            group_train = np.mean([np.abs(error[train[self.groups[train] == g]]).mean(axis=0)
                                   for g in training_groups], axis=0)
            self.cache[key] = dict(predicted=predicted, selected_alphas=ALPHAS[chosen].tolist(),
                 inner_losses_by_alpha=losses.tolist(), train_mae_log_group_balanced=group_train.tolist(),
                 train_mae_log_case_weighted=np.abs(error[train]).mean(axis=0).tolist(),
                 train_rmse_log_case_weighted=np.sqrt(np.mean(error[train]**2, axis=0)).tolist())
        return self.cache[key]

    def job(self, experiment, held, size, order, train_groups, allowed):
        train = np.flatnonzero(np.isin(self.groups, train_groups) & allowed)
        test = np.flatnonzero((self.groups == held) & allowed)
        assert len(test) and not set(train).intersection(test)
        assert held not in train_groups
        result = dict(experiment=experiment, held_group=held, size=size, order=order,
                      train_groups=sorted(train_groups), train_cases=len(train), test_cases=len(test),
                      train_names=[self.data[i]["name"] for i in train],
                      test_names=[self.data[i]["name"] for i in test], models={})
        for model in MODELS:
            fit = self.fit(model, train)
            residual = fit["predicted"][test]-self.y[test]
            result["models"][model] = {k: v for k, v in fit.items() if k != "predicted"}
            result["models"][model].update(predicted_log=fit["predicted"][test].tolist(),
                heldout_mae_log=np.abs(residual).mean(axis=0).tolist(),
                heldout_rmse_log=np.sqrt(np.mean(residual**2, axis=0)).tolist())
        return result


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    start = time.monotonic()
    prepare()
    cfg = read(ROOT/"run_config.json")
    for name, expected in cfg["files"].items():
        assert sha(STUDY/name) == expected, name
    data = read(ROOT/"dataset.json")
    exp = Experiment(data)
    old = sorted({r["group"] for r in data if r["source"] == "pilot"})
    new = sorted({r["group"] for r in data if r["source"] == "discovery"})
    assert len(old) == 7 and len(new) == 12
    completed = []
    for experiment, parents in (("original", old), ("expansion_fixed_noise", new), ("expansion_mixed_noise", new)):
        allowed = np.array([r["source"] == "pilot" if experiment == "original"
                            else (r["p"] == .001 if experiment == "expansion_fixed_noise" else True) for r in data])
        for held in parents:
            name = experiment + "__" + held.replace("/", "_")
            path = ROOT/"checkpoints"/(name+".json")
            if path.exists():
                chunk = read(path)
                assert chunk["config_sha256"] == sha(ROOT/"run_config.json")
            else:
                jobs = []
                others = [g for g in parents if g != held]
                if experiment == "original":
                    for size in cfg["original_sizes"]:
                        for order, subset in enumerate(itertools.combinations(others, size)):
                            jobs.append(exp.job(experiment, held, size, order, list(subset), allowed))
                else:
                    for order in range(cfg["expansion_orders"]):
                        seed = int.from_bytes(hashlib.sha256(f"incremental_order_v1/{held}/{order}".encode()).digest()[:8], "little")
                        permutation = np.random.default_rng(seed).permutation(others).tolist()
                        for size in cfg["expansion_sizes"]:
                            jobs.append(exp.job(experiment, held, size, order, old+permutation[:size], allowed))
                chunk = dict(config_sha256=sha(ROOT/"run_config.json"), experiment=experiment, held_group=held, jobs=jobs)
                save(path, chunk)
            completed.append(name)
            progress = dict(status="running", completed_outer_groups=len(completed), total_outer_groups=31,
                            last_completed=name, elapsed_seconds=time.monotonic()-start,
                            cached_training_fits=len(exp.cache), svd_fits_this_process=exp.svd_fits,
                            decoder_shots_collected=0)
            save(ROOT/"progress.json", progress)
            print(json.dumps(progress), flush=True)
    progress.update(status="measurements_complete", previous_manifests_verified=check_manifests())
    save(ROOT/"progress.json", progress)
    print(json.dumps(progress), flush=True)


if __name__ == "__main__":
    main()
