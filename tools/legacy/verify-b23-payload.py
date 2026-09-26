"""Compare full HNP resource payload with the actual development import ZIP."""
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
out=root/'validation/full-resources'
with zipfile.ZipFile(root/'artifacts/harmony-full-resources-2025.1.zip') as development, zipfile.ZipFile(root/'artifacts/texlive-1.0.13.hnp') as full:
    manifest=json.loads(development.read('manifest.json'))
    prefix=next(n[:-len('hnp.json')] for n in full.namelist() if n.endswith('/hnp.json'))
    for count,(name,item) in enumerate(manifest['files'].items(),1):
        h=hashlib.sha256()
        with full.open(prefix+name) as stream:
            for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
        assert h.hexdigest()==item['sha256'] and full.getinfo(prefix+name).file_size==item['size'],name
        if count%20000==0: print('Identical HNP/ZIP resources:',count,flush=True)
    baseline=json.loads((out/'result.json').read_text())
    for name,sha in baseline['nativeFiles'].items():
        assert hashlib.sha256(full.read(prefix+name)).hexdigest()==sha,name
    result={'passed':True,'fullVersion':'1.0.13','developmentVersion':'1.0.12','profile':manifest['profile'],'identicalResourceFiles':len(manifest['files']),'nativeFilesUnchanged':len(baseline['nativeFiles']),'compatibilityId':manifest['compatibilityId']}
    (out/'b23-payload.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
