"""Replay every bridge physical stream and check all packed correction vectors."""
import importlib
from pathlib import Path
from scipy.stats import beta
from common import *


def main():
    import stim
    previous = verify_previous()
    cfg = read(ROOT/"bridge_config.json")
    for name, expected in cfg["files"].items():
        assert sha(STUDY/name) == expected, name
    for name, expected in read(ROOT/"analysis_lock.json")["files"].items():
        assert sha(ROOT/name) == expected, name
    for module, expected in cfg["binaries"].items():
        assert sha(Path(importlib.import_module(module).__file__)) == expected["sha256"]
    corpus = read(ROOT/"corpus.json")
    result = read(ROOT/"bridge_analysis.json")
    summaries = {(r["name"], r["setting"]): r for r in result["summaries"]}
    correction_count, physical_eval, physical_profile = 0, 0, 0
    case_arrays = {}
    pids = []
    for session in range(3):
        session_path = ROOT/"results"/f"session_{session}"
        session_summary = read(session_path/"session_summary.json")
        pids.append(session_summary["pid"])
        session_eval, session_calls = 0, 0
        for case in corpus:
            h, l, _ = load_matrices(case)
            for suffix, expected in case["files"].items():
                assert sha(ROOT/"circuits"/(case["name"]+suffix)) == expected
            circuit = stim.Circuit((ROOT/"circuits"/(case["name"]+".stim")).read_text())
            settings = ["whole30", "whole100"]+(["components30"] if case["name"] == "d5_q2_memory_none" else [])
            cpu_total = 0
            lengths = []
            for phase, setting in [("profiling", None)]+[("evaluation", setting) for setting in settings]:
                path = session_path/phase/(case["name"]+("__"+setting if setting else "")+".npz")
                meta = read(path.with_suffix(".json"))
                assert meta["file_sha256"] == sha(path)
                assert meta["config_sha256"] == sha(ROOT/"bridge_config.json")
                assert meta["seed"] == seed("bridge_profile" if phase == "profiling" else "bridge_eval", session, case["name"])
                planned = 64 if phase == "profiling" else 512
                detectors, observables = circuit.compile_detector_sampler(seed=meta["seed"]).sample(planned, separate_observables=True)
                with np.load(path) as archive:
                    a = {key: archive[key] for key in archive.files}
                n = len(a["wall_ns"])
                assert n == meta["shots"] and 0 < n <= planned
                assert np.all(a["wall_ns"] > 0) and np.all(a["cpu_ns"] >= 0)
                detectors, observables = detectors[:n], observables[:n]
                assert int(a["correction_columns"]) == h.shape[1]
                corrections = np.unpackbits(a["corrections_packed"], axis=1, count=h.shape[1])
                assert np.array_equal((h@corrections.T).T % 2, detectors)
                failures = np.any((l@corrections.T).T % 2 != observables, axis=1)
                assert np.array_equal(failures, a["logical_z_failure"])
                assert np.array_equal(detectors.sum(axis=1), a["syndrome_weight"])
                assert np.array_equal(detectors.any(axis=1), a["bp_flag_valid"])
                assert np.all(a["bp_iterations"][~a["bp_flag_valid"]] == -1)
                assert np.isclose(np.quantile(a["wall_ns"], .95), meta["p95_wall_ns"], rtol=1e-13)
                assert failures.sum() == meta["logical_z_failures"]
                correction_count += n
                if phase == "profiling":
                    physical_profile += n
                else:
                    lengths.append(n)
                    assert n % 64 == 0 and meta["completed_blocks"] == n//64
                    assert meta["censored"] == (n < 512)
                    case_arrays.setdefault((case["name"], setting), []).append(a)
                    cpu_total += int(a["cpu_ns"].sum())
                    session_calls += n
                    if setting == "whole30":
                        session_eval += n
            assert len(set(lengths)) == 1
            for setting in settings:
                meta = read(session_path/"evaluation"/(case["name"]+"__"+setting+".json"))
                assert cpu_total == meta["resource_cpu_ns"]
                if meta["censored"]:
                    assert cpu_total >= cfg["evaluation_cpu_cap_ns"]
        assert session_eval == session_summary["physical_evaluation_shots"]
        assert session_calls == session_summary["evaluation_decoder_calls"]
        physical_eval += session_eval
    assert len(set(pids)) == 3
    for key, chunks in case_arrays.items():
        row = summaries[key]
        values = np.concatenate([a["wall_ns"] for a in chunks])
        failures = np.concatenate([a["logical_z_failure"] for a in chunks])
        assert row["shots"] == len(values)
        assert np.isclose(row["p95_wall_ns"], np.quantile(values, .95), rtol=1e-13)
        assert row["logical_z_failures"] == failures.sum()
        if row["setting"] == "whole30" and not row["censored"]:
            k, n = int(failures.sum()), len(failures)
            upper = 1. if k == n else float(beta.ppf(1-.05/19, k+1, n-k))
            assert row["logical_z_upper"] == upper
            assert row["screen_qualified"] == (upper <= .01)
    # Check every declared budget's primary raw/padded admission against raw samples.
    predictions = read(ROOT/"bridge_predictions.json")
    for row in result["budget_sweep"]:
        computed = dict(admitted=0, confident_false_admissions=0, confident_conservative_rejections=0,
                        qualified_admitted=0, qualified_confident_false_admissions=0, qualified_confident_conservative_rejections=0)
        for detail in row["details"]:
            name = detail["name"]
            values = np.concatenate([a["wall_ns"] for a in case_arrays[name, "whole30"]])
            misses = int((values > row["budget_ms"]*1e6).sum())
            assert detail["miss_fraction"] == misses/len(values)
            if row["policy"].startswith("profile_"):
                estimate = result["profiling"][name]["p95_ns" if row["policy"] == "profile_point" else "p95_upper_ns"]
            else:
                model, mode = row["policy"].split("/")
                estimate = predictions[name][model][mode+"_ns"][1]
            admitted = estimate is not None and estimate <= row["budget_ms"]*1e6
            assert admitted == detail["admitted"]
            ci = detail["interval"]
            qualified = summaries[name, "whole30"]["screen_qualified"]
            false = bool(ci and admitted and ci[0] > .05)
            rejection = bool(ci and not admitted and ci[1] < .05)
            for k,v in (("admitted", admitted), ("confident_false_admissions", false),
                        ("confident_conservative_rejections", rejection), ("qualified_admitted", admitted and qualified),
                        ("qualified_confident_false_admissions", false and qualified),
                        ("qualified_confident_conservative_rejections", rejection and qualified)):
                computed[k] += int(v)
        assert all(row[k] == v for k,v in computed.items())
    assert physical_eval == result["physical_evaluation_shots"] == 29184
    assert physical_profile == result["physical_profiling_shots"] == 3648
    assert correction_count == 63552
    # Verify that the alternative BP budget really is configured as intended.
    from bridge import Whole
    h, _, priors = load_matrices(corpus[0])
    assert Whole(h, priors, 30, cfg["decoder"]).decoder.max_iter == 30
    assert Whole(h, priors, 100, cfg["decoder"]).decoder.max_iter == 100
    audit = dict(passed=True, internal_only=True, previous_manifests_verified=previous,
         physical_evaluation_samples_replayed=physical_eval, physical_profiling_samples_replayed=physical_profile,
         correction_vectors_checked=correction_count, fresh_process_ids=pids,
         raw_budget_metrics_checked=len(result["budget_sweep"]), declared_analysis_hashes_match=True,
         decoder_configuration_checked=True, compiled_backend_hashes_match=True,
         reserved_test_parents_used=False)
    save(ROOT/"bridge_audit.json", audit)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
