"""Verify prior artifacts and snapshot this completed, bounded calibration gate."""
from common import *


def inventory(base, excluded):
    return {str(p.relative_to(base)): sha(p) for p in sorted(base.rglob("*"))
            if p.is_file() and not {"__pycache__", ".git", ".pytest_cache"}.intersection(p.relative_to(base).parts)
            and p.name != ".DS_Store" and p.suffix not in (".pyc", ".tmp")
            and str(p.relative_to(base)) not in excluded}


def verify(base, files):
    for name, expected in files.items():
        assert sha(base/name) == expected, name


def main():
    previous = verify_previous()
    assert read(ROOT/"model_audit.json")["passed"]
    assert read(ROOT/"bridge_audit.json")["passed"]
    analysis = read(ROOT/"bridge_analysis.json")
    assert not analysis["censored_cases"] and not analysis["reserved_test_parents_used"]
    assert analysis["physical_evaluation_shots"] == 29184 and analysis["evaluation_decoder_calls"] == 59904
    for name, expected in read(ROOT/"bridge_config.json")["files"].items():
        assert sha(STUDY/name) == expected, name
    for name, expected in read(ROOT/"analysis_lock.json")["files"].items():
        assert sha(ROOT/name) == expected, name
    save(ROOT/"final_integrity.json", dict(client_date="2026-11-15", previous_manifests_verified=previous,
         model_audit_passed=True, bridge_audit_passed=True, physical_evaluation_shots=29184,
         physical_profiling_shots=3648, correction_vectors_checked=63552, no_resource_censoring=True,
         reserved_test_parents_used=False, internal_checks_only=True))
    files = inventory(ROOT, {"manifest.json"})
    files["../STATUS_2026-11-15.md"] = sha(STUDY/"STATUS_2026-11-15.md")
    note = "Post-analysis local SHA-256 snapshot; no external timestamp or preregistration claim"
    save(ROOT/"manifest.json", dict(client_date="2026-11-15", note=note, files=files))
    name = "artifact_manifest_2026-11-15.json"
    study_files = inventory(STUDY, {name})
    save(STUDY/name, dict(client_date="2026-11-15", note=note,
         original_manifest_preserved="artifact_manifest.json", files=study_files))
    verify(ROOT, files)
    verify(STUDY, study_files)
    print(json.dumps(dict(gate_snapshot_files=len(files), study_snapshot_files=len(study_files),
                          previous_manifests_verified=previous, passed=True), indent=2))


if __name__ == "__main__":
    main()
