from pathlib import Path
import hashlib,json,shutil,zipfile,sys
r=Path(__file__).resolve().parents[1]; out=r/'validation/network-1.0.31'
hap=r/'artifacts/TeXstudioHarmony-1.0.31-arm64-unsigned.hap'; hnp=r/'artifacts/texlive-1.0.30.hnp'
if '--verify' not in sys.argv:
    assert not hap.exists(), 'Preserve previous candidates before rebuilding'
    shutil.copy2(out/'app-core.hap',hap)
    with zipfile.ZipFile(hap,'a',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
        assert 'hnp/arm64-v8a/texlive.hnp' not in z.namelist()
        z.write(hnp,'hnp/arm64-v8a/texlive.hnp')
with zipfile.ZipFile(hap) as z:
    assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
    app=json.loads(z.read('module.json'))['app']; assert app['versionName']=='1.0.31'
    assert hashlib.sha256(z.read('hnp/arm64-v8a/texlive.hnp')).digest()==hashlib.sha256(hnp.read_bytes()).digest()
    assert b'OpenSSL 3.' in z.read('libs/arm64-v8a/libQt5Network.so')
report={'version':'1.0.31','runtimeVersion':'1.0.30','zipCRC':'passed','unchangedRuntime':True,'sha256':hashlib.sha256(hap.read_bytes()).hexdigest()}
(r/'artifacts/package-check-1.0.31.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
