"""Prove the reviewed candidate preserves native code and the previous resource tree."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root/'validation/common-resources'
read = lambda p: json.loads(p.read_text())
assembly = read(out/'assembly.json')
prior = read(root/'validation/full-resources/result.json')
candidate = Path(assembly['candidate'])
base = Path(assembly['previousCandidate'])
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for b in iter(lambda:stream.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
assert read(out/'regression/result.json')['passed']
assert read(out/'maps-reviewed.json')['passed']
assert read(out/'profile-tests.json')['passed']
for name, expected in prior['nativeFiles'].items():
    assert sha(candidate/name) == expected, name
changed = []
count = 0
for p in (base/'texmf').rglob('*'):
    if not p.is_file(): continue
    rel = p.relative_to(base)
    assert (candidate/rel).is_file(), str(rel)
    if sha(p) != sha(candidate/rel): changed.append(rel.as_posix())
    count += 1
assert set(changed) == {'texmf/ls-R','texmf/fonts/map/pdftex/updmap/pdftex.map','texmf/fonts/map/dvips/updmap/psfonts.map'}, changed
for item in assembly['added']:
    assert sha(candidate/'texmf'/item['path']) == item['sha256'], item['path']
report = {'stage':'B2.4','candidate':str(candidate),'hostValidated':True,'deviceValidated':False,
          'frozenBaselineUnchanged':True,'nativeFiles':prior['nativeFiles'],
          'previousResourceFilesCompared':count,'expectedGeneratedChanges':changed,
          'reviewedPackages':assembly['selected'],'addedFiles':len(assembly['added']),
          'unsupportedFontEntries':len(read(out/'maps-reviewed.json')['maps']['pdftex.map']['missing'])}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print('Verified preserved native files and',count,'existing resource files; additions:',len(assembly['added']))
