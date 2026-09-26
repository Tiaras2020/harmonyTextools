"""Record a signed but not yet device-accepted B3.1 candidate."""
import hashlib,json,pathlib,shutil
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'validation/latexmk'
package=json.loads((root/'artifacts/package-check-1.0.15.json').read_text())
sign=json.loads((root/'validation/device-signing-1.0.15/result.json').read_text())
report={'stage':'B3.1','version':'1.0.15','status':'signed-candidate-awaiting-device-validation',
        'deviceAccepted':False,'installed':False,'deviceBlocker':'Device is screen-locked; interactive HiShell/app launch denied by HarmonyOS',
        'hostRegression':json.loads((out/'host-regression/result.json').read_text()),
        'ohosPerlEmulation':json.loads((out/'qemu-result.json').read_text()),
        'launcher':json.loads((out/'launcher-tests.json').read_text()),
        'payload':json.loads((out/'payload-check.json').read_text()),
        'signingEvidence':'validation/device-signing-1.0.15/result.json',
        'packageEvidence':'artifacts/package-check-1.0.15.json',
        'lastDeviceAcceptedVersion':'1.0.14'}
(out/'candidate-result-1.0.15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifestpath=root/'DELIVERY-MANIFEST.json'; manifest=json.loads(manifestpath.read_text(encoding='utf-8'))
manifest['B3.1-candidate']=report
for relative in ('artifacts/TeXstudioHarmony-1.0.15-arm64-device-signed.hap','artifacts/texlive-1.0.15.hnp'):
    assert (root/relative).is_file()
    if relative not in manifest['artifacts']: manifest['artifacts'].insert(0,relative)
for relative in ('validation/latexmk/candidate-result-1.0.15.json','validation/device-signing-1.0.15/result.json'):
    if relative not in manifest['evidence']: manifest['evidence'].append(relative)
manifestpath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Reproducible source snapshot: reviewed application files and B3.1 build/test scripts only.
snapshot=out/'source-1.0.15'; snapshot.mkdir(exist_ok=True)
files=[root/'texstudio-harmony'/p for p in ('release.json','third_party/texstudio/src/texstudio.cpp',
    'third_party/texstudio/src/buildmanager.cpp','third_party/texstudio/src/buildmanager.h',
    'third_party/texstudio/src/harmonyprocess.h','third_party/texstudio/src/harmonyRelease.h',
    'scripts/texlive/latexmk_launcher.c','scripts/common/build_texlive_hnp.sh')]
files += [p for p in (root/'build-support').glob('*') if p.is_file() and any(k in p.name for k in ('perl','latexmk'))]
files += [out/'hishell-test.sh',out/'perl-smoke.pl',root/'LATEXMK-B31.md']
hashes={}
for path in files:
    relative=path.relative_to(root); target=snapshot/relative; target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target); hashes[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
(snapshot/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('Recorded signed B3.1 candidate; device acceptance remains pending.')
