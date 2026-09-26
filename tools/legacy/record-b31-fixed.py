"""Record verified 1.0.16 device outputs and retain the failed 1.0.15 history."""
import hashlib,json,pathlib,re,shutil,subprocess
root=pathlib.Path(__file__).resolve().parents[1]; out=root/'validation/latexmk'
shell=out/'device-hishell-1.0.16'; app=out/'device-app-1.0.16'
log=next(shell.rglob('hishell-result.txt')).read_text(encoding='utf-8')
assert 'PASS: nested -cd project path' in log and 'PASS: B3.1 automatic passes' in log
for path in shell.rglob('*.stdout'):
    assert 'Use of uninitialized' not in path.read_text(encoding='utf-8',errors='replace'),path
before=(out/'cancel-before-1.0.16.txt').read_text(encoding='utf-8-sig')
after=(out/'cancel-after-1.0.16.txt').read_text(encoding='utf-8-sig')
for pid in (33963,33977,33978):
    assert re.search(r'^\s*'+str(pid)+r'\s',before,re.M)
    assert not re.search(r'^\s*'+str(pid)+r'\s',after,re.M)
assert re.search(r'^\s*19661\s',after,re.M)
pdfs={}
for directory in (shell,app):
    for pdf in directory.rglob('*.pdf'):
        if pdf.name=='stop.pdf': continue
        fonts=subprocess.check_output([r'E:\texlive\2024\bin\windows\pdffonts.exe',str(pdf)],text=True)
        pdf.with_suffix('.pdffonts.txt').write_text(fonts,encoding='utf-8')
        rows=fonts.splitlines()[2:]; assert rows and all(r.split()[-5]=='yes' for r in rows)
        pdfs[pdf.relative_to(out).as_posix()]={'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'allFontsEmbedded':True,'fontCount':len(rows)}
assert len(pdfs)==7
for stem in ('app-xe','app-pdf'):
    assert (app/(stem+'.fdb_latexmk')).is_file(),'Missing actual latexmk database'
    assert (app/(stem+'.pdf')).is_file()
result={'stage':'B3.1','version':'1.0.16','date':'2026-09-17','installed':True,'passed':True,
 'scope':'Perl/latexmk automatic build and cwd repair; not exhaustive all-engine acceptance',
 'hishell':{'passed':True,'noResourceOverrides':True,'automaticPasses':True,'incrementalNoOp':True,
 'bibliographyEdit':True,'errorRecovery':True,'unicodeSpaceDirectory':True,'nestedChdir':True,'uninitializedPathWarnings':False},
 'application':{'xeAutoBuildAndPreview':True,'pdfAutoBuildAndPreview':True,'cancelCompilerGroup':True,
 'cancelledPids':[33963,33977,33978],'applicationSurvived':True,'automaticBuildAfterCancel':True,
 'screenshots':['xe16.png','pdf16.png','cancel16.png','recovered16.png']},
 'pdfs':pdfs,'pathFallbackUnitTests':11,
 'remainingLimitations':['Perl may warn that en_US.UTF-8 locale falls back to C; tested Unicode files and CJK PDFs work',
 'Explicit cancellation is still displayed by the existing UI as a killed/crashed command',
 'Biber and LuaLaTeX remain outside this acceptance scope']}
(out/'device-result-1.0.16.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifestpath=root/'DELIVERY-MANIFEST.json'; m=json.loads(manifestpath.read_text(encoding='utf-8'))
m['status']='1.0.16_B3.1_latexmk_and_cwd_fix_device_validated'; m['latestReport']='LATEXMK-B31.md'
m['latexmkB31']=result
m['deviceValidationScope']='deviceRuntimeValidated remains false for exhaustive all-engine acceptance; B2.4 and B3.1 scoped device results are recorded separately.'
for path in ('artifacts/TeXstudioHarmony-1.0.16-arm64-device-signed.hap','artifacts/texlive-1.0.16.hnp'):
    if path not in m['artifacts']: m['artifacts'].insert(0,path)
for path in ('validation/latexmk/device-result-1.0.16.json','validation/device-signing-1.0.16/result.json','validation/latexmk/final-module-check.json'):
    if path not in m['evidence']: m['evidence'].append(path)
manifestpath.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(root/'validation/resources/artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8')
snapshot=out/'source-1.0.16'; snapshot.mkdir(exist_ok=True)
paths=[root/'texstudio-harmony'/p for p in ('release.json','third_party/texstudio/src/utilsSystem.cpp',
 'third_party/texstudio/src/harmonyRelease.h','third_party/texstudio/src/texstudio.cpp',
 'third_party/texstudio/src/buildmanager.cpp','third_party/texstudio/src/buildmanager.h','third_party/texstudio/src/harmonyprocess.h',
 'scripts/texlive/latexmk_launcher.c','scripts/texlive/HarmonyCwd.pm','scripts/common/build_texlive_hnp.sh')]
paths += [p for p in (root/'build-support').iterdir() if p.is_file() and any(k in p.name for k in ('perl','latexmk','cwd','b31'))]
paths += [out/'hishell-test.sh',out/'test-harmony-cwd.pl',out/'REPAIR-1.0.16.md',root/'LATEXMK-B31.md']
hashes={}
for path in paths:
    relative=path.relative_to(root); target=snapshot/relative; target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target); hashes[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
(snapshot/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('1.0.16 B3.1 device acceptance recorded; seven PDFs have embedded fonts.')
