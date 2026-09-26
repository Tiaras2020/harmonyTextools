"""Validate the UI-only HAP on Windows, reusing the accepted runtime evidence."""
import hashlib, json, zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dest=root/'artifacts'
hap=dest/'TeXstudioHarmony-1.0.28-arm64-unsigned.hap'
hnp=dest/'texlive-1.0.21.hnp'
def sha(stream):
    h=hashlib.sha256()
    while block:=stream.read(8*1024*1024): h.update(block)
    return h.hexdigest()
with hnp.open('rb') as f: runtime_sha=sha(f)
accepted=json.loads((dest/'package-check-1.0.21.json').read_text(encoding='utf-8'))[hnp.name]
assert runtime_sha==accepted['sha256']
with zipfile.ZipFile(hap) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))
    module=json.loads(z.read('module.json'))
    assert module['app']['versionName']=='1.0.28'
    assert module['app']['versionCode']==1000028
    for name in ['libtexstudio.so','libqohos.so']:
        assert any(p.endswith('/'+name) for p in z.namelist())
    with z.open('hnp/arm64-v8a/texlive.hnp') as f: assert sha(f)==runtime_sha
    entries=len(z.namelist())
with hap.open('rb') as f: app_sha=sha(f)
report={hap.name:{'bytes':hap.stat().st_size,'sha256':app_sha,'entries':entries,'zip_crc':'passed'},hnp.name:accepted,
        'app_module':module,'runtimeVersion':'1.0.21','embedded_hnp_matches_standalone':True,
        'runtimeEvidence':'package-check-1.0.21.json; archive identity rechecked'}
(dest/'package-check-1.0.28.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(dest/'SHA256SUMS-1.0.28.txt').write_text(f'{app_sha}  {hap.name}\n{runtime_sha}  {hnp.name}\n',encoding='utf-8')
print('PASS: app 1.0.28, ZIP CRC, native libraries, unchanged runtime 1.0.21')
