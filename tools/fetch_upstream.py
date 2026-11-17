"""Restore omitted, pinned upstream helper files without executing them."""
from pathlib import Path
import hashlib,json,urllib.request

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/"structure_decoder_study"


def main():
    tasks=[("failure_target_2026-11-17","sources/dem_trapping_sets-b9ac6a1"),
           ("natural_noise_reproduction_2026-11-17","sources/Adaptive-qLDPC-8cc3201")]
    count=0
    for folder,destination in tasks:
        manifest=json.loads((STUDY/folder/"source_manifest.json").read_text())
        repo=manifest["repository"].removeprefix("https://github.com/")
        for name,record in manifest["files"].items():
            path=STUDY/folder/destination/name
            if path.exists():data=path.read_bytes()
            else:
                url=f"https://raw.githubusercontent.com/{repo}/{manifest['commit']}/{name}"
                with urllib.request.urlopen(url,timeout=60) as response:data=response.read()
            assert hashlib.sha256(data).hexdigest()==record["sha256"],name
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);count+=1
    print(json.dumps(dict(verified_upstream_files=count,source_executed=False)))


if __name__=="__main__":main()
