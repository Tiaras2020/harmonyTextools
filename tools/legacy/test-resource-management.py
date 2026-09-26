"""Production C++ round-trip export and protected deletion regression."""
import json, os, pathlib, shutil, subprocess, tempfile, zipfile
root = pathlib.Path(os.environ['DELIVERY_ROOT'])
out = root/'validation/resources'
cli = out/'resource-cli'
results = {}
(out/'management-tests.json').write_text('{"passed":false}\n')
def run(*args, ok=True):
    p = subprocess.run([str(cli), *map(str,args)],capture_output=True,text=True)
    assert (p.returncode == 0) == ok, (args,p.stdout,p.stderr)
    return p.stdout.strip()
with tempfile.TemporaryDirectory(prefix='resource-management-') as tmp:
    tmp = pathlib.Path(tmp); store = tmp/'资源 storage'
    original = tmp/'input.zip'
    shutil.copy2(root/'artifacts/harmony-resource-demo-1.zip',original)
    ident = run('import',store,original)
    original.unlink()
    run('verify',store,ident)
    results['originalZipNotRequired'] = True
    run('activate',store,ident)
    state = (store/'active.json').read_bytes()
    run('remove',store,ident,'builtin',ok=False)
    assert (store/'active.json').read_bytes() == state
    results['nextStartupSelectionProtected'] = True
    export = tmp/'导出.zip'
    run('export',store,ident,export)
    with zipfile.ZipFile(export) as z:
        assert z.testzip() is None
        assert 'texmf/ls-R' not in z.namelist()
        assert z.read('manifest.json') == (store/'resources'/ident/'manifest.json').read_bytes()
    second = tmp/'second'
    assert run('import',second,export) == ident
    run('verify',second,ident)
    results['exportAndReimportSameIdentity'] = True
    run('export',store,ident,store/'resources'/ident/'manifest.json',ok=False)
    results['exportCannotOverwriteInstalledData'] = True
    run('activate',store,'builtin')
    run('remove',store,ident,ident,ok=False)
    results['runningSessionProtectedAfterRollback'] = True
    cache = store/'var/tl2025-harmony-baseline-1.0.5'/ident/'fontconfig'
    cache.mkdir(parents=True); (cache/'test').write_text('test')
    outside = tmp/'outside'; outside.mkdir(); (outside/'keep').write_text('keep')
    link = store/'resources/link'; link.symlink_to(outside,target_is_directory=True)
    run('remove',store,'link','builtin',ok=False)
    run('remove',store,'../outside','builtin',ok=False)
    assert (outside/'keep').read_text() == 'keep'
    results['deletionPathAndSymlinkProtection'] = True
    run('remove',store,ident,'builtin')
    assert not (store/'resources'/ident).exists() and not cache.parent.exists()
    assert (outside/'keep').exists()
    results['inactiveResourceAndCacheRemoved'] = True
    assert run('import',store,export) == ident
    results['restoreFromExportAfterDeletion'] = True
    file = next((store/'resources'/ident/'texmf').rglob('*.sty'))
    file.write_text('corrupt')
    preserved = tmp/'preserved.zip'; preserved.write_bytes(b'existing destination')
    run('export',store,ident,preserved,ok=False)
    assert preserved.read_bytes() == b'existing destination'
    results['corruptExportPreservesDestination'] = True
(out/'management-tests.json').write_text(json.dumps({'passed':True,'tests':results},indent=2)+'\n')
print(json.dumps(results,indent=2))
