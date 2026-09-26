"""Verify immutable delivery, release failure modes, and render regression PDFs."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from contextlib import nullcontext
import zipfile
import pymupdf
from PIL import Image, ImageOps, ImageDraw

root = pathlib.Path(__file__).resolve().parent.parent
out = root / 'validation/baseline'
report = {'checks': {}}
expected = {'TeXstudioHarmony-1.0.5-arm64-device-signed.hap': '5e52ac3a6a21dc2d95a6d51d159502e176664325e25160e2ddee1955d7778e99',
            'texlive-1.0.5.hnp': '2d4ad4b87610720dec435b6837092d6a4bc697ff9ce3ed879994d91ce1f2ce32'}
for name, sha in expected.items():
    actual = hashlib.file_digest((root / 'artifacts' / name).open('rb'), 'sha256').hexdigest()
    assert actual == sha, 'Baseline artifact changed: ' + name
    report['checks'][name] = actual

(out / 'release-test-copy').mkdir(exist_ok=True)
with nullcontext(out / 'release-test-copy') as tmp:
    repo = pathlib.Path(tmp)
    assert repo.resolve().is_relative_to(out.resolve())
    for relative in ('scripts/release_config.py', 'release.json', 'texstudio_harmony/AppScope/app.json5'):
        dest = repo / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / 'texstudio-harmony' / relative, dest)
    (repo / 'third_party/texstudio/src').mkdir(parents=True, exist_ok=True)
    data = json.loads((repo / 'release.json').read_text())
    data.update(version='1.0.6', versionCode=1000006)
    (repo / 'release.json').write_text(json.dumps(data))
    (repo / 'third_party/texstudio/src/harmonyRelease.h').write_text('// stale fixture\n')
    cmd = [sys.executable, str(repo / 'scripts/release_config.py')]
    assert subprocess.run(cmd, capture_output=True).returncode != 0
    subprocess.run(cmd + ['--write'], check=True, capture_output=True)
    subprocess.run(cmd, check=True, capture_output=True)
    assert '"1.0.6"' in (repo / 'third_party/texstudio/src/harmonyRelease.h').read_text()
    assert json.loads((repo / 'texstudio_harmony/AppScope/app.json5').read_text())['app']['versionCode'] == 1000006
    report['checks']['versionChangeAndStaleDetection'] = 'passed in temporary copy'
    shutil.copy2(root / 'texstudio-harmony/scripts/verify_archives.py', repo / 'scripts/verify_archives.py')
    archive = repo / 'build/src/test.tar.xz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(b'known archive fixture')
    (repo / 'dependencies.lock.json').write_text(json.dumps({'archives': {'build/src/test.tar.xz': {'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}}}))
    verify = [sys.executable, str(repo / 'scripts/verify_archives.py'), str(archive)]
    subprocess.run(verify, check=True, capture_output=True)
    archive.write_bytes(b'tampered archive fixture')
    assert subprocess.run(verify, capture_output=True).returncode != 0
    report['checks']['archiveTamperingRejected'] = True
env = os.environ.copy()
env['PACKAGE_VERSION'] = '1.0.0'
assert subprocess.run([sys.executable, str(root / 'build-support/release_config.py')], env=env, capture_output=True).returncode != 0
report['checks']['conflictingVersionRejected'] = True

pages = []
for name, relative in [('english', 'english/pdflatex-basic.pdf'), ('chinese', '中文 空格路径/xelatex-cjk.pdf'), ('mcm', 'mcm/mcmthesis-demo.pdf')]:
    doc = pymupdf.open(out / 'regression' / relative)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(0.6, 0.6), alpha=False)
        image = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        image.thumbnail((300, 410))
        tile = Image.new('RGB', (320, 445), 'white')
        tile.paste(image, ((320-image.width)//2, 25))
        ImageDraw.Draw(tile).text((10, 8), f'{name} {i+1}', fill='black')
        pages.append(tile)
    if name == 'chinese':
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4)).save(out / 'chinese-page.png')
sheet = Image.new('RGB', (320 * 4, 445 * ((len(pages)+3)//4)), '#cccccc')
for i, tile in enumerate(pages):
    sheet.paste(tile, ((i%4)*320, (i//4)*445))
sheet.save(out / 'regression-overview.png')
ppm = out / 'preview/cjk.ppm'
if ppm.exists():
    Image.open(ppm).save(out / 'preview/cjk.png')
report['checks']['renderedPages'] = len(pages)
report['passed'] = True
(out / 'windows-checks.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
