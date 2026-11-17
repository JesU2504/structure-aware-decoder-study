"""Verify the original artifact and snapshot the completed stress exploration.

Run after analysis and figure generation finish. These local SHA-256 manifests
detect later changes; they are not externally timestamped preregistrations.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
SNAPSHOT = "artifact_manifest_2026-11-13.json"
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def inventory(base, omitted):
    return {
        str(path.relative_to(base)): digest(path)
        for path in sorted(base.rglob("*"))
        if path.is_file()
        and not EXCLUDED_PARTS.intersection(path.relative_to(base).parts)
        and path.name != ".DS_Store"
        and path.suffix != ".pyc"
        and path.relative_to(base).as_posix() not in omitted
    }


def verify(base, records):
    failures = [name for name, expected in records.items()
                if not (base / name).is_file() or digest(base / name) != expected]
    if failures:
        raise RuntimeError(f"Artifact integrity failure: {failures}")


def main():
    original = json.loads((STUDY / "artifact_manifest.json").read_text())["files"]
    verify(STUDY, original)
    audit = json.loads((ROOT / "results/audit.json").read_text())
    review = json.loads((ROOT / "results/review_summary.json").read_text())
    assert audit["passed"] and audit["physical_shots_replayed"] == review["physical_shots_total"]
    assert audit["case_sessions"] == 186 and review["unique_new_configurations"] == 56
    integrity = dict(original_files_checked=len(original), original_files_unchanged=True,
                     new_physical_shots=audit["physical_shots_replayed"],
                     correction_checkpoints=audit["correction_checkpoints"],
                     case_sessions=audit["case_sessions"],
                     unique_new_configurations=review["unique_new_configurations"],
                     internal_checks_only=True, external_peer_review=False)
    write_json(ROOT / "results/final_integrity.json", integrity)
    note = "Local post-analysis integrity snapshot; no external timestamp or preregistration claim"
    stress_files = inventory(ROOT, {"manifest.json"})
    write_json(ROOT / "manifest.json", dict(date="2026-11-13", note=note,
               excluded="Python caches, .git, .DS_Store, and this manifest", files=stress_files))
    study_files = inventory(STUDY, {SNAPSHOT})
    write_json(STUDY / SNAPSHOT, dict(date="2026-11-13", note=note,
               original_manifest_preserved="artifact_manifest.json",
               excluded="Python caches, .git, .DS_Store, and this manifest", files=study_files))
    verify(ROOT, stress_files)
    verify(STUDY, study_files)
    print(json.dumps(dict(**integrity, stress_snapshot_files=len(stress_files),
                          study_snapshot_files=len(study_files)), indent=2))


if __name__ == "__main__":
    main()
