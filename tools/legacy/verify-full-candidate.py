"""Record provenance and ensure candidate assembly preserved frozen resources."""
import hashlib
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'texstudio-harmony/scripts/texlive'))
from full_resources import digest

out=root/'validation/full-resources'
assembly=json.loads((out/'assembly-v1.json').read_text())
candidate=Path(assembly['candidate'])
baseline=Path(assembly['baseline'])
changed=[]
for rel,expected in assembly['baselineFiles'].items():
    assert digest(baseline/'texmf'/rel)==expected, 'Frozen baseline changed: '+rel
    if digest(candidate/'texmf'/rel)!=expected:
        assert rel=='ls-R' or (rel.startswith('fonts/map/') and Path(rel).name in ('pdftex.map','psfonts.map')), 'Unexpected baseline override: '+rel
        changed.append(rel)
native={}
for part in ('bin','lib'):
    for f in sorted((baseline/part).rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(baseline)
        original=digest(f)
        assert digest(candidate/rel)==original, 'Native runtime changed: '+str(rel)
        native[rel.as_posix()]=original
for item in assembly['added']:
    assert digest(candidate/'texmf'/item['path'])==item['sha256'], 'Added resource changed: '+item['path']
regression=json.loads((out/'regression/result.json').read_text())
assert regression['passed'] and len(regression['cases'])==5, 'Five host regression cases required'
maps=json.loads((out/'maps-reviewed.json').read_text())
assert maps['passed']
(out/'font-adaptations.json').write_bytes((candidate/'font-adaptations.json').read_bytes())
source={}
paths=list((root/'texstudio-harmony/scripts/texlive').glob('full_resources.py'))+[root/'texstudio-harmony/scripts/texlive/resource-policy.json']
paths += [root/'build-support'/n for n in ('plan-full-resources.sh','assemble-full-resources.py','audit-full-maps.py','adapt-full-fonts.py','regress-full-resources.sh','regress-baseline.py','verify-full-candidate.py')]
paths += [out/'test_full_resources.py']+list((out/'fixtures').glob('*.tex'))
for f in paths: source[f.relative_to(root).as_posix()]=digest(f)
report={'stage':'B2.2 initial conservative candidate','hostValidated':True,'deviceValidated':False,'releaseVersionUnchanged':'1.0.11','candidate':str(candidate),'frozenBaselineUnchanged':True,'nativeFiles':native,'expectedGeneratedChanges':changed,'addedResourceFiles':len(assembly['added']),'fontMapExcludedEntries':len(maps['maps']['pdftex.map']['missing']),'sourceSha256':source,'limitations':['Pending packages are not included; scheme-full coverage is incomplete','Excluded font entries remain unsupported','Candidate is not a signed HNP/HAP and not an additive-v1 import ZIP','B2.3 packaging and device/HiShell acceptance remain required']}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print('Candidate provenance and five host regressions verified; device validation pending.')
