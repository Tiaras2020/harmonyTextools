"""Exercise the production C++ importer and real TeX lookup/compilation."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import zipfile

root = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
out = root / 'validation/resources'
cli = out / 'resource-cli'
dist = repo / 'build/build-texlive-ohos-dist'
pack = root / 'artifacts/harmony-resource-demo-1.zip'
results = {}
(out/'host-tests.json').write_text(json.dumps({'passed': False, 'status': 'running'})+'\n')

def run(*args, ok=True):
    p = subprocess.run([str(cli), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (args, p.returncode, p.stdout, p.stderr)
    return p.stdout.strip()

def altered(path, change):
    with zipfile.ZipFile(pack) as z:
        content = [(info, z.read(info)) for info in z.infolist()]
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, data in change(content):
            z.writestr(info, data)

with tempfile.TemporaryDirectory(prefix='resource-regression-', dir='/tmp') as work:
    work = pathlib.Path(work)
    store = work / '中文 resources'
    id1 = run('import', store, pack)
    run('activate', store, id1)
    state = (store/'active.json').read_bytes()
    run('verify', store, id1)
    assert 'harmonyresourcedemo.sty' in (store/'resources'/id1/'texmf/ls-R').read_text()
    results['validImportIndexAndActivation'] = True
    run('import', store, pack, ok=False)
    results['duplicateVersionRejected'] = True

    def bad_manifest(items, key, value):
        for info, data in items:
            if info.filename == 'manifest.json':
                m = json.loads(data); m[key] = value; data = json.dumps(m).encode()
            yield info, data
    attacks = {
        'incompatible': lambda items: bad_manifest(items, 'compatibilityId', 'wrong-engine'),
        'pathTraversal': lambda items: [*items, ('../escaped.sty', b'bad')],
        'nativeExecutable': lambda items: [*items, ('bin/evil', b'\x7fELF')],
        'unlisted': lambda items: [*items, ('texmf/tex/latex/demo/extra.sty', b'bad')],
        'checksum': lambda items: [(i, d.replace(b'NeedsTeXFormat', b'NeedsTeXForMat') if i.filename.endswith('.sty') else d) for i,d in items],
        'duplicateEntry': lambda items: [*items, items[-1]],
        'missingEntry': lambda items: [x for x in items if not x[0].filename.endswith('.sty')],
    }
    symlink = zipfile.ZipInfo('texmf/tex/latex/link.sty'); symlink.external_attr = 0o120777 << 16
    attacks['symlink'] = lambda items: [*items, (symlink, b'/tmp/escape')]
    def relocate(items, new_name):
        old_name = next(i.filename for i,d in items if i.filename.endswith('.sty'))
        for info, data in items:
            if info.filename == old_name:
                info.filename = new_name
            elif info.filename == 'manifest.json':
                m = json.loads(data); m['files'][new_name] = m['files'].pop(old_name); data = json.dumps(m).encode()
            yield info, data
    attacks['coreReplacement'] = lambda items: relocate(items, 'texmf/tex/latex/base/latex.ltx')
    attacks['declaredNativeExecutable'] = lambda items: relocate(items, 'bin/evil')
    for name, change in attacks.items():
        bad = work/(name+'.zip'); altered(bad, change)
        run('import', store, bad, ok=False)
        assert (store/'active.json').read_bytes() == state
        assert not (work/'escaped.sty').exists()
        assert len(list((store/'resources').iterdir())) == 1
        assert not list(store.glob('.import-*'))
        results[name+'RejectedWithoutStateChange'] = True

    base_env = os.environ.copy()
    base_env.update(TEXMFROOT=str(dist), TEXMFDIST=str(dist/'texmf'), TEXMFCNF=str(dist/'texmf/web2c'))
    def environment(id):
        return {**base_env, **json.loads(run('environment', store, dist, id))}
    kpse = repo/'build/build-texlive-host/texk/kpathsea/kpsewhich'
    assert subprocess.run([str(kpse),'harmonyresourcedemo.sty'], env=environment('builtin'), capture_output=True).returncode != 0
    found = subprocess.check_output([str(kpse),'harmonyresourcedemo.sty'],env=environment(id1),text=True).strip()
    assert str(store/'resources'/id1) in found
    results['MissingBeforeFoundAfter'] = True
    index = subprocess.check_output([str(kpse),'--show-path','ls-R'],env=environment(id1),text=True)
    assert str(store/'resources'/id1/'texmf') in index
    results['editorIndexPath'] = True
    main = work/'resource-demo.tex'; shutil.copy2(out/'fixture/resource-demo.tex', main)
    proc = subprocess.run([str(repo/'build/build-texlive-host/texk/web2c/pdftex'), '-progname=pdflatex', '-halt-on-error', '-interaction=nonstopmode', '-recorder', main.name],cwd=work,env=environment(id1),capture_output=True)
    (out/'compile.stdout').write_bytes(proc.stdout+proc.stderr)
    assert proc.returncode == 0
    shutil.copy2(work/'resource-demo.pdf', out/'resource-demo.pdf')
    shutil.copy2(work/'resource-demo.log', out/'resource-demo.log')
    assert str(store) in (work/'resource-demo.fls').read_text()
    results['realPdfCompilation'] = True
    run('activate', store, 'builtin')
    assert json.loads((store/'active.json').read_text())['id'] == ''
    assert subprocess.run([str(kpse),'harmonyresourcedemo.sty'],env=environment('builtin'),capture_output=True).returncode != 0
    run('activate', store, id1)
    results['rollbackAndReactivate'] = True
    resource = store/'resources'/id1/'texmf/tex/latex/harmony-resource-demo/harmonyresourcedemo.sty'
    resource.write_bytes(resource.read_bytes()+b'changed')
    run('verify', store, id1, ok=False)
    run('activate', store, id1, ok=False)
    results['installedCorruptionDetected'] = True

(out/'host-tests.json').write_text(json.dumps({'passed': True, 'tests': results},indent=2)+'\n')
print(json.dumps(results, indent=2))
