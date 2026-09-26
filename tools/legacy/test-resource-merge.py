import json, os, pathlib, subprocess, tempfile
r=pathlib.Path(os.environ['DELIVERY_ROOT'])
cli=r/'validation/resources/resource-cli'
dist=pathlib.Path(os.environ['BUILD_REPO'])/'build/build-texlive-ohos-dist'
def run(*args, ok=True):
    p=subprocess.run([str(cli), *map(str,args)],capture_output=True,text=True)
    assert (p.returncode==0)==ok,(args,p.stdout,p.stderr)
with tempfile.TemporaryDirectory() as td:
    t=pathlib.Path(td); store=t/'store'; source=t/'source'; source.write_text('test')
    a='tex/latex/alpha/alpha.sty'; b='tex/luatex/beta/nested/beta.lua'
    run('user-save',store,dist,a,source)
    run('user-save',t/'second',dist,b,source)
    run('user-export',t/'second',dist,t/'beta.zip')
    run('user-mkdir',store,dist,'tex/latex/alpha/empty')
    run('user-merge',store,dist,t/'beta.zip')
    assert (store/'texmf-home'/a).read_text()=='test'
    assert (store/'texmf-home'/b).read_text()=='test'
    assert (store/'texmf-home/tex/latex/alpha/empty').is_dir()
    before={str(p.relative_to(store)):p.read_bytes() for p in (store/'texmf-home').rglob('*') if p.is_file()}
    run('user-merge',store,dist,t/'beta.zip',ok=False)
    after={str(p.relative_to(store)):p.read_bytes() for p in (store/'texmf-home').rglob('*') if p.is_file()}
    assert before==after
    for path in ('../../escape','tex/latex/base/x','tex/latex/l3kernel/x','bin/tools'):
        run('user-mkdir',store,dist,path,ok=False)
    (store/'texmf-home/tex/latex/link').symlink_to(t,target_is_directory=True)
    run('user-mkdir',store,dist,'tex/latex/link/new',ok=False)
    run('user-merge',store,dist,t/'beta.zip',ok=False)
    assert not (t/'new').exists()
result={'passed':True,'checks':['merge retains existing files','TDS subdirectories preserved','empty folders retained','collision rejects entire import','traversal/core/unsupported folders rejected','symlinks rejected']}
(r/'validation/interaction-1.0.24/resource-merge-tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
