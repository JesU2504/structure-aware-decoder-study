"""Check saved construction results independently; no resampling or decoding."""
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import stim

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
OUT = ROOT / "construction_probe"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    result = json.loads((OUT / "result.json").read_text())
    checks = result["checks"]
    assert [name for name, ok in checks.items() if not ok] == ["repository_priors_match_xor_merge"]
    dem = stim.DetectorErrorModel.from_file(OUT / "bb144_r12_p0.001_z.dem")
    signatures = json.loads((OUT / "column_signatures.json").read_text())
    lookup = {(tuple(d), tuple(l)): i for i, (d, l) in enumerate(signatures)}
    groups = [[] for _ in signatures]
    for inst in dem.flattened():
        if inst.type != "error":
            continue
        targets = inst.targets_copy()
        ds = [t.val for t in targets if t.is_relative_detector_id()]
        ls = [t.val for t in targets if t.is_logical_observable_id()]
        assert len(ds) == len(set(ds)) and len(ls) == len(set(ls))
        assert not any(t.is_separator() for t in targets)
        groups[lookup[(tuple(sorted(ds)), tuple(sorted(ls)))]].append(inst.args_copy()[0])
    assert all(groups)
    exact = np.array([0.5 * (1-np.prod(1-2*np.array(g))) for g in groups])
    additive = np.array([sum(g) for g in groups])
    saved = np.load(OUT / "priors.npy")
    assert np.allclose(exact, saved, atol=2e-16, rtol=1e-12)
    delta = additive-exact
    affected = delta > 1e-14
    # An analytic two-event check includes the probability of both events firing.
    p1, p2 = 0.01, 0.02
    assert abs((p1*(1-p2)+(1-p1)*p2) - (1-(1-2*p1)*(1-2*p2))/2) < 1e-16
    h, l = sp.load_npz(OUT / "H.npz"), sp.load_npz(OUT / "L.npz")
    samples = np.load(OUT / "validation_samples.npz")
    assert np.array_equal((h @ samples["merged_faults"].T).T % 2, samples["syndrome"])
    assert np.array_equal((l @ samples["merged_faults"].T).T % 2, samples["observable"])
    assert samples["syndrome"].shape == (256, 936)
    assert samples["observable"].shape == (256, 12)
    assert not samples["noiseless_syndrome"].any()
    assert not samples["noiseless_observable"].any()
    np.save(OUT / "repository_additive_priors.npy", additive)
    worst = int(np.argmax(delta))

    old_paths = [
        "artifact_manifest.json", "artifact_manifest_2026-11-13.json",
        "artifact_manifest_2026-11-15.json", "artifact_manifest_2026-11-16.json",
        "stress_gate/manifest.json", "fit_diagnostic_2026-11-13/manifest.json",
        "learning_curves_2026-11-13/manifest.json", "reviewer_perspective_2026-11-13/manifest.json",
        "validation_gate_2026-11-13/manifest.json", "supervisor_review_2026-11-16/manifest.json",
        "supervisor_review_2026-11-16/cross_domain_manifest.json", "novelty_feasibility_2026-11-16/manifest.json",
        "next_stage_design_2026-11-16/manifest.json", "consumer_gate_2026-11-16/manifest.json",
        "research_reorientation_2026-11-16/manifest.json", "experimental_design_review_2026-11-16/manifest.json",
    ]
    previous = {}
    for name in old_paths:
        manifest = STUDY / name
        files = json.loads(manifest.read_text())["files"]
        for relative, expected in files.items():
            assert sha(manifest.parent / relative) == expected, (name, relative)
        previous[name] = len(files)
    audit = {
        "audit_passed": True,
        "generator_and_support_conversion_gate": "pass",
        "repository_exact_prior_equality_gate": "fail; discrepancy preserved",
        "exact_published_failure_reproduction": "not established; no decoder calls",
        "priors": {"columns": len(groups), "affected_columns": int(affected.sum()),
                   "max_absolute_additive_minus_xor": float(delta.max()),
                   "max_relative_to_exact": float((delta/exact).max()),
                   "worst_column": worst, "worst_additive": float(additive[worst]),
                   "worst_exact": float(exact[worst]),
                   "independent_product_formula_max_saved_difference": float(np.max(np.abs(exact-saved))),
                   "interpretation": "Conversion approximation; decoding impact not measured. "
                                     "Not evidence that published failure results are invalid."},
        "samples_checked_without_resampling": {"noiseless_circuit": 32, "dem": 256},
        "new_decoder_calls": 0, "new_training_samples": 0,
        "prior_manifests_verified": previous,
        "raw_result_sha256": sha(OUT / "result.json"),
        "probe_source_sha256": sha(ROOT / "probe_generator.py"),
        "audit_source_sha256": sha(Path(__file__)),
    }
    (ROOT / "probe_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({k: v for k, v in audit.items() if k not in ["prior_manifests_verified", "priors"]}))
    print(json.dumps(audit["priors"]))


if __name__ == "__main__":
    main()
