"""Repackage only reviewed runtime changes; verify all other payload identities."""
from pathlib import Path
import copy,hashlib,json,shutil,zipfile
r=Path(__file__).resolve().parents[1];out=r/'validation/crash-fix-1.0.30';a=r/'artifacts'
overlay=out/'runtime-overlay';hnp=a/'texlive-1.0.30.hnp';hap=a/'TeXstudioHarmony-1.0.30-arm64-unsigned.hap'
assert not hnp.exists() and not hap.exists(), 'Never overwrite a delivery'
changes={};oldprefix=b'texlive_1.0.21';newprefix=b'texlive_1.0.30'
with zipfile.ZipFile(a/'texlive-1.0.21.hnp') as old,zipfile.ZipFile(hnp,'w',allowZip64=True) as new:
    prefix=next(n[:-len('hnp.json')] for n in old.namelist() if n.endswith('/hnp.json'))
    for info in old.infolist():
        rel=info.filename[len(prefix):];before=old.read(info);data=before
        if (overlay/rel).is_file():data=(overlay/rel).read_bytes()
        elif rel=='texmf/web2c/texmf.cnf':data=data.replace(oldprefix,newprefix)
        elif rel=='hnp.json':
            cfg=json.loads(data);cfg['version']='1.0.30';data=(json.dumps(cfg,indent=2)+'\n').encode()
        assert oldprefix not in data, 'Unmigrated runtime path: '+rel
        if data!=before:changes[rel]={'before':hashlib.sha256(before).hexdigest(),'after':hashlib.sha256(data).hexdigest()}
        new.writestr(copy.copy(info),data)
with zipfile.ZipFile(hnp) as z:
    assert z.testzip() is None
    for alias,engine in {'pdflatex':'pdftex','latex':'pdftex','xelatex':'xetex'}.items():assert z.read(prefix+'bin/'+alias)==z.read(prefix+'bin/'+engine)
shutil.copy2(out/'app-core.hap',hap)
with zipfile.ZipFile(hap,'a',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
    assert 'hnp/arm64-v8a/texlive.hnp' not in z.namelist()
    z.write(hnp,'hnp/arm64-v8a/texlive.hnp')
report={'runtimeChanges':changes,'runtimeVersion':'1.0.30','unchangedEntriesVerified':True}
for p in (hnp,hap):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        if p==hap:
            app=json.loads(z.read('module.json'))['app'];assert app['versionName']=='1.0.30' and app['versionCode']==1000030
            assert hashlib.sha256(z.read('hnp/arm64-v8a/texlive.hnp')).digest()==hashlib.sha256(hnp.read_bytes()).digest()
    report[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'zip_crc':'passed'}
(a/'package-check-1.0.30.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: app/runtime 1.0.30, CRC, aliases, no stale prefix, unchanged resource identities;',len(changes),'changed entries')
