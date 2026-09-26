"""Stream a deterministic development ZIP from the reviewed full runtime delta."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'texstudio-harmony/scripts/texlive'))
from full_resources import digest, path_allowed
evidence=root/'validation/full-resources'
result=json.loads((evidence/'result.json').read_text())
assert result['hostValidated'] and result['frozenBaselineUnchanged']
tree=Path(result['candidate'])/'texmf'
policy=json.loads((root/'texstudio-harmony/scripts/texlive/resource-policy.json').read_text())
assembly=json.loads((evidence/'assembly-v1.json').read_text())
expected={i['path']:i['sha256'] for i in assembly['added']}
for i in json.loads((evidence/'font-adaptations.json').read_text())['aliases']:
    expected[i['alias']]=i['sha256']
extras=[p for p in result['expectedGeneratedChanges'] if p.startswith('fonts/map/')]
extras += ['fonts/map/dvips/tetex/'+n for n in assembly['mapBuildInputs']['files']]
for name in extras: expected[name]=digest(tree/name)
files={}
for name,sha in sorted(expected.items()):
    f=tree/name
    assert path_allowed(name,policy) and not f.is_symlink() and digest(f)==sha,name
    files['texmf/'+name]={'size':f.stat().st_size,'sha256':sha}
release=json.loads((root/'texstudio-harmony/release.json').read_text())
manifest={'schema':1,'profile':'runtime-extension-v1','id':'harmony-full-resources','version':'2025.1',
          'title':'TeX Live 2025 兼容资源集合（首批）','compatibilityId':release['compatibilityId'],
          'catalogSha256':digest(evidence/'plan.json'),'unsupportedFontEntries':118,
          'scope':'3194 static resource packages; pending packages and unavailable external tool backends excluded', 'files':files}
output=root/'artifacts/harmony-full-resources-2025.1.zip'
assert not output.exists(), 'Refusing to overwrite resource artifact'
temporary=output.with_suffix('.partial')
assert not temporary.exists(), 'Preserve incomplete artifact for inspection'
def info(name):
    i=zipfile.ZipInfo(name,(2026,1,1,0,0,0)); i.compress_type=zipfile.ZIP_DEFLATED; i.external_attr=0o100644<<16
    return i
with zipfile.ZipFile(temporary,'x',compression=zipfile.ZIP_DEFLATED,allowZip64=True) as archive:
    archive.writestr(info('manifest.json'),(json.dumps(manifest,ensure_ascii=False,sort_keys=True)+'\n').encode())
    for count,name in enumerate(files,1):
        with open(tree/name[6:],'rb') as inp, archive.open(info(name),'w') as out:
            shutil.copyfileobj(inp,out,1024*1024)
        if count%10000==0: print('Packed',count,'/',len(files),flush=True)
temporary.rename(output)
with zipfile.ZipFile(output) as archive: assert archive.testzip() is None
(evidence/'development-pack.json').write_text(json.dumps({'path':str(output),'profile':manifest['profile'],'files':len(files),'expandedBytes':sum(f['size'] for f in files.values()),'bytes':output.stat().st_size,'sha256':digest(output),'zipCrc':'passed','catalogSha256':manifest['catalogSha256']},indent=2)+'\n')
print('Full development resource pack verified:',output,flush=True)
