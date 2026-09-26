"""Production importer profile boundaries and a real full ZIP on a slim runtime."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

root=Path(os.environ['DELIVERY_ROOT']); repo=Path(os.environ['BUILD_REPO'])
common=os.environ.get('HARMONY_COMMON_IMPORT') == '1'
out=root/('validation/common-resources/import-tests' if common else 'validation/full-resources/import-tests'); out.mkdir(exist_ok=True)
cli=root/'validation/resources/resource-cli'
compat=json.loads((root/'texstudio-harmony/release.json').read_text())['compatibilityId']
result={'passed':False,'checks':{}}
def run(*args,ok=True):
    p=subprocess.run([str(cli),*map(str,args)],capture_output=True,text=True)
    assert (p.returncode==0)==ok,(args,p.stdout,p.stderr)
    return p.stdout.strip()
def pack(path,files,profile='runtime-extension-v1'):
    m={'schema':1,'profile':profile,'id':'profile-test','version':'1','compatibilityId':compat,
       'files':{n:{'size':len(v),'sha256':hashlib.sha256(v).hexdigest()} for n,v in files.items()}}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(m))
        for n,v in files.items(): z.writestr(n,v)
try:
    with tempfile.TemporaryDirectory(prefix='harmony-profile-') as temp:
        temp=Path(temp)
        types=['fonts/tfm/a.tfm','fonts/vf/a.vf','fonts/type1/a.pfb','fonts/enc/a.enc','fonts/map/a.map','makeindex/a.ist','tex/latex/a/a.bbx','fonts/cmap/Identity-H']
        pack(temp/'valid.zip',{'texmf/'+n:b'data' for n in types})
        id=run('import',temp/'store',temp/'valid.zip'); run('verify',temp/'store',id)
        result['checks']['fullResourceFileTypes']=True
        for n in ['texmf/web2c/texmf.cnf','texmf/web2c/pdflatex.fmt','texmf/tex/latex/base/latex.ltx','texmf/tex/latex/l3kernel/expl3.sty','texmf/scripts/install.lua','texmf/fonts/conf/fonts.conf','bin/xelatex','../outside.pfb']:
            pack(temp/'bad.zip',{n:b'data'})
            run('import',temp/'store',temp/'bad.zip',ok=False)
        result['checks']['coreConfigFormatScriptBinaryTraversalRejected']=True
        pack(temp/'old.zip',{'texmf/fonts/type1/a.pfb':b'data'},'additive-v1')
        run('import',temp/'store',temp/'old.zip',ok=False)
        result['checks']['legacyProfileRemainsRestricted']=True
    store=repo/'build'/('common-import-test-store' if common else 'full-import-test-store')
    archive=root/'artifacts'/('harmony-full-resources-2025.2.zip' if common else 'harmony-full-resources-2025.1.zip')
    if os.environ.get('HARMONY_RESUME_IMPORT') == '1':
        assert common and store.exists()
        installed=list((store/'resources').iterdir())
        assert len(installed)==1
        id=installed[0].name
        with zipfile.ZipFile(archive) as z:
            assert json.loads(z.read('manifest.json'))==json.loads((installed[0]/'manifest.json').read_text())
        run('verify',store,id)
        result['resumedVerifiedImport']=True
    else:
        assert not store.exists(), 'Preserve prior import evidence'
        id=run('import',store,archive)
    run('activate',store,id)
    slim=repo/'build/build-texlive-ohos-dist'
    env=os.environ.copy()
    env.update(TEXMFROOT=str(slim),TEXMFDIST=str(slim/'texmf'),TEXMFCNF=str(slim/'texmf/web2c'))
    env.update(json.loads(run('environment',store,slim,id)))
    kpse=repo/'build/build-texlive-host/texk/kpathsea/kpsewhich'
    for name in ('pdftex.map','qrcode.sty','AccanthisADFStdNo3-Regular.pfb'):
        found=subprocess.check_output([str(kpse),name],env=env,text=True).strip()
        assert str(store/'resources'/id) in found,(name,found)
    result['checks']['fullArchiveImportAndMapPrecedence']=True
    for name in ('new-packages','new-type1-font'):
        work=out/name; work.mkdir(exist_ok=True)
        shutil.copy2(root/'validation/full-resources/fixtures'/(name+'.tex'),work)
        p=subprocess.run([str(repo/'build/build-texlive-host/texk/web2c/pdftex'),'-progname=pdflatex','-halt-on-error','-interaction=nonstopmode','-recorder',name+'.tex'],cwd=work,env=env,capture_output=True)
        (work/'compile.stdout').write_bytes(p.stdout+p.stderr)
        assert p.returncode==0,name
        assert str(store) in (work/(name+'.fls')).read_text()
    result['checks']['slimPlusImportedMacrosAndType1Compile']=True
    if common:
        driver=repo/'build/build-texlive-host/texk/dvipdfm-x/xdvipdfmx'
        for name,engine in [('beamer-zh','xetex'),('pgfplots-test','pdftex'),('newpx-test','pdftex'),('bibtex-zh','xetex')]:
            work=out/name; work.mkdir(exist_ok=True)
            for src in (root/'validation/common-resources/fixtures').iterdir(): shutil.copy2(src,work)
            command=[str(repo/'build/build-texlive-host/texk/web2c'/engine),'-progname='+('xelatex' if engine=='xetex' else 'pdflatex'),'-recorder','-halt-on-error','-interaction=nonstopmode']
            if engine=='xetex': command.append('-output-driver='+str(driver)+' -q -E')
            for index in range(3):
                p=subprocess.run(command+[name+'.tex'],cwd=work,env=env,capture_output=True)
                (work/f'pass-{index+1}.stdout').write_bytes(p.stdout+p.stderr)
                assert p.returncode==0,(name,index)
                if name=='bibtex-zh' and index==0:
                    bib=subprocess.run([str(repo/'build/build-texlive-host/texk/web2c/bibtex'),name],cwd=work,env=env,capture_output=True)
                    (work/'bibtex.stdout').write_bytes(bib.stdout+bib.stderr)
                    assert bib.returncode==0
            log=(work/(name+'.log')).read_text()
            assert 'undefined references' not in log and 'Missing character:' not in log,name
            recorder=(work/(name+'.fls')).read_text()
            if name!='bibtex-zh': assert str(store) in recorder,name
            for line in recorder.splitlines():
                if line.startswith('INPUT /'):
                    path=Path(line[6:]).resolve()
                    assert any(path.is_relative_to(p.resolve()) for p in (slim,store,work)),line
        result['checks']['reviewedFeaturesCompileOnSlimWithV2Import']=True
    run('activate',store,'builtin')
    env.update(json.loads(run('environment',store,slim,'builtin')))
    assert subprocess.run([str(kpse),'qrcode.sty'],env=env,capture_output=True).returncode!=0
    result['checks']['rollbackRemovesImportedLookup']=True
    result.update(passed=True,store=str(store),resourceId=id)
finally:
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
