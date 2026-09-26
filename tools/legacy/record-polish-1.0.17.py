"""Record the observed device UI checks and verify the returned artifacts."""
import hashlib,json,pathlib,re,shutil,subprocess
root=pathlib.Path(__file__).resolve().parents[1];out=root/'validation/latexmk';v='1.0.17'
shell=out/f'device-hishell-{v}';app=out/f'device-app-{v}'/'B317'
shellroot=next(shell.rglob('hishell-result.txt')).parent
log=(shellroot/'hishell-result.txt').read_text(encoding='utf-8')
for marker in ('PASS: nested -cd project path','PASS: B3.1 automatic passes','PASS: locale initialization and Unicode round trip without warnings'):
    assert marker in log,marker
for p in [shellroot/'hishell-result.txt',*shellroot.rglob('*.stdout')]:
    t=p.read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Setting locale failed|Falling back to|Use of uninitialized',t),p
for loc in ('C','C.UTF-8','en_US.UTF-8'):
    assert json.loads((shellroot/f'locale-{loc}.json').read_text())['passed']
    assert (shellroot/f'locale-{loc}.stderr').stat().st_size==0
before=(out/f'cancel-before-{v}.txt').read_text(encoding='utf-8')
after=(out/f'cancel-after-{v}.txt').read_text(encoding='utf-8')
final=(out/f'final-processes-{v}.txt').read_text(encoding='utf-8')
for pid in (29864,29874,29875):
    assert re.search(r'^\s*'+str(pid)+r'\s',before,re.M)
    assert not re.search(r'^\s*'+str(pid)+r'\s',after,re.M)
assert re.search(r'^\s*24917\s',after,re.M) and re.search(r'^\s*24917\s',final,re.M)
assert not re.search(r'latexmk\.pl|pdflatex .*stop\.tex',final)
assert 'Undefined control sequence' in (app/'app-error.log').read_text(encoding='utf-8')
assert not (app/'app-error.pdf').exists()
pdfs={}
for directory in (shell,app):
    for pdf in directory.rglob('*.pdf'):
        if pdf.name=='stop.pdf':
            assert pdf.stat().st_size==0
            continue
        fonts=subprocess.check_output([r'E:\texlive\2024\bin\windows\pdffonts.exe',str(pdf)],text=True)
        pdf.with_suffix('.pdffonts.txt').write_text(fonts,encoding='utf-8')
        rows=fonts.splitlines()[2:];assert rows and all(row.split()[-5]=='yes' for row in rows)
        pdfs[pdf.relative_to(out).as_posix()]={'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'allFontsEmbedded':True,'fontCount':len(rows)}
assert len(pdfs)==7
for stem in ('app-xe','app-pdf'):
    assert (app/(stem+'.fdb_latexmk')).is_file()
    text=(app/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Undefined control sequence|Missing character:',text)
screens=['b317-xe.png','b317-cancel.png','b317-error.png','b317-error-message.png','b317-recovered.png']
for name in screens:assert (out/name).is_file()
sign=json.loads((root/f'validation/device-signing-{v}/result.json').read_text())
assert sign['signature_verified'] and sign['original_payloads_identical'] and sign['embedded_hnp_unchanged']
baseline=json.loads((out/'payload-check.json').read_text());assert baseline['passed']
result={'stage':'B3.1 polish','version':v,'date':'2026-09-17','installed':True,'passed':True,
 'scope':'Cancellation state and Perl UTF-8 locale; not exhaustive all-engine acceptance',
 'hishell':{'automaticAndIncremental':True,'bibliographyUpdate':True,'errorRecovery':True,'nestedChdir':True,
 'noResourceOverrides':True,'localeWarningAbsent':True,'localesTested':['C','C.UTF-8','en_US.UTF-8'],'unicodeFileRoundTrip':True},
 'application':{'xeAutoBuildAndPreview':True,'pdfAutoBuildAfterCancelAndError':True,'cancelledTextObserved':'已取消编译',
 'cancelDoesNotShowCrash':True,'cancelledPids':[29864,29874,29875],'applicationPid':24917,
 'applicationSurvived':True,'cancelStopsCommandChain':True,'realCompileErrorRetained':True,'screenshots':screens},
 'pdfs':pdfs,'baseline':baseline,'signedArtifact':sign,
 'remainingLimitations':['Preview timeout and external crash were not separately device-injected in this run; their kill/error paths remain distinct from user cancellation.',
 'Biber dependency audit only; Biber and LuaLaTeX are not delivered or validated.']}
(out/f'device-result-{v}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=root/'DELIVERY-MANIFEST.json';m=json.loads(manifest.read_text(encoding='utf-8'))
m['status']='1.0.17_B3.1_polish_device_validated';m['latestReport']='LATEXMK-POLISH-1.0.17.md';m['latexmkB31Polish']=result
m['biberB32']={'status':'dependency_audit_only','version':'2.21','directModules':45,'available':5,'unavailable':40,'report':'BIBER-B32.md','evidence':'validation/biber/dependency-audit.json'}
for path in (f'artifacts/TeXstudioHarmony-{v}-arm64-device-signed.hap',f'artifacts/texlive-{v}.hnp'):
    if path not in m['artifacts']:m['artifacts'].insert(0,path)
for path in (f'validation/latexmk/device-result-{v}.json',f'validation/device-signing-{v}/result.json','validation/biber/dependency-audit.json'):
    if path not in m['evidence']:m['evidence'].append(path)
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(root/'validation/resources/artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
print('1.0.17 device acceptance recorded; seven PDFs have embedded fonts.')
