"""Create a privacy-sanitized, independently verifiable public project mirror."""
from pathlib import Path
import hashlib,json,os,re,tempfile
from urllib.parse import quote,unquote

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
WORKSPACE=STUDY.parent
OMIT_PREFIXES=("failure_target_2026-11-17/sources/dem_trapping_sets-b9ac6a1/",
               "natural_noise_reproduction_2026-11-17/sources/Adaptive-qLDPC-8cc3201/",
               "publication_2026-11-17/private/")
IGNORE_PARTS={".git",".venv","__pycache__",".pytest_cache","runtime_cache"}
TEXT_SUFFIXES={".md",".json",".jsonl",".py",".txt",".log",".csv",".toml",".yml",".yaml",".hpp",".h",".cpp",".pxd",".pyx",".in",".rst",".cff"}

README="""# Structure-aware decoder study

Research code, protocols and simulated data for studying decoder costs and
reproducing decoding failures. This is exploratory work, not a manuscript or a
claim of a new decoder or compiler speedup. AI supervisor reviews are labelled
as AI reviews, not external human peer review.

## Current findings (17 November 2026)

- Earlier circuit-derived cost-model experiments did not establish a useful
  incremental benefit from the tested graph summaries or a compiler speedup.
- A source-matched BB144 Z-memory reproduction at 24 rounds and p=0.007 produced
  12 syndrome-valid logical errors in 512 natural circuit-noise observations.
  BP20+OSD0, BP30+LSD0 and BP100+LSD0 failed on the same 12 observations.
- The planned Python 1FV comparison stopped when its native-baseline equality
  gate failed at case 51. No real 1FV search was run.
- An implementation-derived ordering diagnostic matched all 24 cached native
  baselines, versus 23 for stable Python ordering. It accounts for that observed
  tie-order incompatibility on the fixed macOS arm64 panel. It does not resume
  the stopped search or establish repair headroom or cross-platform equivalence.

## Verify and replay

Python3.12 was used for the recorded experiments. Create a fresh environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verify.py
```

The verifier checks every exported file's checksum and independently recomputes
all 1,627 stored natural-noise experiment outcomes and the ordering-panel matches.
It makes no decoder calls. To replay the first recorded logical failure:

```sh
.venv/bin/python -m pip install -r requirements-decoder.txt
.venv/bin/python tools/replay_case.py --case 23
```

The recorded environment gives syndrome residual 0 and 6 wrong logical bits for
case 23. Exact correction vectors and random-seed streams can depend on package
versions and platform. The source circuit extracts **Z checks only**.

## Read the evidence

- [Natural-noise reproduction](structure_decoder_study/natural_noise_reproduction_2026-11-17/RESULTS.md)
- [Stopped headroom comparison](structure_decoder_study/headroom_1fv_2026-11-17/RESULTS.md)
- [Ordering diagnostic](structure_decoder_study/ordering_diagnostic_2026-11-17/RESULTS.md)
- [Supervisor review](structure_decoder_study/publication_strategy_2026-11-17/supervisor_headroom_postcheck.md)
- [Original cost-model study](structure_decoder_study/README.md)

## Export and provenance

This is a public mirror of the decoder project, not the surrounding workspace.
No environment, credentials, native binaries or unrelated projects are included.
Data arrays are byte-preserved. Personal host paths in text are replaced by
`<WORKSPACE>`, `<USER_HOME>` or `<TEMP>`; Markdown file links are made relative.
`PUBLIC_EXPORT.json` records original and exported hashes and all exclusions.

Historical machine-specific freeze/manifests are retained as provenance, not
re-signed as if sanitized bytes were the original experiment. Their old hashes
can differ from transformed text or omitted dependencies. Use `tools/verify.py`
for this mirror rather than running historical in-place freeze/audit drivers.
Fresh experiments belong in new output directories with a newly frozen protocol.

Upstream snapshots without an explicit license are not vendored. If needed,
`tools/fetch_upstream.py` restores their exact pinned files without executing
them. See [third-party notices](THIRD_PARTY.md). The saved-data verifier and
native case replay do not require those helpers.

The reproduction is a baseline. Publication novelty and a consequential
compiler-facing decision remain open research requirements.
"""


def digest(data):return hashlib.sha256(data).hexdigest()


def sanitize(text,relative):
    if relative.suffix==".md":
        prefixes=[str(WORKSPACE),quote(str(WORKSPACE),safe="/")]
        expression=r"\]\((<?)((?:"+"|".join(re.escape(p) for p in prefixes)+r")[^)\n>]+)(>?)\)"
        def link(match):
            target=unquote(match.group(2));line=""
            found=re.search(r":(\d+)$",target)
            if found:line="#L"+found.group(1);target=target[:found.start()]
            tail=Path(target).relative_to(WORKSPACE)
            destination=Path(os.path.relpath(tail,start=relative.parent))
            return "]("+quote(destination.as_posix(),safe="/#")+line+")"
        text=re.sub(expression,link,text)
    text=text.replace(quote(str(WORKSPACE),safe="/"),"<WORKSPACE>").replace(str(WORKSPACE),"<WORKSPACE>")
    text=text.replace(str(Path.home()),"<USER_HOME>")
    text=re.sub(r"/(?:private/)?var/folders/[^\s\"'<>\)]+","<TEMP>",text)
    return text


def main():
    destination=Path(tempfile.mkdtemp(prefix="structure-decoder-public-",dir="/private/tmp"))
    records={};excluded=[]
    for source in sorted(STUDY.rglob("*")):
        if not source.is_file():continue
        rel=source.relative_to(STUDY)
        if any(p in IGNORE_PARTS for p in rel.parts) or source.name==".DS_Store" or any(rel.as_posix().startswith(p) for p in OMIT_PREFIXES):
            excluded.append(dict(path="structure_decoder_study/"+rel.as_posix(),reason="cache/private publication state or omitted upstream helper snapshot"));continue
        if source.suffix in {".so",".dylib",".pyc",".pyo"}:
            excluded.append(dict(path="structure_decoder_study/"+rel.as_posix(),reason="native binary/cache"));continue
        target_rel=Path("structure_decoder_study")/rel
        original=source.read_bytes();published=original
        if source.suffix.lower() in TEXT_SUFFIXES or source.name.startswith("LICENSE"):
            try:published=sanitize(original.decode("utf-8"),target_rel).encode("utf-8")
            except UnicodeDecodeError:pass
        target=destination/target_rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(published)
        records[target_rel.as_posix()]=dict(original_sha256=digest(original),sha256=digest(published),bytes=len(published),privacy_transformed=published!=original)
    root_files={"README.md":README,
        ".gitattributes":"* -text\n",
        "requirements.txt":"numpy==2.4.1\nscipy==1.17.0\n",
        "requirements-decoder.txt":"-r requirements.txt\nldpc==2.4.1\nstim==1.16.0\n",
        "requirements-analysis.txt":"-r requirements-decoder.txt\nscikit-learn==1.8.0\nmatplotlib==3.11.2\nnetworkx==3.6.1\nsympy==1.14.0\n",
        ".gitignore":".venv/\n__pycache__/\n*.py[cod]\n.DS_Store\n.env\n.env.*\n*.so\n*.dylib\nstructure_decoder_study/publication_2026-11-17/private/\nstructure_decoder_study/failure_target_2026-11-17/sources/dem_trapping_sets-b9ac6a1/\nstructure_decoder_study/natural_noise_reproduction_2026-11-17/sources/Adaptive-qLDPC-8cc3201/\n",
        "THIRD_PARTY.md":"# Third-party notices\n\nPinned TMCBS sources retain their Apache-2.0 license and vendored license notices.\nPinned ldpc source excerpts and its PyPI archive retain the MIT license.\n\nThe Error-Correction-Lab/dem_trapping_sets and UCL-CCS/Adaptive-qLDPC helper snapshots are referenced by commit and hash but are not vendored here. The optional fetch tool restores those public files without executing them.\n\nRecorded simulation outputs, experimental protocols and review reports are part of this project. AI reviews are not external human peer review. No additional blanket license overriding upstream terms is asserted.\n"}
    for name,text in root_files.items():
        data=text.encode();(destination/name).write_bytes(data);records[name]=dict(sha256=digest(data),bytes=len(data),generated_for_public_export=True)
    for source in (HERE/"public_tools").glob("*.py"):
        p=destination/"tools"/source.name;p.parent.mkdir(exist_ok=True);data=source.read_bytes();p.write_bytes(data)
        records["tools/"+source.name]=dict(sha256=digest(data),bytes=len(data),generated_for_public_export=True)
    suspicious=[]
    patterns=[re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")]
    for name in records:
        data=(destination/name).read_bytes()
        if any(pattern.search(data) for pattern in patterns):suspicious.append(name)
        assert str(WORKSPACE).encode() not in data,name
        assert str(Path.home()).encode() not in data,name
    assert not suspicious,"Secret-like material found; stop public export: "+repr(suspicious)
    export=dict(date="2026-11-17",scope="Privacy-sanitized decoder project mirror",files=records,excluded=excluded,
        data_arrays_byte_preserved=True,historical_manifests_resigned=False,secret_scan_passed=True,
        transformations=["Personal absolute paths replaced by documented placeholders","Markdown links made relative","Unlicensed upstream helper snapshots omitted; pinned restoration tool supplied","Virtual environments/native binaries/caches/unrelated workspace excluded"])
    (destination/"PUBLIC_EXPORT.json").write_text(json.dumps(export,indent=2,sort_keys=True)+"\n")
    private=HERE/"private";private.mkdir(exist_ok=True)
    (private/"export_location.json").write_text(json.dumps(dict(destination=str(destination),files=len(records),bytes=sum(r['bytes'] for r in records.values()),transformed=sum(r.get('privacy_transformed',False) for r in records.values()),excluded=len(excluded)),indent=2)+"\n")
    print((private/"export_location.json").read_text())


if __name__=="__main__":main()
