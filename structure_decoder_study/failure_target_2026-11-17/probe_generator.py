"""Bounded construction/conversion check; see ENTRY_PROTOCOL.md. No decoding."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import signal
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import stim

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources" / "dem_trapping_sets-b9ac6a1"
OUT = ROOT / "construction_probe"
SEED_NOISELESS = 2026111701
SEED_DEM = 2026111702


def gf2_rank(matrix):
    """Independent integer-XOR elimination; no source helper linear algebra."""
    pivots = {}
    for row in np.asarray(matrix):
        word = sum(1 << int(j) for j in np.flatnonzero(row % 2))
        while word:
            p = word.bit_length() - 1
            if p in pivots:
                word ^= pivots[p]
            else:
                pivots[p] = word
                break
    return len(pivots)


def matrix_from_supports(supports, nrows):
    rows, cols = [], []
    for j, support in enumerate(supports):
        for i in support:
            rows.append(i)
            cols.append(j)
    return sp.csc_matrix(
        (np.ones(len(rows), dtype=np.uint8), (rows, cols)),
        shape=(nrows, len(supports)), dtype=np.uint8,
    )


def parse_dem(dem):
    """Track XOR parity, including repeated targets, rather than sets."""
    signatures, probabilities = [], []
    separators = 0
    for instruction in dem.flattened():
        if instruction.type != "error":
            continue
        d, l = set(), set()
        for target in instruction.targets_copy():
            if target.is_separator():
                separators += 1
                continue
            if target.is_relative_detector_id():
                support = d
            elif target.is_logical_observable_id():
                support = l
            else:
                raise ValueError(f"Unexpected error target {target}")
            if target.val in support:
                support.remove(target.val)
            else:
                support.add(target.val)
        signatures.append((tuple(sorted(d)), tuple(sorted(l))))
        probabilities.append(instruction.args_copy()[0])
    return signatures, np.asarray(probabilities), separators


def deadline(_signum, _frame):
    raise TimeoutError("90-second construction-probe limit exceeded")


def main():
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(90)
    started = time.perf_counter()
    if OUT.exists():
        raise FileExistsError("Preserve previous probe output; choose a new dated run")
    OUT.mkdir()
    manifest = json.loads((ROOT / "source_manifest.json").read_text())
    assert manifest["valid"]
    for path, expected in manifest["files"].items():
        data = (SOURCE / path).read_bytes()
        assert len(data) == expected["bytes"]
        assert hashlib.sha256(data).hexdigest() == expected["sha256"]

    # These helper imports do not import the dpl_search enumeration entry point.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(SOURCE / "examples"))
    from include_py import codes_q as codes
    from include_py import build_decoding_matrices_layered as bdm

    code, aa, bb = codes.create_bivariate_bicycle_codes(
        12, 6, [3], [1, 2], [1, 2], [3]
    )
    hx, hz = np.asarray(code.hx), np.asarray(code.hz)
    lx, lz = np.asarray(code.lx), np.asarray(code.lz)
    checks = {
        "source_hashes": True,
        "css_commutes": not np.any(hx @ hz.T % 2),
        "logical_x_commutes_with_z_checks": not np.any(lx @ hz.T % 2),
        "logical_z_commutes_with_x_checks": not np.any(lz @ hx.T % 2),
        "expected_dimensions": code.N == 144 and code.K == 12,
        "logical_pairing_full_rank": gf2_rank(lx @ lz.T % 2) == 12,
        "logical_x_independent_mod_stabilizers":
            gf2_rank(np.vstack([hx, lx])) - gf2_rank(hx) == 12,
        "logical_z_independent_mod_stabilizers":
            gf2_rank(np.vstack([hz, lz])) - gf2_rank(hz) == 12,
    }
    circuit = bdm.build_circuit(
        code, aa, bb, p=0.001, num_repeat=12,
        z_basis=True, use_both=False, HZH=False,
    )
    dem = circuit.detector_error_model()
    circuit.to_file(OUT / "bb144_r12_p0.001_z.stim")
    dem.to_file(OUT / "bb144_r12_p0.001_z.dem")

    signatures, raw_p, separators = parse_dem(dem)
    raw_h = matrix_from_supports([s[0] for s in signatures], dem.num_detectors)
    raw_l = matrix_from_supports([s[1] for s in signatures], dem.num_observables)
    checks["raw_error_count_matches_dem"] = len(signatures) == dem.num_errors
    checks["unseparated_dem"] = separators == 0
    ref_h, ref_l, ref_p, ids = bdm.dem_to_check_matrices(dem, return_col_dict=True)
    # Align to repository column IDs, but derive each support independently.
    aligned_signatures = [None] * len(ids)
    for key, column in ids.items():
        tokens = key.split()
        d = tuple(sorted(int(x[1:]) for x in tokens if x.startswith("D")))
        l = tuple(sorted(int(x[1:]) for x in tokens if x.startswith("L")))
        aligned_signatures[column] = (d, l)
    independent_ids = {s: i for i, s in enumerate(aligned_signatures)}
    checks["signature_alignment_bijective"] = (
        len(independent_ids) == len(ids) and set(signatures) == set(independent_ids)
    )
    aligned_h = matrix_from_supports([s[0] for s in aligned_signatures], dem.num_detectors)
    aligned_l = matrix_from_supports([s[1] for s in aligned_signatures], dem.num_observables)
    merged_p = np.zeros(len(ids))
    raw_to_merged = []
    for signature, p in zip(signatures, raw_p):
        j = independent_ids[signature]
        raw_to_merged.append(j)
        merged_p[j] = merged_p[j] * (1-p) + (1-merged_p[j]) * p
    checks["repository_h_matches"] = (aligned_h != ref_h).nnz == 0
    checks["repository_l_matches"] = (aligned_l != ref_l).nnz == 0
    prior_difference = float(np.max(np.abs(merged_p-ref_p)))
    checks["repository_priors_match_xor_merge"] = prior_difference < 1e-14
    counts = Counter(signatures)

    noiseless_d, noiseless_l = circuit.without_noise().compile_detector_sampler(
        seed=SEED_NOISELESS
    ).sample(shots=32, separate_observables=True)
    checks["noiseless_detectors_zero"] = not np.any(noiseless_d)
    checks["noiseless_observables_zero"] = not np.any(noiseless_l)
    syndrome, observable, faults = dem.compile_sampler(seed=SEED_DEM).sample(
        shots=256, return_errors=True
    )
    predicted_d = np.asarray((raw_h @ faults.astype(np.uint8).T).T) % 2
    predicted_l = np.asarray((raw_l @ faults.astype(np.uint8).T).T) % 2
    checks["raw_fault_syndrome_reconstruction"] = np.array_equal(predicted_d, syndrome)
    checks["raw_fault_observable_reconstruction"] = np.array_equal(predicted_l, observable)
    merged_faults = np.zeros((len(faults), len(ids)), dtype=np.uint8)
    for raw_j, merged_j in enumerate(raw_to_merged):
        merged_faults[:, merged_j] ^= faults[:, raw_j]
    checks["merged_fault_syndrome_reconstruction"] = np.array_equal(
        np.asarray((aligned_h @ merged_faults.T).T) % 2, syndrome
    )
    checks["merged_fault_observable_reconstruction"] = np.array_equal(
        np.asarray((aligned_l @ merged_faults.T).T) % 2, observable
    )

    sp.save_npz(OUT / "H.npz", aligned_h)
    sp.save_npz(OUT / "L.npz", aligned_l)
    np.save(OUT / "priors.npy", merged_p)
    np.savez_compressed(
        OUT / "validation_samples.npz", faults=faults, merged_faults=merged_faults,
        syndrome=syndrome, observable=observable,
        noiseless_syndrome=noiseless_d, noiseless_observable=noiseless_l,
    )
    (OUT / "column_signatures.json").write_text(json.dumps(aligned_signatures) + "\n")
    result = {
        "status": "pass" if all(checks.values()) else "fail",
        "scope": "generator/converter validation only; no decoder failure reproduced",
        "source_commit": manifest["commit"], "source_executed": "construction helpers only",
        "settings": {"data_qubits": 144, "logical_qubits": 12, "rounds": 12,
                     "p": 0.001, "sector": "Z memory", "HZH": False, "use_both": False},
        "dimensions": {"detectors": dem.num_detectors, "observables": dem.num_observables,
                       "raw_dem_errors": dem.num_errors, "merged_fault_columns": len(ids),
                       "H_nnz": int(aligned_h.nnz), "L_nnz": int(aligned_l.nnz),
                       "rank_hx": gf2_rank(hx), "rank_hz": gf2_rank(hz)},
        "duplicate_signatures": sum(v-1 for v in counts.values()),
        "prior_max_difference": prior_difference,
        "checks": {k: bool(v) for k, v in checks.items()},
        "sampling": {"noiseless_circuit_validation": 32, "dem_validation": 256,
                     "noiseless_seed": SEED_NOISELESS, "dem_seed": SEED_DEM,
                     "decoder_calls": 0, "training_samples": 0},
        "environment": {"python": platform.python_version(), "system": platform.platform(),
                        **{name: importlib.metadata.version(name) for name in
                           ["numpy", "scipy", "stim", "ldpc"]}},
        "probe_elapsed_seconds": time.perf_counter() - started,
        "distance_certified": False,
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    signal.alarm(0)
    print(json.dumps({"status": result["status"], "dimensions": result["dimensions"],
                      "checks_passed": sum(checks.values()), "checks_total": len(checks),
                      "scope": result["scope"]}))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
