"""Check collected UI fixtures without modifying device or source files."""
import hashlib
import json
from pathlib import Path
import fitz

root = Path(__file__).resolve().parents[1]
out = root / 'validation/ui-polish-1.0.22'
device = out / 'device-final'
expected = json.loads((out / 'source-hashes.json').read_text(encoding='utf-8'))
sources = {}
for name, digest in expected.items():
    actual = hashlib.sha256((device / name).read_bytes()).hexdigest()
    assert actual == digest, f'Source/sentinel changed: {name}'
    sources[name] = actual

pdfs = {}
for name, pages in [('plain', 1), ('sync', 3), ('links', 2)]:
    with fitz.open(device / (name + '.pdf')) as pdf:
        assert len(pdf) == pages, name
        text = '\n'.join(page.get_text() for page in pdf)
        if name == 'plain':
            assert 'Stochastic Optimization' in text and '[3]' in text
            assert '[?]' not in text
        if name == 'links':
            assert 'END PAGE LINK TARGET' in text
            assert any(page.get_links() for page in pdf), 'Missing PDF link'
        pdfs[name] = {'pages': pages, 'bytes': (device / (name + '.pdf')).stat().st_size}
        (out / (name + '-extracted.txt')).write_text(text, encoding='utf-8')

fdb = (device / 'plain.fdb_latexmk').read_text(encoding='utf-8')
assert 'texlive_1.0.20/' not in fdb
assert 'texlive_1.0.21/' in fdb
assert fdb.splitlines()[1].endswith(' 0'), 'BibTeX failure remains recorded'
report = {'source_hashes_unchanged': sources, 'pdfs': pdfs,
          'old_failure_record_replaced': True,
          'scope': 'File checks supplement the separately recorded device UI tests.'}
(out / 'fixture-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('PASS: seven source/sentinel hashes, three PDFs, bibliography failure cache recovery')
