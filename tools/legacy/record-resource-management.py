"""Record 1.0.8 evidence without rewriting 1.0.7 acceptance records."""
import hashlib, json, pathlib, shutil, zipfile
import fitz
root = pathlib.Path(__file__).resolve().parent.parent
out = root/'validation/resources'
version = '1.0.8'
assert json.loads((root/'texstudio-harmony/release.json').read_text())['version'] == version
assert json.loads((out/'management-tests.json').read_text())['passed']
assert json.loads((out/'host-tests.json').read_text())['passed']
log = (out/f'device-compile-{version}.log').read_text()
assert 'texlive_1.0.8' in log and '/files/tex-resources/resources/' in log
pdf = fitz.open(out/f'device-compile-{version}.pdf')
assert len(pdf) == 1 and 'Offline resource import works.' in pdf[0].get_text()
with zipfile.ZipFile(out/'device-export.zip') as z, zipfile.ZipFile(root/'artifacts/harmony-resource-demo-1.zip') as original:
    assert z.testzip() is None and set(z.namelist()) == set(original.namelist())
    assert all(z.read(n) == original.read(n) for n in z.namelist())
sign_path = root/f'validation/device-signing-{version}/result.json'
sign = json.loads(sign_path.read_text())
signed = root/'artifacts'/sign['signed_file']
assert sign['signature_verified'] and hashlib.sha256(signed.read_bytes()).hexdigest() == sign['sha256']
sign['installed'] = True
sign_path.write_text(json.dumps(sign,indent=2)+'\n')
report = {'version':version,'installed':True,'nativeSavePickerExport':True,
          'exportedPayloadsIdentical':True,'activeDeletionProtected':True,
          'deleteAfterRollbackAndRestart':True,'reimportExportedZip':True,
          'restartedPdflatexAndPreview':True,'pdfPages':1,
          'hostManagementTests':9,'hostImportRegressionTests':17,
          'terminalValidation': {
              'HiShell': {'pdftex':'user_reported_available','xelatex':'user_reported_available',
                          'importedPrivateResources':'not_verified'},
              'hdcShell':'pdflatex_not_on_PATH_and_direct_physical_entry_permission_denied; not_representative_of_HiShell'},
          'newEngineBuild':False}
(out/f'device-result-{version}.json').write_text(json.dumps(report,indent=2)+'\n')
manifest_path = root/'DELIVERY-MANIFEST.json'
m = json.loads(manifest_path.read_text(encoding='utf-8'))
m['status'] = '1.0.8_resource_export_delete_restore_device_validated'
m['resourceExtension']['deviceEvidence'] = f'validation/resources/device-result-{version}.json'
m['resourceExtension']['managementTests'] = 'validation/resources/management-tests.json'
m['resourceExtension']['design'] = 'RESOURCE-DESIGN.md'
for name in [sign['signed_file'],f'texlive-{version}.hnp']:
    rel = 'artifacts/'+name
    if rel not in m['artifacts']: m['artifacts'].insert(0,rel)
manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory = [{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(out/'artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
source = out/f'source-{version}'
paths = [x['path'] for x in json.loads((out/'source-1.0.7/manifest.json').read_text())]
files = []
for rel in paths:
    src = root/'texstudio-harmony'/rel; dst = source/rel
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    files.append({'path':rel,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(source/'manifest.json').write_text(json.dumps(files,indent=2)+'\n')
print(json.dumps(report,indent=2))
