"""Bounded construction and semantic gate; no decoder calls."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import time
import hashlib
import importlib.metadata as metadata
import json
import platform
import signal
from collections import Counter

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources" / "Adaptive-qLDPC-8cc3201"
OUT = ROOT / "entry"
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
os.environ["MPLCONFIGDIR"] = str(ROOT / "runtime_cache")
sys.dont_write_bytecode = True
import numpy as np
import scipy.sparse as sp
import stim


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def gf2_rank(matrix):
    csr = sp.csr_matrix(matrix)
    pivots = {}
    for i in range(csr.shape[0]):
        support = [int(j) for j,v in zip(csr.indices[csr.indptr[i]:csr.indptr[i+1]], csr.data[csr.indptr[i]:csr.indptr[i+1]]) if int(v)%2]
        word = sum(1 << j for j in support)
        while word:
            pivot = word.bit_length()-1
            if pivot in pivots:
                word ^= pivots[pivot]
            else:
                pivots[pivot] = word
                break
    return len(pivots)


def independent_convert(dem):
    ds_all, ls_all, probabilities, examples = [], [], [], []
    separators = repeated_d = repeated_l = 0
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        dc, lc = Counter(), Counter()
        for t in inst.targets_copy():
            if t.is_relative_detector_id():
                dc[t.val] += 1
            elif t.is_logical_observable_id():
                lc[t.val] += 1
            elif t.is_separator():
                separators += 1
            else:
                raise ValueError(str(t))
        rd, rl = any(v>1 for v in dc.values()), any(v>1 for v in lc.values())
        repeated_d += rd
        repeated_l += rl
        if (rd or rl) and len(examples) < 8:
            examples.append(dict(raw_error_index=len(probabilities), instruction=str(inst),
                                 repeated_detectors=rd, repeated_observables=rl))
        ds_all.append(sorted(j for j,v in dc.items() if v%2))
        ls_all.append(sorted(j for j,v in lc.items() if v%2))
        probabilities.append(inst.args_copy()[0])
    def matrix(supports, nr):
        rows, columns = [], []
        for j, support in enumerate(supports):
            rows.extend(support)
            columns.extend([j]*len(support))
        return sp.csc_matrix((np.ones(len(rows),dtype=np.uint8),(rows,columns)), shape=(nr,len(probabilities)))
    return matrix(ds_all,dem.num_detectors), matrix(ls_all,dem.num_observables), np.asarray(probabilities), dict(
        separators=separators, error_columns_with_repeated_detectors=repeated_d,
        error_columns_with_repeated_observables=repeated_l, examples=examples)


def timeout(_s, _f):
    raise TimeoutError("90-second entry limit exceeded")


def main():
    assert not OUT.exists(), "Preserve any earlier entry attempt"
    OUT.mkdir()
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(90)
    started = time.perf_counter()
    manifest = json.loads((ROOT / "source_manifest.json").read_text())
    for name, expected in manifest["files"].items():
        assert sha(SOURCE / name) == expected["sha256"]
    sys.path.insert(0,str(SOURCE))
    from failure_prediction import qldpc_circuit as qc
    code = qc._get_code("bb_144_12_12")
    hx, hz = code.hx.toarray(), code.hz.toarray()
    lz, lx = qc.z_logical_basis(code), qc.x_logical_basis(code)
    checks = dict(source_hashes=True,
        css_commutes=not np.any(hx @ hz.T % 2),
        css_encoded_dimension=144-gf2_rank(hx)-gf2_rank(hz)==12,
        z_logicals_commute=not np.any(lz @ hx.T % 2),
        x_logicals_commute=not np.any(lx @ hz.T % 2),
        z_logicals_independent=gf2_rank(np.vstack([hz,lz]))-gf2_rank(hz)==12,
        x_logicals_independent=gf2_rank(np.vstack([hx,lx]))-gf2_rank(hx)==12,
        logical_pairing_full_rank=gf2_rank(lx @ lz.T % 2)==12)
    circuit = qc.build_z_memory_circuit(code, p=0.007, rounds=24)
    dem = circuit.detector_error_model(decompose_errors=True, ignore_decomposition_failures=True)
    source = qc.detector_error_model_to_matrices(dem)
    h, l, priors, repeats = independent_convert(dem)
    source_h, source_l = source.h.tocsc(), sp.csc_matrix(source.logicals)
    source_binary_h = source_h.copy()
    source_binary_h.data = (source_binary_h.data != 0).astype(np.uint8)
    source_mod2_h = source_h.copy()
    source_mod2_h.data %= 2
    source_mod2_h.eliminate_zeros()
    rank = gf2_rank(h)
    checks.update(published_dimensions=(h.shape==(1800,12240) and l.shape==(12,12240)),
                  published_rank=rank==1794,
                  source_h_strict_binary=bool(np.isin(source_h.data,[0,1]).all()),
                  source_h_raw_matches=(source_h!=h).nnz==0,
                  source_h_mod2_matches=(source_mod2_h!=h).nnz==0,
                  source_h_nonzero_projection_matches=(source_binary_h!=h).nnz==0,
                  source_l_matches=(source_l!=l).nnz==0,
                  source_prior_exact=np.array_equal(source.error_probs,priors),
                  raw_error_count=h.shape[1]==dem.num_errors)
    # Independent parity unit case, evaluated by Stim with forced events.
    toy = stim.DetectorErrorModel("error(0.1) D0 D1 L0 ^ D1 D2 L0")
    th, tl, _, _ = independent_convert(toy)
    toy_d, toy_o, _ = toy.compile_sampler(seed=2026111720).sample(
        shots=1, recorded_errors_to_replay=np.ones((1,1),dtype=np.bool_))
    checks["independent_repeated_target_parity"] = (
        np.array_equal(np.asarray(th.sum(axis=1)).ravel()%2,toy_d[0]) and
        np.array_equal(np.asarray(tl.sum(axis=1)).ravel()%2,toy_o[0]))
    noiseless_d, noiseless_o = circuit.without_noise().compile_detector_sampler(seed=2026111721).sample(
        shots=16,separate_observables=True)
    checks["noiseless_detectors_zero"] = not np.any(noiseless_d)
    checks["noiseless_observables_zero"] = not np.any(noiseless_o)
    detector, observable, faults = dem.compile_sampler(seed=2026111722).sample(shots=64,return_errors=True)
    checks["independent_syndrome_reconstruction"] = np.array_equal(np.asarray((h@faults.astype(np.uint8).T).T)%2,detector)
    checks["independent_observable_reconstruction"] = np.array_equal(np.asarray((l@faults.astype(np.uint8).T).T)%2,observable)
    checks["source_syndrome_reconstruction"] = np.array_equal(np.asarray((source_h@faults.astype(np.uint8).T).T)%2,detector)
    checks["source_observable_reconstruction"] = np.array_equal(np.asarray((source_l@faults.astype(np.uint8).T).T)%2,observable)
    circuit.to_file(OUT / "bb144_r24_p0.007_z.stim")
    dem.to_file(OUT / "bb144_r24_p0.007_z.dem")
    for name, mat in (("H",h),("L",l),("source_H",source_h),("source_L",source_l)):
        sp.save_npz(OUT / f"{name}.npz",mat)
    np.save(OUT / "priors.npy",priors)
    np.save(OUT / "source_priors.npy",source.error_probs)
    np.savez_compressed(OUT / "css_logicals.npz",hx=hx,hz=hz,lx=lx,lz=lz)
    np.savez_compressed(OUT / "validation_samples.npz",detector=detector,observable=observable,faults=faults,
                        noiseless_detector=noiseless_d,noiseless_observable=noiseless_o)
    result = dict(status="pass" if all(checks.values()) else "fail",checks={k:bool(v) for k,v in checks.items()},
        dimensions=dict(H=list(h.shape),L=list(l.shape),rank_H=rank,H_nnz=h.nnz,L_nnz=l.nnz,
                        raw_dem_errors=dem.num_errors,qubits=circuit.num_qubits),
        source_discrepancies=dict(H_raw_nnz=(source_h!=h).nnz,H_mod2_nnz=(source_mod2_h!=h).nnz,
             H_nonzero_projection_nnz=(source_binary_h!=h).nnz,L_nnz=(source_l!=l).nnz,
             prior_entries_clipped=int(np.count_nonzero(source.error_probs!=priors))),
        repeated_targets=repeats,scope="Only Z-check extraction in source generator; logical Z-memory observables",
        source_commit=manifest["commit"],source_executed="Reviewed construction/conversion helpers only",
        sampling=dict(noiseless_circuit_validation=16,dem_validation=64,synthetic_parity_replays=1,
                      decoder_calls=0,experiment_shots=0),
        environment=dict(python=platform.python_version(),system=platform.platform(),
                         **{name:metadata.version(name) for name in ("numpy","scipy","stim","ldpc")}),
        elapsed_seconds=time.perf_counter()-started)
    save("result.json",result)
    signal.alarm(0)
    print(json.dumps(dict(status=result["status"],dimensions=result["dimensions"],
                         failed_checks=[k for k,v in checks.items() if not v],
                         source_discrepancies=result["source_discrepancies"])))
    if result["status"]!="pass":
        raise SystemExit(1)


if __name__=="__main__":
    main()
