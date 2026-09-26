"""Exercise new Lua profile through production resource API, including rollback."""
import hashlib, json, os, pathlib, subprocess, tempfile, zipfile
root = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
cli = root/'validation/resources/resource-cli'
dist = repo/'build/build-texlive-ohos-dist'
out = root/'validation/lua-cli-1.0.23'
out.mkdir(parents=True, exist_ok=True)
def run(*args, ok=True):
    p = subprocess.run([str(cli), *map(str,args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (args,p.stdout,p.stderr)
    return p.stdout
with tempfile.TemporaryDirectory(prefix='lua-user-') as temp:
    work = pathlib.Path(temp); store = work/'store'; source = work/'module.lua'
    source.write_text('return {message="Lua user layer"}\n')
    rel = 'tex/luatex/testpkg/nested/module.lua'
    run('user-save',store,dist,rel,source)
    backup = work/'backup.zip'
    run('user-export',store,dist,backup)
    with zipfile.ZipFile(backup) as z:
        manifest = json.loads(z.read('manifest.json'))
        assert manifest['profile'] == 'additive-lua-v1'
        assert z.read('texmf/'+rel) == source.read_bytes()
    run('user-delete',store,dist,rel)
    run('user-restore',store,dist,backup)
    ident = run('import',work/'immutable',backup).strip()
    run('verify',work/'immutable',ident)
    for bad in ['tex/luatex/testpkg/module.so','tex/luatex/testpkg/module.luc','scripts/test.lua',
                '../escape.lua','tex/latex/l3kernel/a.lua','tex/luatex/testpkg/language.dat.lua']:
        run('user-save',store,dist,bad,source,ok=False)
    invalid = work/'invalid.zip'
    manifest['profile'] = 'additive-v1'
    with zipfile.ZipFile(invalid,'w') as z:
        z.writestr('manifest.json', json.dumps(manifest))
        z.writestr('texmf/'+rel,source.read_bytes())
    run('user-restore',store,dist,invalid,ok=False)
    assert (store/'texmf-home'/rel).read_bytes() == source.read_bytes()
    env = json.loads(run('environment',store,dist,'builtin'))
    assert str(store/'texmf-home') in env['LUAINPUTS']
    run('user-enable',store,'false')
    env = json.loads(run('environment',store,dist,'builtin'))
    assert str(store/'texmf-home') not in env['LUAINPUTS']
    backup.unlink()
    assert (store/'texmf-home'/rel).exists()
result = {'passed':True, 'checks':['Lua save/editable path','nested backup/restore','new immutable profile',
    'native module and core protection','old profile rejection','failed restore preserves user files',
    'enable/disable Lua search path','ZIP independence'], 'scope':'Host production C++ resource API; device Lua execution still requires acceptance.'}
(out/'resource-tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
