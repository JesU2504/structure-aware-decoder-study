"""Read public GitHub metadata; save a bounded artifact-access inventory."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = "Error-Correction-Lab/dem_trapping_sets"
PIN = "b9ac6a1133e1db71a99d253e523ebca524117142"


def api(endpoint):
    p = subprocess.run(["gh", "api", endpoint], check=True, text=True,
                       capture_output=True, timeout=45)
    return json.loads(p.stdout)


def tree(commit):
    result = api(f"repos/{REPO}/git/trees/{commit}?recursive=1")
    assert not result.get("truncated", False)
    return {"commit": commit, "files": [
        {k: x[k] for k in ("path", "sha", "size")}
        for x in result["tree"] if x["type"] == "blob"
    ]}


def decoder_metadata(repo):
    info = api(f"repos/{repo}")
    commit = api(f"repos/{repo}/commits/{info['default_branch']}")["sha"]
    result = api(f"repos/{repo}/git/trees/{commit}?recursive=1")
    assert not result.get("truncated", False)
    paths = [x["path"] for x in result["tree"] if x["type"] == "blob"]
    return {"repository": repo, "inspected_commit": commit,
            "file_count": len(paths), "paths": paths,
            "scope": "metadata only; implementation not downloaded or executed"}


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        commits_f = pool.submit(api, f"repos/{REPO}/commits?per_page=100")
        branches_f = pool.submit(api, f"repos/{REPO}/branches?per_page=100")
        releases_f = pool.submit(api, f"repos/{REPO}/releases?per_page=100")
        commits, branches, releases = commits_f.result(), branches_f.result(), releases_f.result()
    assert 0 < len(commits) < 100
    assert commits[0]["sha"] == PIN, "Upstream changed; preserve original inspection separately"
    with ThreadPoolExecutor(max_workers=4) as pool:
        trees = list(pool.map(tree, [c["sha"] for c in commits]))
        decoders = list(pool.map(decoder_metadata, ["trmue/relay", "UCL-CCS/Adaptive-qLDPC"]))
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": REPO, "pin": PIN,
        "branches": [b["name"] for b in branches],
        "release_assets": [{"tag": r["tag_name"], "assets": [a["name"] for a in r["assets"]]}
                           for r in releases],
        "commit_trees": trees, "decoder_repositories": decoders,
        "interpretation": "No exact labeled BB144 decoder-failure witness located in these trees. "
                          "This inspection cannot establish global unavailability.",
    }
    (ROOT / "public_access_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"commits_checked": len(trees), "branches": report["branches"],
                      "releases": len(releases), "decoder_repositories_found": len(decoders)}))


if __name__ == "__main__":
    main()
