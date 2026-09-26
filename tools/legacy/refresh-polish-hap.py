"""Assemble the final 1.0.17 app with its unchanged HNP before signing."""
import hashlib,json,pathlib,shutil,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'validation/latexmk/repack-1.0.17'; version='1.0.17'
art=root/'artifacts'; hap=art/f'TeXstudioHarmony-{version}-arm64-unsigned.hap'; hnp=art/f'texlive-{version}.hnp'
assert not (art/f'TeXstudioHarmony-{version}-arm64-device-signed.hap').exists()
reportpath=art/f'package-check-{version}.json'
report=json.loads(reportpath.read_text(encoding='utf-8'))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(hap)==report[hap.name]['sha256']
assert digest(hnp)==report[hnp.name]['sha256']
candidate=out/'final.hap'; assert not candidate.exists()
shutil.copy2(out/'base.hap',candidate)
with zipfile.ZipFile(candidate,'a',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
    assert 'hnp/arm64-v8a/texlive.hnp' not in z.namelist()
    assert json.loads(z.read('module.json'))['app']['versionName']==version
    z.write(hnp,'hnp/arm64-v8a/texlive.hnp')
with zipfile.ZipFile(candidate) as z:
    assert z.testzip() is None
    assert hashlib.sha256(z.read('hnp/arm64-v8a/texlive.hnp')).hexdigest()==report[hnp.name]['sha256']
    entries=len(z.namelist())
    assert entries==len(set(z.namelist()))
previous=out/'before-command-chain-fix.hap'
assert not previous.exists()
for path in (hap,candidate,previous):path.resolve().relative_to(root.resolve())
shutil.copy2(reportpath,out/'before-package-check.json')
hap.rename(previous);candidate.rename(hap)
report[hap.name]={'bytes':hap.stat().st_size,'sha256':digest(hap),'entries':entries,'zip_crc':'passed'}
report['polishFinalAppRefresh']={'appRebuilt':True,'hnpUnchanged':True,'previousUnsignedArchived':previous.relative_to(root).as_posix()}
reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(art/f'SHA256SUMS-{version}.txt').write_text('\n'.join(report[p.name]['sha256']+'  '+p.name for p in (hap,hnp))+'\n')
print(json.dumps(report[hap.name],indent=2))
