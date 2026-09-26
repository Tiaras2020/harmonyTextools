"""B2.4 incremental reviewed resources, preserving the previous full candidate."""
import json
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'texstudio-harmony/scripts/texlive'))
from full_resources import digest, read_database, plan, download, extract_package
out=root/'validation/common-resources'
old=read=lambda p:json.loads(p.read_text())
previous=old(root/'validation/full-resources/result.json')
base=Path(previous['candidate']); candidate=base.with_name('full-runtime-v2')
policy=old(out/'policy.json'); metadata=root/'validation/full-resources/texlive.tlpdb.xz'
assert digest(metadata)==policy['metadataSha256']
db=read_database(lzma.decompress(metadata.read_bytes()).decode())
old_plan=old(root/'validation/full-resources/plan.json')
pinned={n for n,p in old_plan['packages'].items() if p['status'] in ('candidate','frozen')}
report=plan(db,policy,pinned)
assert set(report['selected'])=={'beamer','pgfplots','newpx','translator'},report['selected']
assert not candidate.exists(), 'Preserve earlier build; candidate already exists'
required=shutil.disk_usage(base).free
assert required>8*1024**3, 'Need 8 GiB available staging space'
cache=base.parent/'full-resources-cache/archives'
archives={name:download(name,db[name],cache,policy['repository']) for name in report['selected']}
shutil.copytree(base,candidate,symlinks=True,ignore=shutil.ignore_patterns('map-build'))
stage=candidate/'reviewed-additions'; stage.mkdir()
report.update(candidate=str(candidate),previousCandidate=str(base),added=[],helpers=[],status='incomplete')
try:
    for name,path in archives.items():
        size,count=extract_package(path,db[name],stage,policy)
        report['packages'][name]['extractedFiles']=count
    # These are encoding tables, not support for the packages' external tools.
    helper_files={'cs':['fonts/enc/dvips/cs/xl2.enc','fonts/enc/dvips/cs/xt2.enc'],
                  'metapost':['fonts/enc/dvips/metapost/groff.enc'],
                  'ttfutils':['fonts/enc/ttf2pk/base/T1-WGL4.enc']}
    for name,names in helper_files.items():
        archive=download(name,db[name],cache,policy['repository'])
        with tarfile.open(archive,'r:xz') as tar:
            for rel in names:
                metadata_name=('RELOC/' if db[name].get('relocated')=='1' else 'texmf-dist/')+rel
                assert metadata_name in db[name]['runfiles']
                member=tar.getmember(rel if db[name].get('relocated')=='1' else metadata_name)
                assert member.isfile() and member.size<1024*1024
                target=stage/rel; target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
                report['helpers'].append({'package':name,'revision':db[name]['revision'],'path':rel,'archiveSha512':digest(archive,'sha512'),'scope':'encoding table only, no external tool support'})
    for f in sorted(stage.rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(stage); target=candidate/'texmf'/rel
        if target.exists(): assert digest(target)==digest(f),'Collision: '+str(rel)
        else:
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,target)
        report['added'].append({'path':rel.as_posix(),'sha256':digest(f),'bytes':f.stat().st_size})
    work=candidate/'map-build'; work.mkdir()
    config=(base/'map-build/updmap.cfg').read_text()
    assert 'Map newpx.map\n' not in config
    (work/'updmap.cfg').write_text(config+'Map newpx.map\n')
    tree=candidate/'texmf'
    env=os.environ.copy()
    env.update(TEXMF=str(tree),TEXMFDIST=str(tree),TEXMFROOT=str(candidate),TEXMFHOME=str(work/'home'),TEXMFVAR=str(work/'var'),TEXMFCONFIG=str(work/'config'),TEXFONTMAPS=str(tree/'fonts/map')+'//')
    subprocess.run(['mktexlsr',str(tree)],check=True,capture_output=True)
    proc=subprocess.run(['updmap','--user','--cnffile',str(work/'updmap.cfg'),'--outputdir',str(work/'output'),'--nohash','--copy','--force'],env=env,capture_output=True,text=True)
    (work/'updmap.log').write_text(proc.stdout+proc.stderr)
    assert proc.returncode==0,'updmap failed'
    report['status']='assembled-awaiting-audit'
finally:
    (out/'assembly.json').write_text(json.dumps(report,indent=2)+'\n')
print('Reviewed additions:',len(report['added']),flush=True)
