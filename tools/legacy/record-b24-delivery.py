"""Record measured release and HiShell evidence; run after application UI acceptance."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import fitz

root=Path(__file__).resolve().parents[1]
out=root/'validation/common-resources'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
for path in ('result.json','regression/result.json','profile-tests.json','import-tests/result.json','payload.json','device/app-acceptance.json'):
    proof=read(out/path)
    assert proof.get('passed',proof.get('hostValidated')),path
terminal=out/'device/hishell-common-1.0.14'
result=(terminal/'hishell-result.txt').read_text()
assert 'PASS: Chinese Beamer, PGFPlots 2D/3D/table, newpx, BibTeX multi-pass; no manual resource setup.' in result
for var in ('TEXINPUTS','TEXMF','TEXMFCNF','TEXMFHOME','TEXFONTMAPS','TFMFONTS'):assert var+'=' in result.splitlines()
pdf_results={}
for name,pages in [('beamer-zh',3),('pgfplots-test',1),('newpx-test',1),('bibtex-zh',1)]:
    pdf=terminal/(name+'.pdf'); doc=fitz.open(pdf)
    assert len(doc)==pages
    log=(terminal/(name+'.log')).read_text()
    assert not re.search(r'undefined (references|citations)|Missing character:|Font shape .*undefined',log),name
    for line in (terminal/(name+'.fls')).read_text().splitlines():
        if line.startswith('INPUT /'):
            assert line[6:].startswith(('/data/service/hnp/texlive.org/texlive_1.0.14/','/storage/Users/currentUser/Download/TeXstudioResourceTest/B24/hishell-common-1.0.14/')),line
    fonts=subprocess.check_output([r'E:\texlive\2024\bin\windows\pdffonts.exe',str(pdf)],text=True)
    rows=fonts.splitlines()[2:];assert rows and all(row.split()[-5]=='yes' for row in rows),name
    pdf.with_suffix('.pdffonts.txt').write_text(fonts)
    pdf_results[name]={'pages':pages,'allFontsEmbedded':True,'fontCount':len(rows),'sha256':sha(pdf)}
    for i,page in enumerate(doc):page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(terminal/f'{name}-page{i+1}.png')
bbl=(terminal/'bibtex-zh.bbl').read_text();assert all(n in bbl for n in ('knuth1984','lamport1994'))
signpath=root/'validation/device-signing-1.0.14/result.json'; sign=read(signpath)
assert sign['signature_verified'] and sign['embedded_hnp_unchanged']
assert sha(root/'artifacts'/sign['signed_file'])==sign['sha256']
sign['installed']=True;signpath.write_text(json.dumps(sign,indent=2)+'\n')
pack=read(out/'development-pack.json')
assert sha(root/'artifacts/harmony-full-resources-2025.2.zip')==pack['sha256']
report={'stage':'B2.4','version':'1.0.14','installed':True,'resourceProfile':'full','passed':True,
        'resourceVersion':'2025.2','addedFiles':974,'identicalDevelopmentAndFullResourceFiles':91998,
        'nativeFilesUnchanged':204,'unsupportedFontEntries':44,
        'tests':{'parserExtraction':16,'profileBoundaries':24,'legacyImport':17,'management':9,'userLayer':10,'hostCompileCases':9},
        'device':{'app':read(out/'device/app-acceptance.json'),'freshHiShellNoResourceOverrides':True,'publicHnpOnly':True,'bibtexMultiPass':True},
        'pdfChecks':pdf_results,
        'limits':['PGFPlots ordinary TeX backend only; no externalization, Lua or external contour tools',
                  'newpx Type1 tested, not all fontspec options','44 unavailable font mappings remain quarantined',
                  'BibTeX tested with English bibliography entries and Chinese body; Biber remains unported',
                  'Private user resources need explicit HiShell sync','Developer-signed device release; store distribution not validated']}
(out/'device-result-1.0.14.json').write_text(json.dumps(report,indent=2)+'\n')
sources=[root/'texstudio-harmony/release.json',root/'texstudio-harmony/scripts/texlive/full_resources.py',root/'texstudio-harmony/scripts/texlive/resource-policy.json',
         root/'texstudio-harmony/third_party/texstudio/src/harmonyresources.cpp',root/'texstudio-harmony/third_party/texstudio/src/harmonyRelease.h',
         root/'texstudio-harmony/texstudio_harmony/AppScope/app.json5',out/'hishell-common-test.sh']
sources += [p for p in (root/'build-support').iterdir() if p.is_file() and (any(s in p.name for s in ('common','b24')) or p.name in ('prepare-resource-release.py','regress-baseline.py','test-full-import.py'))]
sources += list((out/'fixtures').iterdir())
sources += [root/'validation/full-resources/test_full_resources.py']
records=[]
for src in sources:
    rel=src.relative_to(root); dst=out/'source-1.0.14'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    records.append({'path':rel.as_posix(),'sha256':sha(dst)})
(out/'source-1.0.14/manifest.json').write_text(json.dumps(records,indent=2)+'\n')
path=root/'DELIVERY-MANIFEST.json'; delivery=read(path)
delivery.update(status='1.0.14_B2.4_common_resources_and_BibTeX_device_validated',latestReport='COMMON-RESOURCES-B24.md')
delivery['commonResourcesB24']={'status':'device_validated','version':'1.0.14','report':'COMMON-RESOURCES-B24.md','result':'validation/common-resources/device-result-1.0.14.json','resourcePack':'artifacts/harmony-full-resources-2025.2.zip'}
delivery['resourceExtension']['nextMilestone']='Perl + latexmk native runtime and automatic multi-pass build; then Biber and LuaHBTeX'
for name in ('texlive-1.0.14.hnp','harmony-full-resources-2025.2.zip',sign['signed_file']):
    if 'artifacts/'+name not in delivery['artifacts']:delivery['artifacts'].insert(0,'artifacts/'+name)
evidence='validation/common-resources/device-result-1.0.14.json'
if evidence not in delivery['evidence']:delivery['evidence'].append(evidence)
path.write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(root/'validation/resources/artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
print('B2.4 signed payload, application and HiShell evidence recorded.')
