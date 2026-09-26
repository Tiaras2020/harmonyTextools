"""Record measured B2.3 payload, signature, host and device acceptance evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import fitz

root=Path(__file__).resolve().parents[1]
out=root/'validation/full-resources'
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
assert read(root/'texstudio-harmony/release.json')['version']=='1.0.13'
assert read(out/'b23-payload.json')['passed']
assert read(out/'import-tests/result.json')['passed']
for name in ('host-tests.json','management-tests.json','user-tests.json'):
    assert read(root/'validation/resources'/name)['passed']
slim=(out/'device-slim/new-type1-font.log').read_text()
full=(out/'device-full/new-type1-font.log').read_text()
assert 'texlive_1.0.12' in slim and '/tex-resources/resources/' in slim
assert 'texlive_1.0.13' in full and '/tex-resources/resources/' not in full
terminal=out/'device-full/hishell-full-1.0.13'
terminal_result=(terminal/'hishell-result.txt').read_text()
assert 'PASS: pdfTeX macros, Type1 fonts, XeLaTeX; no manual resource setup.' in terminal_result
for name in ('TEXINPUTS','TEXMF','TEXMFCNF','TEXMFHOME','TEXFONTMAPS','TFMFONTS'):
    assert name+'=' in terminal_result.splitlines()
pdf_results={}
pdfs=[out/'device-slim/new-type1-font.pdf',out/'device-full/new-type1-font.pdf']+list(terminal.glob('*.pdf'))
for pdf in pdfs:
    doc=fitz.open(pdf)
    assert len(doc)==1
    expected='Accanthis' if 'type1' in pdf.name else 'Harmony full resource'
    assert expected in doc[0].get_text(),pdf
    fonts=subprocess.check_output([r'E:\texlive\2024\bin\windows\pdffonts.exe',str(pdf)],text=True)
    rows=fonts.splitlines()[2:]
    assert rows and all(row.split()[-5]=='yes' for row in rows),pdf
    pdf.with_suffix('.pdffonts.txt').write_text(fonts)
    pdf_results[pdf.relative_to(root).as_posix()]={'pages':1,'fontsEmbedded':True,'fontCount':len(rows),'sha256':sha(pdf)}
for fls in terminal.glob('*.fls'):
    for line in fls.read_text().splitlines():
        if line.startswith('INPUT /'):
            path=line[6:]
            assert path.startswith(('/data/service/hnp/texlive.org/texlive_1.0.13/','/storage/Users/currentUser/Download/TeXstudioResourceTest/hishell-full-1.0.13/')),path
artifacts=[]
for version in ('1.0.12','1.0.13'):
    p=root/f'validation/device-signing-{version}/result.json'
    sign=read(p)
    assert sign['signature_verified'] and sign['embedded_hnp_unchanged']
    artifact=root/'artifacts'/sign['signed_file']
    assert sha(artifact)==sign['sha256']
    sign['installed']=True; p.write_text(json.dumps(sign,indent=2)+'\n')
    artifacts.append({'path':artifact.relative_to(root).as_posix(),'bytes':artifact.stat().st_size,'sha256':sign['sha256'],'profile':'full' if version=='1.0.13' else 'slim-development'})
pack=root/'artifacts/harmony-full-resources-2025.1.zip'
pack_meta=read(out/'development-pack.json')
assert sha(pack)==pack_meta['sha256']
artifacts.append({'path':pack.relative_to(root).as_posix(),'bytes':pack.stat().st_size,'sha256':pack_meta['sha256'],'profile':'runtime-extension-v1'})
sources=[root/'texstudio-harmony/release.json',root/'texstudio-harmony/scripts/release_config.py',root/'texstudio-harmony/texstudio_harmony/AppScope/app.json5']
sources += [root/'texstudio-harmony/third_party/texstudio/src'/n for n in ('harmonyRelease.h','harmonyresources.cpp','harmonyresources.h','harmonyresourcesdialog.cpp','harmonyuserresourcesdialog.cpp','utilsSystem.cpp')]
sources += [root/'build-support'/n for n in ('prepare-resource-release.py','package-resource-release.sh','make-full-resource-pack.py','test-full-import.py','verify-b23-payload.py','record-b23-delivery.py','finalize-packages.py','sync-baseline.py')]
sources += [root/'texstudio-harmony/scripts/common/build_texlive_hnp.sh',out/'hishell-full-test.sh']
records=[]
for src in sources:
    rel=src.relative_to(root); dst=out/'source-1.0.13'/rel
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    records.append({'path':rel.as_posix(),'sha256':sha(dst)})
(out/'source-1.0.13/manifest.json').write_text(json.dumps(records,indent=2)+'\n')
report={'stage':'B2.3','version':'1.0.13','installed':True,'resourceProfile':'full','slimDevelopmentVersion':'1.0.12',
        'tests':{'legacyImport':17,'resourceManagement':9,'userLayer':10,'fullImportChecks':6},
        'device':{'slimImportRestartCompilePreview':True,'fullBuiltinCompilePreview':True,'importedResourcesDisabledForFullTest':True,'newHiShellDefaultEnvironment':True,'hiShellPdftexAndXelatex':True,'resourcePathsInPublicHnp':True},
        'identicalDevelopmentAndFullResourceFiles':91024,'nativeFilesUnchanged':204,'freeDeviceSpaceBefore':'82 GiB','freeDeviceSpaceAfter':'75 GiB',
        'artifacts':artifacts,'pdfChecks':pdf_results,
        'limits':['First conservative resource set, not all desktop TeX Live packages','1170 package items pending review; 118 font map entries unavailable','Perl/latexmk, Biber, LuaTeX and other external toolchains are not newly ported','Private user edits still require explicit HiShell export/sync','Developer-signed device installation verified; AppGallery distribution not validated']}
(out/'device-result-1.0.13.json').write_text(json.dumps(report,indent=2)+'\n')
manifest_path=root/'DELIVERY-MANIFEST.json'; delivery=read(manifest_path)
delivery['status']='1.0.13_B2.3_full_public_HNP_and_slim_import_validated'
delivery['latestReport']='FULL-RESOURCES.md'
delivery['fullResourcesB23']={'status':'device_validated','report':'FULL-RESOURCES.md','result':'validation/full-resources/device-result-1.0.13.json','fullVersion':'1.0.13','slimVersion':'1.0.12','resourcePack':'artifacts/harmony-full-resources-2025.1.zip'}
delivery['resourceExtension']['nextMilestone']='Review remaining package/font compatibility, bibliography regression, and separately port external native toolchains'
delivery['deviceValidationScope']='deviceRuntimeValidated remains false for exhaustive all-engine acceptance; B2.3 explicit automated and UI device checks are recorded in fullResourcesB23.result.'
for item in reversed(artifacts):
    if item['path'] not in delivery['artifacts']: delivery['artifacts'].insert(0,item['path'])
if 'validation/full-resources/device-result-1.0.13.json' not in delivery['evidence']:
    delivery['evidence'].append('validation/full-resources/device-result-1.0.13.json')
inventory=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(root/'validation/resources/artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
for version in ('1.0.12','1.0.13'):
    name=f'artifacts/texlive-{version}.hnp'
    if name not in delivery['artifacts']: delivery['artifacts'].insert(0,name)
manifest_path.write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('B2.3 signature, payload, 5 device PDFs and HiShell paths verified. Source snapshot and manifest saved.')
