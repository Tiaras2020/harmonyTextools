"""Record the verified B1 delivery, without modifying historical baseline evidence."""
import hashlib, json, pathlib, shutil
root = pathlib.Path(__file__).resolve().parent.parent
out = root/'validation/resources'
log = (out/'device-compile.log').read_text()
assert '/data/storage/el2/base/files/tex-resources/resources/' in log
assert 'Output written on compile-demo.pdf (1 page' in log
assert json.loads((out/'host-tests.json').read_text())['passed']
assert json.loads((out/'font-tests.json').read_text())['passed']
signed = root/'artifacts/TeXstudioHarmony-1.0.7-arm64-device-signed.hap'
signature = json.loads((root/'validation/device-signing-1.0.7/result.json').read_text())
assert hashlib.sha256(signed.read_bytes()).hexdigest() == signature['sha256']
report = {'version':'1.0.7','installed':True,'nativePickerImport':True,
          'restartThenApplicationPdflatex':True,'sandboxResourcePathInLog':True,
          'pdfPages':1,'internalPreview':True,'newFontsDeviceXelatex':'not_tested',
          'fdsanEnginePatchIncluded':False,'fullToolchainValidated':False,
          'signedSha256':signature['sha256']}
(out/'device-result.json').write_text(json.dumps(report,indent=2)+'\n')
signature['installed'] = True
(root/'validation/device-signing-1.0.7/result.json').write_text(json.dumps(signature,indent=2)+'\n')
manifest_path = root/'DELIVERY-MANIFEST.json'
m = json.loads(manifest_path.read_text(encoding='utf-8'))
m['latestReport'] = 'RESOURCE-EXTENSION.md'
m['status'] = '1.0.7_B1_resource_import_and_pdflatex_device_validated'
m['artifactListSemantics'] = 'artifacts preserves historical names; use currentArtifactInventory for actual files; user-deleted artifacts must not be restored'
m['resourceExtension'] = {'report':'RESOURCE-EXTENSION.md', 'deviceEvidence':'validation/resources/device-result.json',
                          'hostEvidence':'validation/resources/host-tests.json','fontEvidence':'validation/resources/font-tests.json',
                          'compatibilityId':'tl2025-harmony-baseline-1.0.5','supersededDebugVersion':'1.0.6'}
for name in ['TeXstudioHarmony-1.0.7-arm64-device-signed.hap','texlive-1.0.7.hnp','harmony-resource-demo-1.zip']:
    rel = 'artifacts/'+name
    if rel not in m['artifacts']: m['artifacts'].insert(0,rel)
inventory = [{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size} for p in sorted((root/'artifacts').iterdir()) if p.is_file()]
(out/'artifact-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
m['currentArtifactInventory'] = 'validation/resources/artifact-inventory.json'
manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source = out/'source-1.0.7'
paths = ['release.json','scripts/release_config.py','scripts/common/build_texlive_hnp.sh',
         'third_party/texstudio/src/quazip/quazip/CMakeLists.txt']
paths += ['third_party/texstudio/src/'+p for p in ['harmonyresources.h','harmonyresources.cpp','harmonyresourcesdialog.cpp','harmonyRelease.h','texstudio.cpp','utilsSystem.cpp','CMakeLists.txt']]
files = []
for rel in paths:
    src = root/'texstudio-harmony'/rel; dst = source/rel
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    files.append({'path':rel,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(source/'manifest.json').write_text(json.dumps(files,indent=2)+'\n')
print(json.dumps(report,indent=2))
