"""Check production resource environment with real Kpathsea searches."""
import json, os, pathlib, subprocess, tempfile
root = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
out = root / 'validation/luahbtex'
kpse = repo / 'build/build-texlive-host/texk/kpathsea/kpsewhich'
with tempfile.TemporaryDirectory(prefix='luahb-env-') as temp:
    store = pathlib.Path(temp) / 'store'
    store.mkdir()
    (store / 'user-font-revision').write_text('initial')
    bundled = pathlib.Path(temp) / 'runtime'
    sty = bundled / 'texmf/tex/luatex/luatexbase/luatexbase.sty'
    sty.parent.mkdir(parents=True)
    sty.write_text('% lookup fixture')
    script = bundled / 'texmf/tex/luatex/luaotfload/luaotfload-main.lua'
    script.parent.mkdir(parents=True)
    script.write_text('-- lookup fixture')
    app = json.loads(subprocess.check_output([str(out / 'resource-cli'), 'environment', str(store), str(bundled), 'builtin']))
    assert app['TEXMFCACHE'] == app['TEXMFVAR']
    assert pathlib.Path(app['TEXMFCACHE']).is_dir()
    env = dict(os.environ, **app)
    env['TEXMFCNF'] = str(repo / 'build/resource-release-1.0.19/texmf/web2c')
    results = {}
    for file, fmt in ((sty, 'tex'), (script, 'lua')):
        found = subprocess.check_output([str(kpse), '--progname=lualatex', '--format=' + fmt, file.name], env=env, text=True).strip()
        assert found == str(file), (file, found)
        results[file.name] = found
    (store / 'user-font-revision').write_text('revision2')
    changed = json.loads(subprocess.check_output([str(out / 'resource-cli'), 'environment', str(store), str(bundled), 'builtin']))
    assert changed['TEXMFCACHE'] != app['TEXMFCACHE']
    assert 'openout_any' not in app
report = {'passed': True, 'luaStyleLookup': True, 'luaModuleLookup': True, 'fontRevisionIsolatesCache': True, 'outputRestrictionsUnchanged': True}
(out / 'app-env-result.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
