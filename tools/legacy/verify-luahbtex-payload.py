"""Verify old runtime preservation and inventory the new Lua payload."""
import hashlib, json, os, subprocess
from pathlib import Path
repo = Path(os.environ['BUILD_REPO'])
root = Path(os.environ['DELIVERY_ROOT'])
out = root / 'validation/luahbtex'
base = repo / 'build/resource-release-1.0.19'
candidate = repo / 'build/resource-release-1.0.20'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
allowed = {'bin/perl', 'bin/latexmk', 'bin/biber', 'bin/lualatex', 'texmf/web2c/texmf.cnf', 'texmf/ls-R'}
unchanged = 0
changed = []
for path in base.rglob('*'):
    if not path.is_file(): continue
    rel = path.relative_to(base).as_posix()
    dest = candidate / rel
    assert dest.is_file(), 'Missing baseline file: ' + rel
    if rel.startswith('lib/perl5/'):
        continue  # separately rebuilt and regression-tested for its new prefix
    if digest(path) == digest(dest):
        unchanged += 1
    else:
        assert rel in allowed, 'Unexpected baseline change: ' + rel
        changed.append(rel)
engine = candidate / 'bin/luahbtex'
assert digest(engine) == digest(candidate / 'bin/lualatex')
tc = Path(os.environ['NATIVE_OHOS_SDK']) / 'llvm/bin'
elf = subprocess.check_output([str(tc / 'llvm-readelf'), '-h', '-l', '-d', str(engine)], text=True)
assert 'AArch64' in elf and '/lib/ld-musl-aarch64.so.1' in elf and '$ORIGIN/../lib' in elf
(out / 'release-elf.txt').write_text(elf)
proof = json.loads((out / 'resources.json').read_text())
for package in proof['packages'].values():
    for rel, sha in package['files'].items():
        assert digest(candidate / 'texmf' / rel) == sha, rel
report = {'passed': True, 'unchangedBaselineFilesOutsideRebuiltPerl': unchanged, 'allowedChangedFiles': changed, 'engineSha256': digest(engine), 'formatSha256': digest(candidate / 'texmf/web2c/luahbtex/lualatex.fmt'), 'resourcePackages': len(proof['packages']), 'newResources': len(json.loads((out / 'staging.json').read_text())['addedResources'])}
(out / 'payload-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
