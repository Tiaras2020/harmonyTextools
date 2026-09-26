"""Prove B3.1 adds only its recorded payload to the B2.4 runtime."""
import hashlib,json,os,pathlib
from release_config import release
root=pathlib.Path(os.environ['DELIVERY_ROOT']); repo=pathlib.Path(os.environ['BUILD_REPO'])
version=release()['version'];assert version in ('1.0.17','1.0.18','1.0.19')
baseline=repo/'build/full-runtime-v2'; candidate=repo/'build'/('resource-release-'+version)
payload=json.loads((root/('validation/biber/payload-'+version+'.json' if version in ('1.0.18','1.0.19') else 'validation/latexmk/payload.json')).read_text())['files']
old={p.relative_to(baseline).as_posix():p for base in ('bin','lib','share','texmf') for p in (baseline/base).rglob('*') if p.is_file()}
new={p.relative_to(candidate).as_posix():p for base in ('bin','lib','share','texmf') for p in (candidate/base).rglob('*') if p.is_file()}
assert set(old)<=set(new)
assert set(new)-set(old)==set(payload),'Unrecorded new payload'
import importlib.util
spec=importlib.util.spec_from_file_location('polish_config',root/'build-support/polish-runtime-config.py');config=importlib.util.module_from_spec(spec);spec.loader.exec_module(config)
count=0
for name,path in old.items():
    if name=='texmf/web2c/texmf.cnf':
        expected=path.read_text().replace('texlive_1.0.5','texlive_'+version)
        assert new[name].read_text()==(config.texmf_config(expected) if version=='1.0.19' else expected)
    elif version=='1.0.19' and name=='texmf/dvipdfmx/dvipdfmx.cfg':
        assert new[name].read_text()==config.driver_config(path.read_text())
    elif name=='texmf/ls-R': continue
    else:
        assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(new[name].read_bytes()).digest(),name
        count+=1
for name,record in payload.items(): assert hashlib.sha256(new[name].read_bytes()).hexdigest()==record['sha256'],name
report={'passed':True,'unchangedBaselineFiles':count,'newPayloadFiles':len(payload),'allowedChanges':['texmf.cnf installation version','regenerated ls-R']}
if version=='1.0.19':report['allowedChanges']+=['dvipdfmx config/map lookup paths','disable absent kanjix.map default']
(root/('validation/biber/payload-check-'+version+'.json' if version in ('1.0.18','1.0.19') else 'validation/latexmk/payload-check.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
