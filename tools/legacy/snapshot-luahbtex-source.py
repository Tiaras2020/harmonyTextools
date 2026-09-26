"""Record the reviewed Lua port sources without signing material."""
import hashlib, json, os, shutil
from pathlib import Path
root = Path(os.environ['DELIVERY_ROOT'])
repo = Path(os.environ['BUILD_REPO'])
out = root / 'validation/luahbtex/source-1.0.20'
out.mkdir(exist_ok=True)
sync = max((root / 'validation/baseline/sync').glob('report-*.json'), key=lambda p: p.name)
paths = [Path('texstudio-harmony') / item['path'] for item in json.loads(sync.read_text())]
paths += [p.relative_to(root) for p in (root / 'build-support').glob('*luahbtex*') if p.is_file()]
paths += [Path('build-support') / n for n in ('prepare-lua-release-perl.py', 'test-lua-release-biber.sh', 'package-resource-release.sh', 'finalize-packages.py', 'sync-baseline.py')]
paths += [Path(n) for n in ('LUAHBTEX-B33.md', 'START-HERE.md')]
for rel in paths:
    source = root / rel
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
for source, name in ((repo / 'build/src/texlive-source/texk/web2c/luatexdir/tex/texfileio.c', 'engine/texfileio.c'),
                     (repo / 'build/luahbtex-ohos/build.sh', 'engine/build.sh'),
                     (repo / 'build/resource-release-1.0.20/texmf/web2c/texmf.cnf', 'runtime/texmf.cnf')):
    dest = out / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
(out / 'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(out).as_posix() + '\n' for p in files))
print('Source snapshot:', len(files), 'files')
