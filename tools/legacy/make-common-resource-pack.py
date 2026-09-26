"""Stream the complete B2.4 development pack, retaining the original pack as evidence."""
import json
from pathlib import Path
import shutil
import sys
import zipfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'texstudio-harmony/scripts/texlive'))
from full_resources import digest, path_allowed
out=root/'validation/common-resources'
result=json.loads((out/'result.json').read_text())
assert result['hostValidated'] and result['frozenBaselineUnchanged']
tree=Path(result['candidate'])/'texmf'
with zipfile.ZipFile(root/'artifacts/harmony-full-resources-2025.1.zip') as old:
    manifest=json.loads(old.read('manifest.json'))
files=manifest['files']
for rel in result['expectedGeneratedChanges']:
    if rel.startswith('texmf/fonts/map/'):
        files[rel]={'size':(tree/rel[6:]).stat().st_size,'sha256':digest(tree/rel[6:])}
for item in json.loads((out/'assembly.json').read_text())['added']:
    files['texmf/'+item['path']]={'size':item['bytes'],'sha256':item['sha256']}
policy=json.loads((root/'texstudio-harmony/scripts/texlive/resource-policy.json').read_text())
for name,item in files.items():
    p=tree/name[6:]
    assert path_allowed(name[6:],policy) and not p.is_symlink() and digest(p)==item['sha256'],name
manifest.update(profile='runtime-extension-v2',version='2025.2',title='TeX Live 2025 兼容资源集合（B2.4）',
                catalogSha256=digest(out/'assembly.json'),unsupportedFontEntries=result['unsupportedFontEntries'],
                scope='3198 selected static resource packages; Beamer PDF output, PGFPlots native TeX backend, newpx Type1 fonts; external backends excluded')
output=root/'artifacts/harmony-full-resources-2025.2.zip'
temporary=output.with_suffix('.partial')
assert not output.exists() and not temporary.exists(), 'Preserve existing artifact'
def info(name):
    i=zipfile.ZipInfo(name,(2026,1,1,0,0,0)); i.compress_type=zipfile.ZIP_DEFLATED; i.external_attr=0o100644<<16
    return i
with zipfile.ZipFile(temporary,'x',allowZip64=True) as z:
    z.writestr(info('manifest.json'),(json.dumps(manifest,ensure_ascii=False,sort_keys=True)+'\n').encode())
    for count,name in enumerate(sorted(files),1):
        with open(tree/name[6:],'rb') as src,z.open(info(name),'w') as dst: shutil.copyfileobj(src,dst,1024*1024)
        if count%20000==0: print('Packed',count,'/',len(files),flush=True)
temporary.rename(output)
with zipfile.ZipFile(output) as z: assert z.testzip() is None
(out/'development-pack.json').write_text(json.dumps({'path':str(output),'profile':manifest['profile'],'files':len(files),
    'expandedBytes':sum(i['size'] for i in files.values()),'bytes':output.stat().st_size,'sha256':digest(output),'zipCrc':'passed'},indent=2)+'\n')
print('B2.4 resource ZIP verified:',output,flush=True)
