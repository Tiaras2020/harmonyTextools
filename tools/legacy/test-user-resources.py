"""Exercise editable resources with production C++, actual kpathsea and pdfTeX."""
import json, os, pathlib, subprocess, tempfile, zipfile, shutil
root = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
out = root/'validation/resources'
cli = out/'resource-cli'
dist = repo/'build/build-texlive-ohos-dist'
kpse = repo/'build/build-texlive-host/texk/kpathsea/kpsewhich'
pdftex = repo/'build/build-texlive-host/texk/web2c/pdftex'
results = {}
(out/'user-tests.json').write_text('{"passed":false}\n')
def run(*args, ok=True):
    p = subprocess.run([str(cli), *map(str,args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (args,p.stdout,p.stderr)
    return p.stdout.strip()
with tempfile.TemporaryDirectory(prefix='user-resource-') as tmp:
    work = pathlib.Path(tmp); store = work/'中文 user resources'
    ident = run('import',store,root/'artifacts/harmony-resource-demo-1.zip')
    rel = 'tex/latex/user/harmonyresourcedemo.sty'
    source = work/'edit.sty'
    source.write_text('\\ProvidesPackage{harmonyresourcedemo}\n\\newcommand{\\HarmonyResourceMessage}{Editable user layer works.}\n')
    run('user-save',store,dist,rel,source)
    def env():
        return dict(os.environ, TEXMFROOT=str(dist), TEXMFDIST=str(dist/'texmf'), TEXMFCNF=str(dist/'texmf/web2c'), **json.loads(run('environment',store,dist,ident)))
    def find():
        return subprocess.check_output([str(kpse),'harmonyresourcedemo.sty'],env=env(),text=True).strip()
    assert '/texmf-home/' in find()
    assert ident in run('user-conflicts',store,dist,rel,ident)
    main = work/'user-demo.tex'
    main.write_text('\\documentclass{article}\n\\usepackage{harmonyresourcedemo}\n\\begin{document}\\HarmonyResourceMessage\\typeout{RESULT: \\HarmonyResourceMessage}\\end{document}\n')
    def compile(expected):
        p = subprocess.run([str(pdftex),'-progname=pdflatex','-halt-on-error','-interaction=nonstopmode','-recorder',main.name],cwd=work,env=env(),capture_output=True)
        assert p.returncode == 0, p.stdout.decode(errors='replace')
        text = (work/'user-demo.log').read_text()
        shutil.copy2(work/'user-demo.pdf',out/'user-host.pdf')
        assert expected in text, text
    compile('Editable user layer works.')
    results['userOverrideAndActualPdf'] = True
    source.write_text(source.read_text().replace('Editable user layer works.', 'Saved edit is effective.'))
    run('user-save',store,dist,rel,source); compile('Saved edit is effective.')
    results['nextCompileSeesEdits'] = True
    run('user-enable',store,'false'); assert '/resources/' in find(); compile('Offline resource import works.')
    run('user-enable',store,'true'); assert '/texmf-home/' in find()
    results['disableFallsBackAndReenable'] = True
    backup = work/'用户备份.zip'; run('user-export',store,dist,backup)
    with zipfile.ZipFile(backup) as z:
        assert z.read('texmf/'+rel) == source.read_bytes()
        assert 'texmf/ls-R' not in z.namelist()
    run('user-delete',store,dist,rel); assert '/resources/' in find()
    run('user-restore',store,dist,backup); backup.unlink(); compile('Saved edit is effective.')
    results['backupDeleteRestoreWithoutOriginalZip'] = True
    for bad in ['../escape.sty','tex/latex/user/latex.ltx','tex/latex/user/article.cls','tex/latex/user/expl3.sty','bin/evil','web2c/texmf.cnf']:
        run('user-save',store,dist,bad,source,ok=False)
    assert not (store/'escape.sty').exists()
    results['coreBasenameAndTraversalProtected'] = True
    external = work/'outside'; external.mkdir()
    link = store/'texmf-home/tex/latex/linked'; link.symlink_to(external,target_is_directory=True)
    run('user-save',store,dist,'tex/latex/linked/escape.sty',source,ok=False)
    assert not list(external.iterdir()); link.unlink()
    results['symlinkRejected'] = True
    badzip = work/'bad.zip'; badzip.write_bytes(b'invalid')
    before = (store/'texmf-home'/rel).read_bytes()
    run('user-restore',store,dist,badzip,ok=False)
    assert (store/'texmf-home'/rel).read_bytes() == before
    results['failedRestorePreservesEdits'] = True
    cache1 = env()['TEXMFVAR']; run('user-refresh',store); assert env()['TEXMFVAR'] != cache1
    results['explicitFontCacheRefresh'] = True
    # A user font becomes visible, then disappears when disabled or removed.
    font = pathlib.Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    fontrel = 'fonts/truetype/user/UserTest.ttf'
    run('user-save',store,dist,fontrel,font)
    def fontpath():
        return subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans'],env=env(),text=True)
    assert '/texmf-home/' in fontpath()
    run('user-enable',store,'false'); assert '/texmf-home/' not in fontpath()
    run('user-enable',store,'true'); assert '/texmf-home/' in fontpath()
    run('user-delete',store,dist,fontrel); assert '/texmf-home/' not in fontpath()
    results['fontAddDisableReenableDelete'] = True
    # Standard backup is also usable as an immutable package on another install.
    run('user-export',store,dist,backup)
    restored = run('import',work/'other',backup); run('verify',work/'other',restored)
    results['backupInteroperatesWithResourceImporter'] = True
(out/'user-tests.json').write_text(json.dumps({'passed':True,'tests':results},indent=2)+'\n')
print(json.dumps(results,indent=2))
