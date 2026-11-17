"""Fetch only five pinned public files; validate before accepting any source."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parent
DEST=ROOT/"sources/dem_trapping_sets-b9ac6a1"
COMMIT="b9ac6a1133e1db71a99d253e523ebca524117142"
FILES=["README.md","examples/enumerate_dem_ts.py","examples/include_py/build_decoding_matrices_layered.py",
       "examples/include_py/codes_q.py","examples/include_py/utils.py"]


def main():
    # Preserve and explicitly invalidate the earlier empty-download bookkeeping.
    old=ROOT/"source_manifest.json"
    if old.exists():
        previous=json.loads(old.read_text())
        if previous.get("files") and all(h==hashlib.sha256(b"").hexdigest() for h in previous["files"].values()):
            (ROOT/"first_fetch_failure.json").write_text(json.dumps(dict(valid=False,
                reason="Five sandbox network failures created empty placeholders; rejected before source execution",
                invalid_preliminary_manifest=previous),indent=2,sort_keys=True)+"\n")
    staged={}
    for name in FILES:
        response=subprocess.run(["gh","api",f"repos/Error-Correction-Lab/dem_trapping_sets/contents/{name}?ref={COMMIT}"],
                                capture_output=True,text=True,timeout=45,check=True)
        obj=json.loads(response.stdout)
        assert obj["type"]=="file" and obj["encoding"]=="base64" and 0<obj["size"]<65536,name
        data=base64.b64decode(obj["content"])
        assert len(data)==obj["size"] and len(data)>0,name
        blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        assert blob==obj["sha"],name
        staged[name]=(data,blob)
    manifest={}
    for name,(data,blob) in staged.items():
        target=DEST/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        manifest[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=blob)
    old.write_text(json.dumps(dict(valid=True,date="2026-11-17",repository="https://github.com/Error-Correction-Lab/dem_trapping_sets",
        commit=COMMIT,files=manifest,source_executed=False,scope="Small pinned source subset; no enumeration or decoder execution"),indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(validated_files=len(manifest),total_bytes=sum(len(v[0]) for v in staged.values()),source_executed=False)))


if __name__=="__main__":
    main()
