"""Audit collected real-device outputs; never runs host TeX."""
from pathlib import Path
import hashlib, json, re
import fitz
root = Path(__file__).resolve().parents[1]
base = root/'validation/compat-fix-1.0.21'
hs = base/'device/hishell/Fix21'
assert (hs/'completed.txt').read_text().strip() == 'passed'
assert len((hs/'results.tsv').read_text().splitlines()) == 7
assert (hs/'biber-version.stderr').stat().st_size == 0
assert (hs/'resource-paths.txt').read_text().count('texlive_1.0.21') == 4
pdfs = [hs/(s+'.pdf') for s in ('plain','abbrv','unsrt','alpha')]
pdfs += [hs/d/'font.pdf' for d in ('cwd-one','cwd-two')]
pdfs += [hs/'lua-regression/main.pdf', base/'device/app/CompatReview/02-bibplain.pdf']
pdfs += [root/'validation/luatex-cn/app-1.0.21/LuaTeXCn/04-guji-spread.pdf']
pdfs += [base/'device/app/05-font-family.pdf']
out = {}
for path in pdfs:
    log = path.with_suffix('.log').read_text(encoding='utf-8', errors='replace')
    assert 'Output written on' in log, path
    assert not re.search(r'^!|There were undefined references', log, re.M), path
    missing = re.findall(r'Missing character:.*', log)
    assert not missing or path.stem == 'alpha', path
    with fitz.open(path) as doc:
        txt = ''.join(p.get_text() for p in doc)
        assert '[?]' not in txt, path
        if path.stem in ('plain','abbrv','unsrt','alpha','02-bibplain'):
            assert path.with_suffix('.bbl').read_bytes().count(b'\\bibitem') == 3
        out[str(path.relative_to(root))] = {'pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'text':txt,'missingGlyphWarnings':missing,'visualStatus':'Chinese alpha labels fail' if missing else 'no missing glyph warnings'}
        review = base/'pdf-review'
        review.mkdir(exist_ok=True)
        if path.stem in ('font','plain','main'):
            doc[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(review/(path.parent.name+'-'+path.stem+'.png'))
result = {'version':'1.0.21','date':'2026-09-25','device':'6UZ0226107000081','installed':True,
          'hishellChecks':(hs/'results.tsv').read_text().splitlines(),
          'appBibtex':'passed after removing stale failure fdb_latexmk',
          'luatexCnApp':'04-guji-spread passed compilation and preview', 'pdfs':out,
          'knownLimitation':'alpha.bst Chinese author labels are corrupt; compile success is not visual acceptance',
          'scope':'Specific fixtures only; no full compatibility claim; cancellation not repeated'}
(base/'device-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(pdfs),'real-device PDFs and seven HiShell checks')
