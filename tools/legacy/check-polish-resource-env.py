"""Check actual kpathsea lookup through the production app environment."""
import json,os,pathlib,subprocess,tempfile
root=pathlib.Path(os.environ['DELIVERY_ROOT']);repo=pathlib.Path(os.environ['BUILD_REPO']);out=root/'validation/biber/polish-1.0.19'
dist=repo/'build/resource-release-1.0.19';kpse=repo/'build/build-texlive-host/texk/kpathsea/kpsewhich'
with tempfile.TemporaryDirectory(prefix='b319-env-') as temp:
    store=pathlib.Path(temp)
    fake=store/'texmf-home/dvipdfmx/dvipdfmx.cfg';fake.parent.mkdir(parents=True);fake.write_text('not a bundled config')
    app=json.loads(subprocess.check_output([str(out/'resource-cli'),'environment',str(store),str(dist),'builtin']))
    env=dict(os.environ,**app);env.update(TEXMFROOT=str(dist),TEXMFDIST=str(dist/'texmf'),TEXMFCNF=str(dist/'texmf/web2c'))
    results={}
    for program in ('dvipdfmx','xdvipdfmx'):
        found=subprocess.check_output([str(kpse),'--progname='+program,'--format=other text files','dvipdfmx.cfg'],env=env,text=True).strip()
        assert found==str(dist/'texmf/dvipdfmx/dvipdfmx.cfg'),found
        results[program]=found
    for name in ('pdftex.map','ckx.map'):
        found=subprocess.check_output([str(kpse),'--format=map',name],env=env,text=True).strip();assert found.startswith(str(dist)),found
        results[name]=found
    # HiShell relies only on texmf.cnf, without the app's environment overrides.
    terminal=dict(os.environ,TEXMFROOT=str(dist),TEXMFDIST=str(dist/'texmf'),TEXMFCNF=str(dist/'texmf/web2c'))
    found=subprocess.check_output([str(kpse),'--progname=xdvipdfmx','--format=other text files','dvipdfmx.cfg'],env=terminal,text=True).strip()
    assert found==results['xdvipdfmx']
report={'passed':True,'lookups':results,'userConfigCannotOverrideBundledDriver':True,'terminalConfigLookup':True}
(out/'resource-env-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
