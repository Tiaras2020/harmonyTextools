"""Assemble a new candidate; never modify the frozen runtime or run upstream scripts."""
import argparse
import hashlib
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
from full_resources import digest, read_database, download

parser=argparse.ArgumentParser()
parser.add_argument('--baseline',type=Path,required=True)
parser.add_argument('--resources',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--report',type=Path,required=True)
parser.add_argument('--resume-maps',action='store_true')
args=parser.parse_args()
plan=json.loads((root/'validation/full-resources/plan.json').read_text())
assert plan['extraction']['status']=='complete', 'Extraction must finish first'
assert args.resume_maps or not args.output.exists(), 'Preserve previous candidates; choose a fresh output'
db=read_database(lzma.decompress((root/'validation/full-resources/texlive.tlpdb.xz').read_bytes()).decode())
if not args.resume_maps:
    shutil.copytree(args.baseline,args.output,symlinks=True,ignore=shutil.ignore_patterns('.tlpkg-cache'))
tree=args.output/'texmf'
report={'status':'incomplete','baseline':str(args.baseline),'candidate':str(args.output),'planSha256':digest(root/'validation/full-resources/plan.json'),'added':[],'identicalCollisions':[],'baselineFiles':{}}
try:
    for f in sorted((args.baseline/'texmf').rglob('*')):
        if f.is_file(): report['baselineFiles'][f.relative_to(args.baseline/'texmf').as_posix()]=digest(f)
    for f in sorted(args.resources.rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(args.resources)
        target=tree/rel
        if target.exists():
            if digest(target)!=digest(f): raise ValueError('Baseline collision: '+str(rel))
            if (args.baseline/'texmf'/rel).exists():
                report['identicalCollisions'].append(rel.as_posix())
            else:
                report['added'].append({'path':rel.as_posix(),'bytes':f.stat().st_size,'sha256':digest(f)})
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(f,target)
        report['added'].append({'path':rel.as_posix(),'bytes':f.stat().st_size,'sha256':digest(f)})
    # Generate with only package-declared maps that exist in this candidate.
    policy=json.loads((root/'texstudio-harmony/scripts/texlive/resource-policy.json').read_text())
    cache=args.output.parent/'full-resources-cache/archives'
    helpers=download('texlive-scripts',db['texlive-scripts'],cache,policy['repository'])
    helper_names=['dvips35.map','pdftex35.map','ps2pk35.map']
    report['mapBuildInputs']={'package':'texlive-scripts','archiveSha512':digest(helpers,'sha512'),'files':helper_names,'scriptsExecuted':False}
    with tarfile.open(helpers,'r:xz') as archive:
        for name in helper_names:
            member=archive.getmember('texmf-dist/fonts/map/dvips/tetex/'+name)
            assert member.isfile() and member.size<1024*1024
            dest=tree/'fonts/map/dvips/tetex'/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            payload=archive.extractfile(member).read()
            if dest.exists(): assert dest.read_bytes()==payload
            else: dest.write_bytes(payload)
    declarations=set()
    missing=[]
    available_maps={f.name for f in (tree/'fonts/map').rglob('*.map')}
    for name,record in plan['packages'].items():
        if record['status'] not in ('candidate','frozen'): continue
        for action in db[name]['execute']:
            fields=action.split()
            if len(fields)!=2 or fields[0] not in ('addMap','addMixedMap'): continue
            if fields[1] not in available_maps:
                missing.append({'package':name,'map':fields[1]}); continue
            declarations.add(fields[0][3:]+' '+fields[1])
    report['missingDeclaredMaps']=missing
    if missing: raise ValueError('Declared maps missing; inspect report')
    work=args.output/'map-build'
    work.mkdir(exist_ok=True)
    cfg=work/'updmap.cfg'
    cfg.write_text('dvipsPreferOutline true\nLW35 URWkb\ndvipsDownloadBase35 true\npdftexDownloadBase14 true\n'+ '\n'.join(sorted(declarations))+'\n')
    env=os.environ.copy()
    env.update(TEXMF=str(tree),TEXMFDIST=str(tree),TEXMFROOT=str(args.output),TEXMFHOME=str(work/'home'),TEXMFVAR=str(work/'var'),TEXMFCONFIG=str(work/'config'),TEXFONTMAPS=str(tree/'fonts/map')+'//')
    subprocess.run(['mktexlsr',str(tree)],check=True,capture_output=True)
    report['updmapVersion']=subprocess.check_output(['updmap','--version'],text=True).strip()
    proc=subprocess.run(['updmap','--user','--cnffile',str(cfg),'--outputdir',str(work/'output'),'--nohash','--copy','--force'],env=env,capture_output=True,text=True)
    (work/'updmap.log').write_text(proc.stdout+proc.stderr)
    report['updmapExitCode']=proc.returncode
    if proc.returncode: raise ValueError('updmap failed; inspect map-build/updmap.log')
    report['status']='assembled-maps-awaiting-review'
finally:
    args.report.write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],len(report['added']),'added files')
