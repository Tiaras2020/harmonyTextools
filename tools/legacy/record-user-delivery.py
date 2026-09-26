"""Record B2.1 evidence after final installation and UI acceptance."""
import hashlib, json, pathlib, shutil, zipfile
import fitz
root = pathlib.Path(__file__).resolve().parent.parent
out = root/'validation/resources'
version = '1.0.11'
assert json.loads((root/'texstudio-harmony/release.json').read_text())['version'] == version
for name in ['host-tests.json','management-tests.json','user-tests.json']:
    assert json.loads((out/name).read_text())['passed'], name
pdfs = {
    'device-user-1.0.11.pdf': 'User edit works.',
    'device-user-disabled-1.0.10.pdf': 'Offline resource import works.',
    'hishell-pdftex-1.0.10.pdf': 'User edit works.',
    'hishell-xelatex-1.0.10.pdf': 'User edit works.',
}
for file, expected in pdfs.items():
    doc = fitz.open(out/file)
    assert len(doc) == 1 and expected in doc[0].get_text(), file
log = (out/'device-user-1.0.11.log').read_text()
assert '/texmf-home/' in log and 'texlive_1.0.11' in log
disabled = (out/'device-user-disabled-1.0.10.log').read_text()
assert '/tex-resources/resources/' in disabled and '/texmf-home/' not in disabled
assert 'HISHELL_USER_RESOURCE_PASSED' in (out/'hishell-result-1.0.10.txt').read_text()
with zipfile.ZipFile(out/'device-user-backup.zip') as z:
    assert z.testzip() is None
    assert b'User edit works.' in z.read('texmf/tex/latex/harmony-resource-demo/harmonyresourcedemo.sty')
for v in ['1.0.9','1.0.10','1.0.11']:
    path = root/f'validation/device-signing-{v}/result.json'
    sign = json.loads(path.read_text())
    assert sign['signature_verified']
    assert hashlib.sha256((root/'artifacts'/sign['signed_file']).read_bytes()).hexdigest() == sign['sha256']
    sign['installed'] = True
    path.write_text(json.dumps(sign,indent=2)+'\n')
report = {
    'version': version, 'installed': True, 'stage': 'B2.1', 'newEngineBuild': False,
    'hostTests': {'import':17,'management':9,'userLayer':10},
    'device': {
        'restoreAdditiveZipAsEditableFiles': True,
        'editAndExportExactPayload': True,
        'compileFromPrivateUserLayer': True,
        'disableWithoutRestartFallsBackToRelease': True,
        'deleteUserMacroAndRestoreBackup': True,
        'restoredContentPersistsAcrossUpgrade': True,
        'finalVersionCompileAndPreview': True,
        'longConflictPathsScrollable': True,
    },
    'terminal': {
        'application': 'HiShell', 'testedRuntime': '1.0.10',
        'publicHnpCommands': True, 'privateResourcesAutomaticallyVisible': False,
        'exportUnzipExplicitTexinputs': True, 'pdflatexPdf': True,'xelatexPdf': True,
        'liveSharedDirectory': False,
    },
    'limits': ['existing font-map warnings remain','user-font name lookup tested on host, not HiShell',
               'full TeX Live resource collection and new native toolchains are B2.2 or later'],
    'pdfChecks': pdfs,
}
(out/f'device-result-{version}.json').write_text(json.dumps(report,indent=2)+'\n')
paths = [x['path'] for x in json.loads((out/'source-1.0.8/manifest.json').read_text())]
paths.append('third_party/texstudio/src/harmonyuserresourcesdialog.cpp')
source = out/f'source-{version}'
records = []
for rel in paths:
    src=root/'texstudio-harmony'/rel; dst=source/rel
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    records.append({'path':rel,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(source/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
for file in ['host-tests.json','management-tests.json','user-tests.json']:
    shutil.copy2(out/file,source/file)
m_path=root/'DELIVERY-MANIFEST.json'; m=json.loads(m_path.read_text(encoding='utf-8'))
m['status']='1.0.11_B2.1_user_resources_and_HiShell_export_sync_validated'
m['latestReport']='USER-RESOURCES.md'
m['resourceExtension'].update(userLayerReport='USER-RESOURCES.md',
    userLayerDeviceEvidence=f'validation/resources/device-result-{version}.json',
    userLayerHostEvidence='validation/resources/user-tests.json',
    nextMilestone='B2.2 fixed-release full resource dependencies, font maps and storage preflight',
    userLayerSourceSnapshot=f'validation/resources/source-{version}/manifest.json',
    intermediateUserLayerVersions=['1.0.9','1.0.10'])
m['deviceFeedback']['HiShell']={'pdftex':'device_tested_PDF_pass','xelatex':'device_tested_PDF_pass',
    'importedPrivateResources':'not_automatically_visible','exportedUserResources':'unzip_and_explicit_TEXINPUTS_PDF_pass'}
for name in [f'TeXstudioHarmony-{version}-arm64-device-signed.hap',f'texlive-{version}.hnp']:
    rel='artifacts/'+name
    if rel not in m['artifacts']: m['artifacts'].insert(0,rel)
m_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(out/'artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
print(json.dumps(report,indent=2))
