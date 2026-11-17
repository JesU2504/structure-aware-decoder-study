"""Paired BP-budget and interleaved old/new timing calibration bridge."""
import argparse
import importlib
import importlib.metadata
import platform
import sys
import time
from datetime import datetime, timezone
from common import *


class Whole:
    def __init__(self, h, priors, iterations, config):
        from ldpc.bplsd_decoder import BpLsdDecoder
        self.decoder = BpLsdDecoder(h, error_channel=priors, **(config | {"max_iter": iterations}))
        self.decoder.set_do_stats(False)
        self.decode = self.decoder.decode

    def diagnostics(self, syndrome):
        return (int(self.decoder.iter), bool(self.decoder.converge)) if syndrome.any() else (-1, False)


class Components:
    def __init__(self, h, priors, config):
        n, labels = connected_components(sp.bmat([[None, h], [h.T, None]], format="csr"), directed=False)
        self.columns = h.shape[1]
        self.parts = []
        for component in range(n):
            rows = np.flatnonzero(labels[:h.shape[0]] == component)
            cols = np.flatnonzero(labels[h.shape[0]:] == component)
            if len(rows):
                assert len(cols)
                self.parts.append((rows, cols, Whole(h[rows][:, cols].tocsc(), priors[cols], 30, config)))
        assert sum(len(cols) for _, cols, _ in self.parts) == self.columns

    def decode(self, syndrome):
        correction = np.zeros(self.columns, dtype=np.uint8)
        for rows, cols, engine in self.parts:
            correction[cols] = engine.decode(syndrome[rows])
        return correction

    def diagnostics(self, syndrome):
        values = [engine.diagnostics(syndrome[rows]) for rows, _, engine in self.parts if syndrome[rows].any()]
        return (sum(v[0] for v in values), all(v[1] for v in values)) if values else (-1, False)


def freeze():
    assert not (ROOT/"results").exists(), "Bridge timing already exists"
    assert not (ROOT/"bridge_config.json").exists(), "Bridge already frozen"
    previous = verify_previous()
    assert read(ROOT/"model_audit.json")["passed"]
    sys.path.insert(0, str(STUDY))
    import study
    paths = [ROOT/name for name in ("PROTOCOL.md", "RESUMPTION_2026-11-15.md", "bridge.py", "common.py", "corpus.json",
             "preparation.json", "bridge_predictions.json", "model_run_config.json", "model_summary.json", "model_audit.json")]
    binaries = {}
    for module in ("ldpc.bplsd_decoder._bplsd_decoder", "ldpc.bp_decoder._bp_decoder"):
        path = Path(importlib.import_module(module).__file__)
        binaries[module] = dict(path=str(path), sha256=sha(path))
    save(ROOT/"bridge_config.json", dict(client_date="2026-11-15", timezone="Asia/Tokyo",
         frozen_utc=datetime.now(timezone.utc).isoformat(), local_provenance_only=True,
         decoder=study.DECODER_CONFIG, sessions=3, eval_blocks=8, block_shots=64, profile_shots=64,
         warmup_shots=32, evaluation_cpu_cap_ns=20_000_000_000,
         settings=["whole30", "whole100"], memory_extra_setting="components30", budget_ms=BUDGET_MS,
         files={str(p.relative_to(STUDY)): sha(p) for p in paths}, binaries=binaries,
         packages={p: importlib.metadata.version(p) for p in ("numpy", "scipy", "stim", "ldpc", "scikit-learn")},
         previous_manifests_verified=previous, no_bridge_timings_collected=True))
    print("Frozen bridge settings and predictions before timing", flush=True)


def timing_batch(engine, detectors):
    wall, cpu, corrections, iterations, convergence = [], [], [], [], []
    for syndrome in detectors:
        startw = time.perf_counter_ns()
        startc = time.process_time_ns()
        correction = engine.decode(syndrome)
        elapsedc = time.process_time_ns()-startc
        elapsedw = time.perf_counter_ns()-startw
        wall.append(elapsedw)
        cpu.append(elapsedc)
        corrections.append(correction.copy())
        it, cv = engine.diagnostics(syndrome)
        iterations.append(it)
        convergence.append(cv)
    return dict(wall_ns=np.array(wall, dtype=np.int64), cpu_ns=np.array(cpu, dtype=np.int64),
         corrections=np.array(corrections, dtype=np.uint8), bp_iterations=np.array(iterations),
         bp_converged=np.array(convergence, dtype=bool), bp_flag_valid=detectors.any(axis=1))


def save_result(path, parts, detectors, observables, h, l, metadata):
    combined = {key: np.concatenate([p[key] for p in parts]) for key in parts[0]}
    count = len(combined["wall_ns"])
    corr = combined.pop("corrections")
    det, obs = detectors[:count], observables[:count]
    assert np.array_equal((h@corr.T).T % 2, det)
    fail = np.any((l@corr.T).T % 2 != obs, axis=1)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **combined, corrections_packed=np.packbits(corr, axis=1),
         correction_columns=h.shape[1], logical_z_failure=fail, syndrome_weight=det.sum(axis=1))
    save(path.with_suffix(".json"), dict(**metadata, shots=count, logical_z_failures=int(fail.sum()),
         mean_wall_ns=float(combined["wall_ns"].mean()), p95_wall_ns=float(np.quantile(combined["wall_ns"], .95)),
         mean_cpu_ns=float(combined["cpu_ns"].mean()), p95_cpu_ns=float(np.quantile(combined["cpu_ns"], .95)),
         file_sha256=sha(path)))


def run_session(session):
    import stim
    assert session in (0, 1, 2)
    cfg = read(ROOT/"bridge_config.json")
    for name, expected in cfg["files"].items():
        assert sha(STUDY/name) == expected, name
    for module, record in cfg["binaries"].items():
        assert sha(Path(importlib.import_module(module).__file__)) == record["sha256"]
    destination = ROOT/"results"/f"session_{session}"
    assert not destination.exists(), "Session already present; do not overwrite"
    destination.mkdir(parents=True)
    begun = datetime.now(timezone.utc).isoformat()
    corpus = read(ROOT/"corpus.json")
    contexts = {}
    order = np.random.default_rng(seed("bridge_prepare_order", session)).permutation(len(corpus))
    for index in order:
        case = corpus[index]
        h, l, priors = load_matrices(case)
        for suffix, expected in case["files"].items():
            assert sha(ROOT/"circuits"/(case["name"]+suffix)) == expected
        circuit = stim.Circuit((ROOT/"circuits"/(case["name"]+".stim")).read_text())
        profile_seed = seed("bridge_profile", session, case["name"])
        detp, obsp = circuit.compile_detector_sampler(seed=profile_seed).sample(cfg["profile_shots"], separate_observables=True)
        detp = detp.astype(np.uint8)
        t = time.perf_counter_ns()
        profiler = Whole(h, priors, 30, cfg["decoder"])
        profile_init = time.perf_counter_ns()-t
        pwarm_seed = seed("bridge_profile_warm", session, case["name"])
        for syndrome in circuit.compile_detector_sampler(seed=pwarm_seed).sample(cfg["warmup_shots"]).astype(np.uint8):
            profiler.decode(syndrome)
        prof = timing_batch(profiler, detp)
        save_result(destination/"profiling"/(case["name"]+".npz"), [prof], detp, obsp, h, l,
             dict(name=case["name"], setting="whole30", phase="profile", session=session,
                  seed=profile_seed, warm_seed=pwarm_seed, init_wall_ns=profile_init,
                  config_sha256=sha(ROOT/"bridge_config.json"), censored=False))
        del profiler
        engines, initialization = {}, {}
        settings = cfg["settings"] + ([cfg["memory_extra_setting"]] if case["name"] == "d5_q2_memory_none" else [])
        warm_seed = seed("bridge_eval_warm", session, case["name"])
        warm = circuit.compile_detector_sampler(seed=warm_seed).sample(cfg["warmup_shots"]).astype(np.uint8)
        for setting in settings:
            t = time.perf_counter_ns()
            engine = (Components(h, priors, cfg["decoder"]) if setting == "components30" else
                      Whole(h, priors, 100 if setting == "whole100" else 30, cfg["decoder"]))
            initialization[setting] = time.perf_counter_ns()-t
            for syndrome in warm:
                engine.decode(syndrome)
            engines[setting] = engine
        evaluation_seed = seed("bridge_eval", session, case["name"])
        det, obs = circuit.compile_detector_sampler(seed=evaluation_seed).sample(cfg["eval_blocks"]*cfg["block_shots"], separate_observables=True)
        contexts[case["name"]] = dict(case=case, h=h, l=l, det=det.astype(np.uint8), obs=obs,
             engines=engines, initialization=initialization, seed=evaluation_seed, warm_seed=warm_seed,
             parts={setting: [] for setting in settings}, measured_cpu=0, blocks=0, stopped=False)
    for block in range(cfg["eval_blocks"]):
        ordered = list(contexts)
        np.random.default_rng(seed("bridge_block_order", session, block)).shuffle(ordered)
        for name in ordered:
            context = contexts[name]
            if context["stopped"]:
                continue
            sl = slice(block*cfg["block_shots"], (block+1)*cfg["block_shots"])
            settings = list(context["engines"])
            np.random.default_rng(seed("bridge_setting_order", session, block, name)).shuffle(settings)
            for setting in settings:
                result = timing_batch(context["engines"][setting], context["det"][sl])
                corr = result["corrections"]
                assert np.array_equal((context["h"]@corr.T).T % 2, context["det"][sl])
                context["parts"][setting].append(result)
                context["measured_cpu"] += int(result["cpu_ns"].sum())
            context["blocks"] += 1
            if context["measured_cpu"] >= cfg["evaluation_cpu_cap_ns"]:
                context["stopped"] = True
        print(json.dumps(dict(session=session, block=block+1, blocks_planned=cfg["eval_blocks"],
             completed_evaluation_shots=sum(c["blocks"]*cfg["block_shots"] for c in contexts.values()),
             capped_configurations=sum(c["stopped"] for c in contexts.values()))), flush=True)
    for name, context in contexts.items():
        censored = context["blocks"] < cfg["eval_blocks"]
        for setting, parts in context["parts"].items():
            save_result(destination/"evaluation"/(name+"__"+setting+".npz"), parts,
                 context["det"], context["obs"], context["h"], context["l"],
                 dict(name=name, setting=setting, phase="evaluation", session=session,
                      seed=context["seed"], warm_seed=context["warm_seed"],
                      init_wall_ns=context["initialization"][setting], completed_blocks=context["blocks"],
                      resource_cpu_ns=context["measured_cpu"], censored=censored,
                      config_sha256=sha(ROOT/"bridge_config.json")))
    summary = dict(session=session, client_measurement_date="2026-11-15", started_utc=begun,
         finished_utc=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), machine=platform.machine(),
         platform=platform.platform(), python=sys.version, packages=cfg["packages"],
         configured_threads={k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")},
         physical_evaluation_shots=sum(c["blocks"]*cfg["block_shots"] for c in contexts.values()),
         evaluation_decoder_calls=sum(c["blocks"]*cfg["block_shots"]*len(c["engines"]) for c in contexts.values()),
         physical_profiling_shots=len(corpus)*cfg["profile_shots"],
         physical_warmup_shots=2*len(corpus)*cfg["warmup_shots"],
         censored=[name for name,c in contexts.items() if c["blocks"] < cfg["eval_blocks"]],
         config_sha256=sha(ROOT/"bridge_config.json"))
    save(destination/"session_summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "run"])
    parser.add_argument("--session", type=int)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze()
    else:
        run_session(args.session)
