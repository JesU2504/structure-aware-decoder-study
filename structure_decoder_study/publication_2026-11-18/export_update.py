"""Update the existing sanitized project mirror without modifying old provenance."""
import hashlib,importlib.util,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    source=HERE.parent/'publication_2026-11-17/export_public.py'
    spec=importlib.util.spec_from_file_location('original_public_export',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.HERE=HERE
    module.README=(HERE/'PUBLIC_README.md').read_text()
    module.OMIT_PREFIXES=module.OMIT_PREFIXES+('publication_2026-11-18/private/',)
    module.IGNORE_PARTS=module.IGNORE_PARTS|{'private','node_modules'}|{p.name for p in module.STUDY.rglob('.env*')}
    module.main()
    location=json.loads((HERE/'private/export_location.json').read_text())
    manifest=Path(location['destination'])/'PUBLIC_EXPORT.json'
    data=json.loads(manifest.read_text());data.update(date='2026-11-18',
        scope='Privacy-sanitized decoder project update including preserved failed probes and stdlib runner repair')
    ignore=Path(location['destination'])/'.gitignore'
    ignore.write_text(ignore.read_text()+'**/private/\n')
    payload=ignore.read_bytes();data['files']['.gitignore'].update(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload))
    for source in sorted((HERE/'root_files').rglob('*')):
        if not source.is_file():continue
        relative=source.relative_to(HERE/'root_files');target=Path(location['destination'])/relative
        target.parent.mkdir(parents=True,exist_ok=True);payload=source.read_bytes();target.write_bytes(payload)
        data['files'][relative.as_posix()]=dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),generated_for_public_export=True)
    manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    for name,entry in data['files'].items():
        payload=(Path(location['destination'])/name).read_bytes()
        assert hashlib.sha256(payload).hexdigest()==entry['sha256'],name
        assert str(module.WORKSPACE).encode() not in payload and str(Path.home()).encode() not in payload,name
        assert not re.search(rb'gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',payload),name
    location['files']=len(data['files'])
    location['bytes']=sum(r['bytes'] for r in data['files'].values())
    (HERE/'private/export_location.json').write_text(json.dumps(location,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
