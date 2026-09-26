"""Preserve source fixes; deliberately exclude signing and machine profile files."""
import hashlib
import json
import pathlib
import subprocess
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
out = root / 'validation/baseline/source'
out.mkdir(parents=True, exist_ok=True)
manifest = {}
for label, relative, paths in (
    ('main', 'texstudio-harmony', ['scripts', 'third_party/lycium', 'texstudio_harmony/AppScope/app.json5', 'release.json', 'dependencies.lock.json']),
    ('texstudio', 'texstudio-harmony/third_party/texstudio', ['src']),
):
    repo = root / relative
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    diff = subprocess.check_output(['git', '-C', str(repo), 'diff', '--binary', 'HEAD', '--', *paths])
    (out / (label + '.patch')).write_bytes(diff)
    names = subprocess.check_output(['git', '-C', str(repo), 'diff', '--name-only', 'HEAD', '--', *paths], text=True).splitlines()
    names += subprocess.check_output(['git', '-C', str(repo), 'ls-files', '--others', '--exclude-standard', '--', *paths], text=True).splitlines()
    files = {}
    with zipfile.ZipFile(out / (label + '-changed-files.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(set(names)):
            p = repo / name
            if '__pycache__' in p.parts or p.suffix == '.pyc':
                continue
            if p.is_file():
                z.write(p, name)
                files[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest[label] = {'head': head, 'files': files, 'patchSha256': hashlib.sha256(diff).hexdigest()}
manifest['excluded'] = ['DevEco signing/build-profile files', 'credentials', 'generated binaries']
support = {}
with zipfile.ZipFile(out / 'build-support.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((root / 'build-support').iterdir()):
        if p.is_file() and p.suffix in ('.py', '.sh'):
            z.write(p, p.name)
            support[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
manifest['buildSupport'] = support
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print('Source snapshots saved; signing profiles excluded')
