from pathlib import Path
import hashlib
import json
import os
import time
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
BASE = ["distance", "n_detectors", "n_faults", "nnz", "prior_sum", "expected_activity"]
DENSITY = BASE+["mean_mechanism_prior", "expected_activity_density"]
STRUCTURE = ["row_degree_var", "col_degree_var", "row_degree_p95", "col_degree_p95",
             "hyperedge_fraction", "components", "largest_component_fraction", "component_size_second_moment"]
SETS = dict(base6=BASE, density8=DENSITY, graph16=DENSITY+STRUCTURE)
ALPHAS = [.0001, .001, .01, .1, 1., 10., 100., 1000., 10000.]
GAMMAS = [.01, .1, 1., 10.]
TARGETS = ["mean_ns", "p95_ns"]
BUDGET_MS = [.25, .5, 1., 2., 4., 5., 8., 16., 32.]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed(*parts):
    return int.from_bytes(hashlib.sha256(json.dumps(parts).encode()).digest()[:8], "little")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")
    temporary.replace(path)


def verify_previous():
    output = {}
    for path in (STUDY/"artifact_manifest.json", STUDY/"artifact_manifest_2026-11-13.json",
                 STUDY/"stress_gate/manifest.json", STUDY/"fit_diagnostic_2026-11-13/manifest.json",
                 STUDY/"learning_curves_2026-11-13/manifest.json", STUDY/"reviewer_perspective_2026-11-13/manifest.json"):
        files = read(path)["files"]
        for name, expected in files.items():
            assert sha(path.parent/name) == expected, (path, name)
        output[str(path.relative_to(STUDY))] = len(files)
    return output


def densities(features):
    f = dict(features)
    f["mean_mechanism_prior"] = f["prior_sum"]/f["n_faults"]
    f["expected_activity_density"] = f["expected_activity"]/f["n_detectors"]
    return f


def features(distance, h, priors):
    t = time.perf_counter_ns()
    f = dict(distance=distance, n_detectors=h.shape[0], n_faults=h.shape[1], nnz=h.nnz,
             prior_sum=float(priors.sum()), expected_activity=float((-.5*np.expm1(h@np.log1p(-2*priors))).sum()))
    f = densities(f)
    base_time = time.perf_counter_ns()-t
    csr = h.tocsr()
    rd, cd = np.diff(csr.indptr), np.diff(h.indptr)
    n, labels = connected_components(sp.bmat([[None, h], [h.T, None]], format="csr"), directed=False)
    counts = np.bincount(labels[:h.shape[0]], minlength=n)
    active = counts > 0
    f.update(row_degree_var=float(rd.var()), col_degree_var=float(cd.var()),
             row_degree_p95=float(np.quantile(rd, .95)), col_degree_p95=float(np.quantile(cd, .95)),
             hyperedge_fraction=float(np.mean(cd > 2)), components=int(active.sum()),
             largest_component_fraction=float(counts.max()/h.shape[0]),
             component_size_second_moment=float(np.sum((counts[active]/h.shape[0])**2)))
    return f, dict(base_density_ns=base_time, full_stable_ns=time.perf_counter_ns()-t)


def load_matrices(case):
    a = np.load(ROOT/"circuits"/(case["name"]+".npz"))
    h = sp.csc_matrix((a["h_data"], a["h_indices"], a["h_indptr"]), shape=a["h_shape"])
    l = sp.csc_matrix((a["l_data"], a["l_indices"], a["l_indptr"]), shape=a["l_shape"])
    return h, l, a["priors"]


def rbf(x, z, gamma):
    distance = np.maximum(0., np.sum(x*x, axis=1)[:, None]+np.sum(z*z, axis=1)[None, :]-2*x@z.T)
    return np.exp(-gamma*distance)


def predict_payload(payload, f):
    result = []
    x = np.log1p([f[c] for c in payload["columns"]])
    z = (x-np.array(payload["center"]))/np.array(payload["scale"])
    for target in payload["targets"]:
        if payload["kind"] == "linear":
            value = z@np.array(target["coef"])
        else:
            k = rbf(z[None, :], np.array(payload["train_z"]), target["gamma"])[0]
            kc = k-k.mean()-np.array(target["kernel_column_mean"])+target["kernel_grand_mean"]
            value = kc@np.array(target["dual"])
        result.append(float(value+target["target_mean"]))
    return np.array(result)
