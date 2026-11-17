"""Fetch a pinned sorting reference and capture only relevant binary evidence."""
from pathlib import Path
import base64,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parent
COMMIT="d3429964cd4ffe1abfc041c6ec8b8425cb174f40"


def main():
    assert not (ROOT/"reference_manifest.json").exists()
    files={}
    for name in ["src_cpp/sort.hpp","src_cpp/osd.hpp","LICENSE"]:
        response=subprocess.run(["gh","api",f"repos/quantumgizmos/ldpc/contents/{name}?ref={COMMIT}"],capture_output=True,text=True,check=True)
        obj=json.loads(response.stdout);data=base64.b64decode(obj["content"])
        assert len(data)==obj["size"] and hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()==obj["sha"]
        p=ROOT/"github_reference"/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        files[name]=dict(sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=obj["sha"],bytes=len(data))
    local=Path('.venv/lib/python3.12/site-packages/ldpc/bposd_decoder/_bposd_decoder.cpython-312-darwin.so').resolve()
    output=subprocess.run(["otool","-tvV",str(local)],capture_output=True,text=True,check=True).stdout.splitlines()
    selected=[];active=False
    for line in output:
        if line.startswith('__ZN4ldpc4sort3cmp') or line.startswith('__ZN4ldpc4sort22soft_decision_col_sort'):active=True
        elif active and line and not line[0].isdigit():active=False
        if active:selected.append(line)
    (ROOT/"installed_sort_disassembly.txt").write_text('\n'.join(selected)+'\n')
    reference=ROOT/"github_reference/src_cpp/osd.hpp"
    archive=ROOT/"source/src_cpp/osd.hpp"
    record=dict(repository="https://github.com/quantumgizmos/ldpc",commit=COMMIT,files=files,
        osd_header_equal_pypi_2_4_1=reference.read_bytes()==archive.read_bytes(),
        installed_binary_sha256=hashlib.sha256(local.read_bytes()).hexdigest(),
        disassembly_sha256=hashlib.sha256((ROOT/"installed_sort_disassembly.txt").read_bytes()).hexdigest(),
        note="PyPI archive omits sort.hpp; this pinned reference is corroborated by the installed binary's exported comparator and qsort call. A wrapper hash match alone does not prove every C++ header used to build the wheel.")
    (ROOT/"reference_manifest.json").write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(pinned_reference_files=3,osd_header_equal_pypi_2_4_1=record['osd_header_equal_pypi_2_4_1'],disassembly_lines=len(selected))))


if __name__=='__main__':main()
