"""Record source license declarations for CPAN metadata with unknown entries."""
import json,os,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);deps=repo/'build/biber-deps'
lock=json.loads((root/'validation/biber/dependencies.lock.json').read_text());records=[]
for r in lock['distributions']:
    if 'unknown' not in r['license']:continue
    evidence=[]
    for p in (deps/r['distribution']).rglob('*'):
        if not p.is_file() or p.suffix not in ('.pm','.pod','') or any(part in ('t','inc','examples') for part in p.relative_to(deps/r['distribution']).parts):continue
        text=p.read_text(errors='replace')
        for m in re.finditer(r'(?i)(?:same terms|(?:artistic|apache|gnu general public) licen[sc]e|(?:copyright|licen[sc]e)\s*\n)',text):
            evidence.append({'file':str(p.relative_to(deps/r['distribution'])),'excerpt':text[max(0,m.start()-100):m.end()+340]})
    assert any(re.search(r'same\s+terms',e['excerpt'],re.I) for e in evidence),r['distribution']
    records.append({'distribution':r['distribution'],'metadataLicense':r['license'],'resolvedLicense':'perl_5','sourceEvidence':evidence[:12]})
(root/'validation/biber/license-audit.json').write_text(json.dumps(records,indent=2)+'\n');print('Source license declarations recorded:',len(records))
