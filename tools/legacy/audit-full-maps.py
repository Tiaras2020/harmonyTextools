"""Check generated map references before installing them into a candidate."""
import argparse
import json
from pathlib import Path
import re
import shutil

p=argparse.ArgumentParser()
p.add_argument('runtime',type=Path)
p.add_argument('--report',type=Path,required=True)
p.add_argument('--quarantine-unavailable',action='store_true',help='Omit and report unavailable font entries; do not claim these fonts supported')
args=p.parse_args()
tree=args.runtime/'texmf'
available={f.name for f in tree.rglob('*') if f.is_file()}
folded={}
for name in available: folded.setdefault(name.lower(),[]).append(name)
result={'passed':True,'maps':{}}
for name in ('pdftex.map','psfonts.map'):
    src=args.runtime/'map-build/output'/name
    missing=[]
    synthetic=[]
    rows=0
    retained=[]
    corrections=[]
    for number,line in enumerate(src.read_text(errors='replace').splitlines(),1):
        if not line.strip() or line.lstrip().startswith(('%','#')):
            retained.append(line); continue
        rows+=1
        refs=re.findall(r'<+[\[]?([^\s<>\[\]"]+)',line)
        for f in refs:
            if f not in available and len(folded.get(f.lower(),[]))==1:
                corrected=folded[f.lower()][0]
                line=re.sub(r'(?<=[<\[])'+re.escape(f)+r'(?=\s|$)',corrected,line)
                corrections.append({'line':number,'from':f,'to':corrected})
        refs=re.findall(r'<+[\[]?([^\s<>\[\]"]+)',line)
        absent=[f for f in refs if f not in available]
        if absent: missing.append({'line':number,'font':line.split()[0],'missing':absent})
        invalid_synthetic=name=='pdftex.map' and ('SlantFont' in line or 'ExtendFont' in line) and not any(f.lower().endswith(('.pfb','.pfa')) for f in refs)
        if invalid_synthetic:
            synthetic.append({'line':number,'font':line.split()[0]})
        if not absent and not invalid_synthetic: retained.append(line)
    result['maps'][name]={'rows':rows,'missing':missing,'syntheticWithoutType1':synthetic,'caseCorrections':corrections,'quarantined':bool(args.quarantine_unavailable and (missing or synthetic))}
    if (missing or synthetic) and not args.quarantine_unavailable: result['passed']=False
    (args.runtime/'map-build/output'/(name+'.audited')).write_text('\n'.join(retained)+'\n')
args.report.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:{'rows':r['rows'],'missing':len(r['missing']),'syntheticWithoutType1':len(r['syntheticWithoutType1'])} for n,r in result['maps'].items()},indent=2))
if not result['passed']: raise SystemExit(1)
for name,subdir in [('pdftex.map','pdftex'),('psfonts.map','dvips')]:
    # Remove ambiguity with the baseline's previous generated map location.
    targets=list((tree/'fonts/map').rglob(name))
    if not targets:
        target=tree/'fonts/map'/subdir/'harmony'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        targets=[target]
    for target in targets: shutil.copy2(args.runtime/'map-build/output'/(name+'.audited'),target)
