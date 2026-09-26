"""Record the actual 1.0.15 device test, including its application failure."""
import hashlib,json,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'validation/latexmk'
work=out/'device-hishell'
log=next(work.rglob('hishell-result.txt')).read_text(encoding='utf-8')
assert 'PASS: B3.1 automatic passes' in log
pdfs={}
for pdf in work.rglob('*.pdf'):
    fonts=subprocess.check_output([r'E:\texlive\2024\bin\windows\pdffonts.exe',str(pdf)],text=True)
    pdf.with_suffix('.pdffonts.txt').write_text(fonts,encoding='utf-8')
    rows=fonts.splitlines()[2:]
    assert rows and all(row.split()[-5]=='yes' for row in rows)
    pdfs[pdf.name]={'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'fontCount':len(rows),'allFontsEmbedded':True}
assert len(pdfs)==4
result={'stage':'B3.1','version':'1.0.15','date':'2026-09-17','installed':True,'passed':False,
 'status':'device-tested-application-autobuild-failed',
 'hishell':{'passed':True,'publicCommands':True,'manualResourceOverrides':False,'cases':pdfs,
 'automaticPasses':True,'incrementalNoOp':True,'bibliographyEdit':True,'errorRecovery':True,'unicodeSpaceDirectory':True,
 'warnings':['Perl locale fallback to C','latexmk path normalization uninitialized values']},
 'application':{'xeAutoBuild':False,'pdfAutoBuild':False,'ordinaryBuildAndPreview':True,'ordinaryBuildEvidence':'validation/latexmk/manual.png','cancelCompilation':'blocked before compiler launch',
 'error':'File::Find cwd is undefined; Cannot change directory; latexmk exits before compilation',
 'screenshots':['validation/latexmk/xe-result.png','validation/latexmk/pdf-result.png']},
 'diagnosis':{'evidence':'validation/latexmk/cwd-diagnostic.txt',
 'getcwd':'undef, errno 1: Operation not permitted','fastcwd':'undef, errno 1',
 'abs_path':'undef, errno 13: Permission denied','cwd':'logical path available in HiShell',
 'next':'Verify child working directory/PWD propagation and safe logical-path fallback; rebuild new version and rerun application tests'},
 'lastFullyAcceptedVersion':'1.0.14'}
(out/'device-result-1.0.15.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifestpath=root/'DELIVERY-MANIFEST.json'; manifest=json.loads(manifestpath.read_text(encoding='utf-8'))
manifest['B3.1-candidate']['installed']=True
manifest['B3.1-candidate']['status']=result['status']
manifest['B3.1-candidate']['deviceBlocker']=result['application']['error']
manifest['B3.1-device-test']=result
relative='validation/latexmk/device-result-1.0.15.json'
if relative not in manifest['evidence']: manifest['evidence'].append(relative)
manifestpath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Device test recorded: HiShell passed, application auto-build failed.')
