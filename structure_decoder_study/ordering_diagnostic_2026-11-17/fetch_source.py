"""Fetch verified PyPI source; inspect, never build/install the package."""
from pathlib import Path
import hashlib,json,tarfile,urllib.request

ROOT=Path(__file__).resolve().parent


def main():
    assert not (ROOT/"source_manifest.json").exists(),"Preserve prior source snapshot"
    url="https://pypi.org/pypi/ldpc/2.4.1/json"
    with urllib.request.urlopen(url,timeout=30) as response:metadata=json.load(response)
    sdists=[x for x in metadata["urls"] if x["packagetype"]=="sdist"]
    assert len(sdists)==1
    entry=sdists[0]
    assert entry["filename"]=="ldpc-2.4.1.tar.gz" and entry["url"].startswith("https://files.pythonhosted.org/") and entry["size"]<20000000
    with urllib.request.urlopen(entry["url"],timeout=60) as response:data=response.read(20000001)
    assert len(data)==entry["size"] and hashlib.sha256(data).hexdigest()==entry["digests"]["sha256"]
    path=ROOT/entry["filename"];path.write_bytes(data)
    files={}
    with tarfile.open(path,"r:gz") as archive:
        for member in archive.getmembers():
            name=member.name
            if not member.isfile():continue
            relative=Path(name).relative_to("ldpc-2.4.1")
            keep=(str(relative).startswith("src_cpp/") and relative.suffix in (".hpp",".h")) or relative.name in ("LICENSE","LICENSE.txt","PKG-INFO") or "bposd_decoder/_bposd_decoder.pyx" in str(relative) or "bposd_decoder/_bposd_decoder.pxd" in str(relative)
            if not keep:continue
            assert ".." not in relative.parts and member.size<1000000
            content=archive.extractfile(member).read()
            target=ROOT/"source"/relative
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
            files[str(relative)]=dict(bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
    manifest=dict(version="2.4.1",metadata_url=url,archive_url=entry["url"],archive_filename=entry["filename"],archive_bytes=len(data),archive_sha256=entry["digests"]["sha256"],files=files,package_installed=False,source_executed=False)
    (ROOT/"source_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(dict(verified_archive=True,bytes=len(data),selected_source_files=len(files),package_installed=False)))


if __name__=="__main__":main()
