"""Independent saved-output audit; no decoder calls or random fault sampling."""
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import stim

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
INPUT = STUDY / "failure_target_2026-11-17" / "construction_probe"


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    frozen, result = read(ROOT / "frozen.json"), read(ROOT / "run_result.json")
    for name, digest in frozen["files"].items():
        assert sha(Path(name)) == digest, name
    assert sha(ROOT / "frozen.json") == result["frozen_sha256"]
    assert read(ROOT / "pre_run_audit.json")["passed"]
    assert read(ROOT / "adapter_result.json")["passed"]
    h, l = sp.load_npz(INPUT / "H.npz"), sp.load_npz(INPUT / "L.npz")
    panel, jobs = read(ROOT / "panel.json"), read(ROOT / "jobs.json")
    mapping = read(ROOT / "fault_mapping.json")
    log = [json.loads(line) for line in (ROOT / "invocations.jsonl").read_text().splitlines()]
    starts = [r for r in log if r["event"] == "start"]
    decode_starts = [r for r in log if r["event"] == "decode_start"]
    rows = [r for r in log if r["event"] == "complete"]
    assert len(starts) == len(decode_starts) == len(rows) == result["decoder_calls"] == 525
    assert [x["index"] for x in rows] == list(range(525))
    assert [x["index"] for x in decode_starts] == list(range(525))
    assert len(rows) < frozen["limits"]["invocations"]
    assert result["cpu_seconds"] < frozen["limits"]["cpu_seconds"]
    assert result["wall_seconds"] < frozen["limits"]["wall_seconds"]
    assert result["status"] == "completed" and result["incomplete_decode_calls"] == 0
    panel_rows = [r for r in rows if r["phase"] == "panel"]
    assert len(panel_rows) == len(jobs) == 512
    assert len({(r["case_id"], r["config"]["name"]) for r in panel_rows}) == 512
    by_case = {(r["case_id"], r["config"]["name"]): r for r in panel_rows}
    for r, job in zip(panel_rows, jobs):
        assert r["case_id"] == job["case_id"] and r["config"] == job["config"]
    logical_nonzero = sum(bool(c["observable_support"]) for c in panel)
    support_recoveries = 0
    bp_fallbacks = 0
    for r in rows:
        obj = read(ROOT / "calls" / f"{r['index']:04d}.json")
        data = np.load(ROOT / "calls" / f"{r['index']:04d}.npz")
        correction, bp = data["correction"], data["bp"]
        assert sha_bytes(correction) == r["correction_sha256"]
        assert sha_bytes(bp) == r["bp_sha256"]
        assert np.isin(correction, [0,1]).all() and np.isin(bp, [0,1]).all()
        if r["phase"] == "adapter_toy":
            current_h = np.array([[1,1,0], [0,1,1]], dtype=np.uint8)
            current_l = np.array([[1,1,1]], dtype=np.uint8)
        else:
            current_h, current_l = h, l
        calculated_syndrome = np.asarray(current_h @ correction).ravel() % 2
        calculated_logical = np.asarray(current_l @ correction).ravel() % 2
        invalid = int(np.count_nonzero(calculated_syndrome != data["syndrome"]))
        logical = int(np.count_nonzero(calculated_logical != data["actual"]))
        expected = "invalid_correction" if invalid else "logical_failure" if logical else "correct"
        assert r["outcome"] == expected and r["syndrome_residual"] == invalid and r["logical_difference"] == logical
        assert np.array_equal(calculated_logical, data["predicted"])
        assert expected == "correct"
        if not r["forced"] and not r["zero_syndrome"] and r["bp_converged"]:
            assert np.array_equal(bp, correction), "Unexpected early-return behavior"
        if r["forced"] and not r["zero_syndrome"]:
            stats = obj["statistics"]
            assert len(stats["individual_cluster_stats"]) > 0
            assert r["postprocessing_observed"]
            assert stats["lsd_order"] == r["order"]
        if r["phase"] == "panel":
            c = panel[r["case_id"]]
            assert np.flatnonzero(data["syndrome"]).tolist() == c["syndrome_support"]
            assert np.flatnonzero(data["actual"]).tolist() == c["observable_support"]
            support_recoveries += int(np.flatnonzero(correction).tolist() == c["columns"])
            bp_fallbacks += int(not r["bp_converged"])
    assert read(ROOT / "selected_pairs.json") == []
    assert not any(r["phase"] in ("replay", "forced_comparison") for r in rows)

    # Replay exactly specified raw DEM faults through Stim, independently of H/L
    # arithmetic. Choosing one representative per signature realizes each merged
    # injection; it does not assert a unique physical-circuit fault realization.
    dem = stim.DetectorErrorModel.from_file(INPUT / "bb144_r12_p0.001_z.dem")
    raw = np.zeros((128, dem.num_errors), dtype=np.bool_)
    expected_syndrome = np.zeros((128, h.shape[0]), dtype=np.bool_)
    expected_logical = np.zeros((128, l.shape[0]), dtype=np.bool_)
    for c in panel:
        i = c["case_id"]
        for col in c["columns"]:
            raw[i, mapping[str(col)]["raw_events"][0]["raw_error_index"]] = True
        expected_syndrome[i, c["syndrome_support"]] = True
        expected_logical[i, c["observable_support"]] = True
    actual_syndrome, actual_logical, replayed = dem.compile_sampler(seed=2026111714).sample(
        shots=128, recorded_errors_to_replay=raw, return_errors=True
    )
    assert np.array_equal(raw, replayed)
    assert np.array_equal(actual_syndrome, expected_syndrome)
    assert np.array_equal(actual_logical, expected_logical)
    np.savez_compressed(ROOT / "stim_deterministic_replay.npz", raw_faults=raw,
                        syndrome=actual_syndrome, observable=actual_logical)

    comparisons = {}
    for a, b in (("exact30", "exact100"), ("additive30", "additive100"),
                 ("exact30", "additive30"), ("exact100", "additive100")):
        comparisons[f"{a}_vs_{b}"] = dict(
            changed_corrections=sum(by_case[i,a]["correction_sha256"] != by_case[i,b]["correction_sha256"] for i in range(128)),
            changed_classifications=sum(by_case[i,a]["outcome"] != by_case[i,b]["outcome"] for i in range(128)))
    configurations = {}
    for cfg in frozen["configs"]:
        subset = [r for r in panel_rows if r["config"] == cfg]
        assert len(subset) == 128
        configurations[cfg["name"]] = dict(
            correct=sum(r["outcome"] == "correct" for r in subset),
            bp_nonconverged_then_lsd_correct=sum(not r["bp_converged"] for r in subset),
            bp_iteration_range=[min(r["bp_iterations"] for r in subset), max(r["bp_iterations"] for r in subset)],
            median_decode_ms=float(np.median([r["decode_wall_ns"] for r in subset]))/1e6,
            median_initialization_ms=float(np.median([r["init_wall_ns"] for r in subset]))/1e6)
    previous = {}
    names = list(read(STUDY / "failure_target_2026-11-17/probe_audit.json")["prior_manifests_verified"])
    names.append("failure_target_2026-11-17/manifest.json")
    for name in names:
        p = STUDY / name
        files = read(p)["files"]
        for relative, digest in files.items():
            assert sha(p.parent / relative) == digest, (name, relative)
        previous[name] = len(files)
    audit = dict(passed=True, completed_decoder_calls=525, adapter_calls=13, panel_calls=512,
        distinct_supports=128, cases_with_nonzero_true_logical_flips=logical_nonzero,
        exact_injected_support_recovered_calls=support_recoveries,
        bp_nonconvergence_with_successful_lsd_calls=bp_fallbacks,
        panel_configurations=configurations, paired_sensitivity=comparisons,
        deterministic_stim_replays=128, new_random_noise_samples=0,
        forced_comparator_adapter_valid=True, witness_found=False,
        post_panel_decoder_calls=0, previous_manifests_verified=previous,
        frozen_sha256=sha(ROOT / "frozen.json"), audit_source_sha256=sha(Path(__file__)),
        conclusion="No full-decoder failure on this fixed panel; stop local search as inconclusive for rare failure existence. No repair-headroom experiment triggered.")
    (ROOT / "result_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k:v for k,v in audit.items() if k not in ("previous_manifests_verified", "panel_configurations")}))
    print(json.dumps(configurations))


def sha_bytes(data):
    return hashlib.sha256(data.tobytes()).hexdigest()


if __name__ == "__main__":
    main()
