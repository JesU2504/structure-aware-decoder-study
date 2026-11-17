"""Frozen bounded witness pilot; prepare before run. See PROTOCOL.md."""
from __future__ import annotations

import time
START_CPU, START_WALL = time.process_time(), time.monotonic()
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import sys
import sysconfig

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
PREVIOUS = STUDY / "failure_target_2026-11-17"
INPUT = PREVIOUS / "construction_probe"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["MPLCONFIGDIR"] = str(ROOT / "runtime_cache")
sys.dont_write_bytecode = True
import numpy as np
import scipy.sparse as sp


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def parity(matrix, indices):
    return np.asarray(matrix[:, indices].sum(axis=1)).ravel().astype(np.uint8) % 2


def load_inputs():
    h, l = sp.load_npz(INPUT / "H.npz"), sp.load_npz(INPUT / "L.npz")
    h, l = h.tocsc(), l.tocsc()
    return h, l, {"exact": np.load(INPUT / "priors.npy"),
                  "additive": np.load(INPUT / "repository_additive_priors.npy")}


def spatial_key(h, support):
    # Detector-only label translations: relatedness flag, not full-code orbit.
    columns = [h.indices[h.indptr[c]:h.indptr[c+1]] for c in support]
    candidates = []
    for dx in range(12):
        for dy in range(6):
            moved = [tuple(sorted(int(t//72*72 + ((t%72//6+dx)%12)*6 + ((t%6+dy)%6))
                                  for t in col)) for col in columns]
            candidates.append(tuple(sorted(moved)))
    return hashlib.sha256(repr(min(candidates)).encode()).hexdigest()


CONFIGS = [dict(name=f"{prior}{cap}", prior=prior, max_iter=cap)
           for prior in ("exact", "additive") for cap in (30, 100)]


def prepare():
    assert not (ROOT / "frozen.json").exists(), "Preserve the existing frozen panel"
    prior_manifest = read(PREVIOUS / "manifest.json")
    for name, digest in prior_manifest["files"].items():
        assert sha(PREVIOUS / name) == digest, name
    h, l, priors = load_inputs()
    assert h.shape == (936, 8784) and l.shape == (12, 8784)
    csr = h.tocsr()
    signatures = read(INPUT / "column_signatures.json")
    signature_ids = {(tuple(d), tuple(o)): i for i, (d, o) in enumerate(signatures)}
    import stim
    dem = stim.DetectorErrorModel.from_file(INPUT / "bb144_r12_p0.001_z.dem")
    raw_map = [[] for _ in signatures]
    raw_id = 0
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        ds, obs = set(), set()
        for t in inst.targets_copy():
            if t.is_relative_detector_id():
                ds.symmetric_difference_update([t.val])
            elif t.is_logical_observable_id():
                obs.symmetric_difference_update([t.val])
            else:
                assert t.is_separator()
        j = signature_ids[(tuple(sorted(ds)), tuple(sorted(obs)))]
        raw_map[j].append({"raw_error_index": raw_id, "probability": inst.args_copy()[0]})
        raw_id += 1
    assert raw_id == dem.num_errors == 10368 and all(raw_map)
    selected, seen = [], set()
    for half, seed in (("connected", 2026111711), ("uniform", 2026111712)):
        rng = np.random.Generator(np.random.PCG64(seed))
        count, attempts = 0, 0
        while count < 64:
            attempts += 1
            assert attempts <= 10000
            if half == "connected":
                growth = [int(rng.integers(h.shape[1]))]
                while len(growth) < 4:
                    detectors = set()
                    for j in growth:
                        detectors.update(h.indices[h.indptr[j]:h.indptr[j+1]])
                    neighbors = set()
                    for i in detectors:
                        neighbors.update(csr.indices[csr.indptr[i]:csr.indptr[i+1]])
                    available = sorted(neighbors-set(growth))
                    if not available:
                        break
                    growth.append(int(rng.choice(available)))
                if len(growth) != 4:
                    continue
            else:
                growth = [int(x) for x in rng.choice(h.shape[1], 4, replace=False)]
            support = tuple(sorted(growth))
            if support in seen:
                continue
            seen.add(support)
            p = priors["exact"]
            log_probability = float(np.log1p(-p).sum() + (np.log(p[list(support)])-np.log1p(-p[list(support)])).sum())
            syndrome, observable = parity(h, list(support)), parity(l, list(support))
            selected.append(dict(case_id=len(selected), half=half, seed=seed,
                                 generation_attempt=attempts, growth_order=growth, columns=list(support),
                                 syndrome_support=np.flatnonzero(syndrome).tolist(),
                                 observable_support=np.flatnonzero(observable).tolist(),
                                 syndrome_weight=int(syndrome.sum()), exact_log_probability=log_probability,
                                 detector_only_spatial_key=spatial_key(h, support)))
            count += 1
    relationships = []
    for i, a in enumerate(selected):
        for b in selected[i+1:]:
            overlap = sorted(set(a["columns"]) & set(b["columns"]))
            same_key = a["detector_only_spatial_key"] == b["detector_only_spatial_key"]
            if overlap or same_key:
                relationships.append(dict(a=a["case_id"], b=b["case_id"], shared_columns=overlap,
                                          same_detector_only_spatial_key=same_key))
    save(ROOT / "panel.json", selected)
    used = sorted({c for row in selected for c in row["columns"]})
    save(ROOT / "fault_mapping.json", {str(j): dict(signature=signatures[j], raw_events=raw_map[j]) for j in used})
    save(ROOT / "relatedness.json", {"pairs": relationships,
         "unique_detector_only_spatial_keys": len({x["detector_only_spatial_key"] for x in selected}),
         "interpretation": "Overlap and detector-only translations are relatedness flags, not independent circuit families"})
    rng = np.random.Generator(np.random.PCG64(2026111713))
    jobs = []
    for case_id in rng.permutation(128):
        for cfg_id in rng.permutation(4):
            jobs.append(dict(case_id=int(case_id), config=CONFIGS[int(cfg_id)]))
    save(ROOT / "jobs.json", jobs)
    package_dir = Path(sysconfig.get_paths()["purelib"]) / "ldpc" / "bplsd_decoder"
    module = list(package_dir.glob("_bplsd_decoder*.so"))
    assert len(module) == 1
    inputs = [INPUT / name for name in ("H.npz", "L.npz", "priors.npy", "repository_additive_priors.npy",
              "column_signatures.json", "bb144_r12_p0.001_z.stim", "bb144_r12_p0.001_z.dem")]
    paths = inputs + [PREVIOUS / "manifest.json", ROOT / "PROTOCOL.md", Path(__file__),
                     ROOT / "panel.json", ROOT / "jobs.json", ROOT / "fault_mapping.json", ROOT / "relatedness.json",
                     package_dir / "_bplsd_decoder.pyx", package_dir / "_bplsd_decoder.pxd", module[0]]
    frozen = dict(files={str(p.resolve()): sha(p) for p in paths},
                  versions={name: metadata.version(name) for name in ("ldpc", "numpy", "scipy", "stim")},
                  python=platform.python_version(), system=platform.platform(),
                  configs=CONFIGS, n_cases=128, panel_calls=512,
                  limits=dict(invocations=640, cpu_seconds=1200, wall_seconds=1800),
                  comparator=dict(method="LSD_CS", order=2, always_run_lsd=True, max_iter=30),
                  no_decoder_calls_during_preparation=True)
    assert frozen["versions"]["ldpc"] == "2.4.1"
    save(ROOT / "frozen.json", frozen)
    print(json.dumps({"panel_frozen": True, "cases": 128, "jobs": len(jobs), "files_hashed": len(paths)}))


class LimitReached(Exception):
    pass


def run():
    frozen = read(ROOT / "frozen.json")
    for name, digest in frozen["files"].items():
        assert sha(Path(name)) == digest, name
    assert not (ROOT / "invocations.jsonl").exists(), "Do not rerun or overwrite a pilot"
    from ldpc.bplsd_decoder import BpLsdDecoder
    (ROOT / "calls").mkdir()
    h, l, priors = load_inputs()
    panel, jobs = read(ROOT / "panel.json"), read(ROOT / "jobs.json")
    records = []
    limits = frozen["limits"]

    def event(value):
        with (ROOT / "invocations.jsonl").open("a") as f:
            f.write(json.dumps(value, sort_keys=True) + "\n")
            f.flush()

    def call(phase, case, cfg, matrix=h, logicals=l, channel=None, method="LSD_0", order=0,
             forced=False, stats=False):
        if len(records) >= limits["invocations"] or time.process_time()-START_CPU >= limits["cpu_seconds"] or time.monotonic()-START_WALL >= limits["wall_seconds"]:
            raise LimitReached("Declared between-call management limit reached")
        index = len(records)
        syndrome = parity(matrix, case["columns"])
        actual = parity(logicals, case["columns"])
        channel = priors[cfg["prior"]] if channel is None else channel
        event(dict(event="start", index=index, phase=phase, case_id=case["case_id"], config=cfg,
                   forced=forced, method=method, order=order,
                   run_cpu=time.process_time()-START_CPU, run_wall=time.monotonic()-START_WALL))
        c0, w0 = time.process_time_ns(), time.perf_counter_ns()
        decoder = BpLsdDecoder(matrix, error_channel=channel, max_iter=cfg["max_iter"],
            bp_method="minimum_sum", ms_scaling_factor=0.625, schedule="parallel",
            omp_thread_count=1, random_schedule_seed=0, bits_per_step=1,
            lsd_order=order, lsd_method=method, always_run_lsd=forced, input_vector_type="syndrome")
        decoder.set_do_stats(stats)
        assert decoder.lsd_order == order and decoder.lsd_method.upper() == method
        init_cpu, init_wall = time.process_time_ns()-c0, time.perf_counter_ns()-w0
        event(dict(event="decode_start", index=index))
        c0, w0 = time.process_time_ns(), time.perf_counter_ns()
        correction = np.asarray(decoder.decode(syndrome), dtype=np.uint8).copy()
        decode_cpu, decode_wall = time.process_time_ns()-c0, time.perf_counter_ns()-w0
        assert correction.shape == (matrix.shape[1],) and np.all((correction == 0) | (correction == 1))
        bp = np.asarray(decoder.bp_decoding, dtype=np.uint8).copy()
        predicted_s = np.asarray(matrix @ correction).ravel() % 2
        predicted_l = np.asarray(logicals @ correction).ravel() % 2
        residual = int(np.count_nonzero(predicted_s != syndrome))
        logical_difference = int(np.count_nonzero(predicted_l != actual))
        outcome = "invalid_correction" if residual else "logical_failure" if logical_difference else "correct"
        full_stats = decoder.statistics if stats else None
        cluster_count = len(full_stats["individual_cluster_stats"]) if full_stats else 0
        row = dict(index=index, phase=phase, case_id=case["case_id"], config=cfg,
                   method=method, order=order, forced=forced, statistics_enabled=stats,
                   zero_syndrome=not bool(syndrome.any()), bp_converged=bool(decoder.converge),
                   bp_iterations=int(decoder.iter), syndrome_residual=residual,
                   logical_difference=logical_difference, outcome=outcome,
                   init_cpu_ns=init_cpu, init_wall_ns=init_wall, decode_cpu_ns=decode_cpu,
                   decode_wall_ns=decode_wall, cluster_count=cluster_count,
                   postprocessing_observed=cluster_count > 0 if stats else None,
                   correction_sha256=hashlib.sha256(correction.tobytes()).hexdigest(),
                   bp_sha256=hashlib.sha256(bp.tobytes()).hexdigest())
        np.savez_compressed(ROOT / "calls" / f"{index:04d}.npz", correction=correction,
                            bp=bp, syndrome=syndrome, actual=actual, predicted=predicted_l,
                            llrs=np.asarray(decoder.log_prob_ratios, dtype=np.float64))
        save(ROOT / "calls" / f"{index:04d}.json", dict(row, statistics=full_stats))
        records.append(row)
        event(dict(event="complete", **row))
        return row

    def replay_equal(a, b):
        return all(a[key] == b[key] for key in ("outcome", "correction_sha256", "bp_sha256", "bp_converged", "bp_iterations"))

    status, message, selected = "running", "", []
    try:
        # Adapter calls count against the same cap. All inputs precede outcomes.
        for cfg in CONFIGS:
            for columns in ([], [0]):
                row = call("adapter_bb", dict(case_id=f"adapter_{len(records)}", columns=columns), cfg, stats=True)
                assert row["outcome"] == "correct", "BB zero/singleton adapter failed"
        toy_h = sp.csc_matrix(np.array([[1,1,0], [0,1,1]], dtype=np.uint8))
        toy_l = sp.csc_matrix(np.array([[1,1,1]], dtype=np.uint8))
        toy_case = dict(case_id="adapter_toy", columns=[1])
        toy_channel = np.full(3, 0.01)
        for method, order, forced in (("LSD_0",0,False), ("LSD_0",0,True), ("LSD_CS",2,True)):
            row = call("adapter_toy", toy_case, CONFIGS[0], matrix=toy_h, logicals=toy_l,
                       channel=toy_channel, method=method, order=order, forced=forced, stats=True)
            out = np.load(ROOT / "calls" / f"{row['index']:04d}.npz")["correction"]
            valid = [np.array([(i>>j)&1 for j in range(3)], dtype=np.uint8) for i in range(8)]
            valid = [v for v in valid if np.array_equal(toy_h @ v % 2, np.ones(2, dtype=np.uint8))]
            scores = [float(v @ np.log((1-toy_channel)/toy_channel)) for v in valid]
            assert row["outcome"] == "correct" and abs(float(out @ np.log((1-toy_channel)/toy_channel))-min(scores)) < 1e-12
            assert row["bp_converged"], "Toy must exercise BP convergence"
            assert row["postprocessing_observed"] == forced, "Forced-search branch check failed"
        for method, order in (("LSD_0",0), ("LSD_CS",2)):
            row = call("adapter_bb_forced", dict(case_id=f"adapter_forced_{order}", columns=[0]),
                       CONFIGS[0], method=method, order=order, forced=True, stats=True)
            assert row["outcome"] == "correct" and row["postprocessing_observed"]
        save(ROOT / "adapter_result.json", dict(passed=True, invocations=len(records),
             forced_after_bp_convergence_verified=True, comparator="Forced LSD_0 and LSD_CS order 2"))
        print(json.dumps({"adapters_passed": True, "counted_invocations": len(records)}), flush=True)

        baseline = {}
        for ji, job in enumerate(jobs):
            case = panel[job["case_id"]]
            row = call("panel", case, job["config"])
            baseline[case["case_id"], job["config"]["name"]] = row
            if (ji+1) % 64 == 0:
                print(json.dumps({"panel_completed": ji+1, "failures_so_far": sum(x["outcome"] != "correct" for x in baseline.values()),
                                  "run_cpu_seconds": time.process_time()-START_CPU}), flush=True)
        failed = [c for c in panel if any(baseline[c["case_id"], cfg["name"]]["outcome"] != "correct" for cfg in CONFIGS)][:8]
        successes = [c for c in panel if all(baseline[c["case_id"], cfg["name"]]["outcome"] == "correct" for cfg in CONFIGS)]
        used_controls = set()
        pairs = []
        for case in failed:
            candidates = [c for c in successes if c["case_id"] not in used_controls]
            control = min(candidates, key=lambda c: (c["half"] != case["half"], abs(c["syndrome_weight"]-case["syndrome_weight"]),
                          abs(c["exact_log_probability"]-case["exact_log_probability"]), c["case_id"])) if candidates else None
            pairs.append(dict(failure=case["case_id"], control=control["case_id"] if control else None,
                              same_half=bool(control and control["half"]==case["half"]),
                              syndrome_weight_difference=control["syndrome_weight"]-case["syndrome_weight"] if control else None))
            selected.append(case)
            if control:
                selected.append(control)
                used_controls.add(control["case_id"])
        save(ROOT / "selected_pairs.json", pairs)
        for case in selected:
            configs = CONFIGS[:2].copy()
            bad = next((cfg for cfg in CONFIGS if baseline[case["case_id"], cfg["name"]]["outcome"] != "correct"), None)
            if bad and bad not in configs:
                configs.append(bad)
            for cfg in configs:
                row = call("replay", case, cfg)
                assert replay_equal(baseline[case["case_id"], cfg["name"]], row), "Deterministic replay mismatch"
            for prior in ("exact", "additive"):
                for method, order in (("LSD_0",0), ("LSD_CS",2)):
                    cfg = dict(name=f"{prior}30", prior=prior, max_iter=30)
                    row = call("forced_comparison", case, cfg, method=method, order=order, forced=True, stats=True)
                    assert row["zero_syndrome"] or row["postprocessing_observed"], "Forced path not verified"
        status = "completed"
        message = "Fixed panel complete; no failure found, stop local search as inconclusive" if not failed else "Fixed panel, selected replays and forced comparisons complete"
    except LimitReached as exc:
        status, message = "resource_stopped", str(exc)
    except Exception as exc:
        status, message = "error_stopped", f"{type(exc).__name__}: {exc}"
        raise
    finally:
        panel_rows = [x for x in records if x["phase"] == "panel"]
        journal = [json.loads(line) for line in (ROOT / "invocations.jsonl").read_text().splitlines()]
        started_calls = sum(x["event"] == "decode_start" for x in journal)
        summary = dict(status=status, message=message, invocations_completed=len(records),
                       panel_calls_completed=len(panel_rows), selected_cases=[c["case_id"] for c in selected],
                       cpu_seconds=time.process_time()-START_CPU, wall_seconds=time.monotonic()-START_WALL,
                       counts={cfg["name"]: {o: sum(r["outcome"]==o and r["config"]["name"]==cfg["name"] for r in panel_rows)
                               for o in ("correct", "logical_failure", "invalid_correction")} for cfg in CONFIGS},
                       frozen_sha256=sha(ROOT / "frozen.json"), decoder_calls=started_calls,
                       incomplete_decode_calls=started_calls-len(records),
                       physical_monte_carlo_samples=0, training_samples=0,
                       interpretation="Enriched merged-DEM support stress panel; no natural LER or p95 inference")
        save(ROOT / "run_result.json", summary)
        print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("prepare", "run"):
        raise SystemExit("Usage: pilot.py prepare|run")
    prepare() if sys.argv[1] == "prepare" else run()
