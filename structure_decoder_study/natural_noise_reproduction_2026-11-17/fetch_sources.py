"""Download a small pinned public source subset; validate all before writing."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import base64
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = "UCL-CCS/Adaptive-qLDPC"
COMMIT = "8cc32014a6461bb8f241f47f62a7e74f63817738"
DEST = ROOT / "sources" / "Adaptive-qLDPC-8cc3201"
FILES = ["README.md", "requirements.txt", "config.py", "failure_prediction/__init__.py",
         "failure_prediction/qldpc_codes.py", "failure_prediction/qldpc_circuit.py",
         "failure_prediction/adaptive_v1_run.py", "failure_prediction/adaptive_v1.py",
         "failure_prediction/osd_internals.py"]


def fetch(name):
    p = subprocess.run(["gh", "api", f"repos/{REPO}/contents/{name}?ref={COMMIT}"],
                       check=True, capture_output=True, text=True, timeout=45)
    obj = json.loads(p.stdout)
    assert obj["type"] == "file" and obj["encoding"] == "base64"
    assert 0 < obj["size"] < 100000
    data = base64.b64decode(obj["content"])
    assert len(data) == obj["size"]
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert blob == obj["sha"]
    return name, data, blob


def main():
    assert not (ROOT / "source_manifest.json").exists(), "Preserve existing fetch snapshot"
    with ThreadPoolExecutor(max_workers=3) as pool:
        staged = list(pool.map(fetch, FILES))
    manifest = {}
    for name, data, blob in staged:
        path = DEST / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        manifest[name] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), git_blob_sha1=blob)
    (ROOT / "source_manifest.json").write_text(json.dumps(dict(valid=True, date="2026-11-17",
        repository=f"https://github.com/{REPO}", commit=COMMIT, files=manifest,
        source_executed=False), indent=2, sort_keys=True) + "\n")
    print(json.dumps(dict(validated_files=len(staged), bytes=sum(len(data) for _,data,_ in staged), source_executed=False)))


if __name__ == "__main__":
    main()
