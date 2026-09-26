"""Require real device output, visual-review evidence, and cancellation proof."""
import hashlib, json, subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[1]
out = root / 'validation/luahbtex'
device = out / 'device'
cases = device / 'B3320'
assert 'successfully' in (device / 'install.log').read_text(encoding='utf-8-sig').lower()
assert (cases / 'completed.txt').read_text().strip() == 'passed'
assert '1.21.0' in (cases / 'engine-version.txt').read_text()
assert not (cases / 'biber-version.stderr').read_bytes()
assert 'Nothing to do' in (cases / 'repeat.log').read_text()
assert json.loads((device / 'cancel-result.json').read_text(encoding='utf-8'))['passed']
pdfs = {}
for name in ('main.pdf', 'harf.pdf', '中文 空格/主文献.pdf', 'app-lua.pdf', 'app-after-cancel.pdf'):
    path = cases / name
    text = subprocess.check_output(['pdftotext', str(path), '-']).decode('utf-8')
    if name == 'harf.pdf':
        assert 'HarfBuzz on HarmonyOS' in text and 'office' in text
    else:
        assert 'UPDATEDTITLE' in text and 'Lua execution passed' in text
        assert '取消后' in text if name == 'app-after-cancel.pdf' else '鸿蒙' in text
    fonts = subprocess.check_output(['pdffonts', str(path)]).decode('utf-8')
    (path.with_suffix('.fonts.txt')).write_text(fonts, encoding='utf-8')
    (path.with_suffix('.text.txt')).write_text(text, encoding='utf-8')
    rows = [r.split() for r in fonts.splitlines()[2:] if r.strip()]
    assert rows and all(row[-5] == 'yes' for row in rows), fonts
    pdfs[name] = {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'embeddedFonts': len(rows)}
    final_log = path.with_suffix('.log').read_text(encoding='utf-8', errors='replace')
    for message in ('undefined references', 'Missing character:', 'Fatal error', 'no writeable cache', 'No match for requested fontloader'):
        assert message not in final_log, (name, message)
review = json.loads((device / 'visual-review.json').read_text(encoding='utf-8'))
assert review['passed'] and set(review['pdfs']) == set(pdfs)
signing = json.loads((root / 'validation/device-signing-1.0.20/result.json').read_text())
assert signing['signature_verified'] and signing['original_payloads_identical']
report = {'version': '1.0.20', 'passed': True, 'installed': True, 'engine': 'LuaHBTeX 1.21.0', 'signedSha256': signing['sha256'], 'checks': ['public HiShell commands', 'default writable font cache', 'HarfBuzz shaping', 'Chinese and math', 'Biber bibliography', 'incremental no-op', 'bibliography update', 'Chinese and spaces in paths', 'app auto Lua build and PDF preview', 'cancel process group', 'new document build after cancellation'], 'pdfs': pdfs}
(out / 'device-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
