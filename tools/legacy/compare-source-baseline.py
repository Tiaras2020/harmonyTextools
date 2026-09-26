"""Record both source copies without overwriting machine-local differences."""
import hashlib
import json
import os
import pathlib
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
repo = pathlib.Path(os.environ.get('BUILD_REPO', '/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915'))
out = root / 'validation/baseline/source'
manifest = json.loads((out / 'manifest.json').read_text())
report = []
with zipfile.ZipFile(out / 'wsl-different-files.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for group, prefix in [('main', pathlib.Path('.')), ('texstudio', pathlib.Path('third_party/texstudio'))]:
        for name, expected in manifest[group]['files'].items():
            relative = prefix / name
            path = repo / relative
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            if actual != expected:
                report.append({'path': relative.as_posix(), 'windows': expected, 'wsl': actual})
                if path.is_file():
                    z.write(path, relative.as_posix())
(out / 'copy-differences.json').write_text(json.dumps(report, indent=2) + '\n')
print('Windows/WSL source differences:', len(report))
for item in report:
    print(item['path'])
