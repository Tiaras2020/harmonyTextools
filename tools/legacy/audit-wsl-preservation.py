"""Read-only source comparison for retirement planning; no secret contents emitted."""
import hashlib, json, os, subprocess
from pathlib import Path
root = Path('/mnt/e/CodeProjects/harmonytexlive')
win = root / 'texstudio-harmony'
repo = Path('/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915')
out = root / 'validation/storage-audit-2026-09-25'
windows_hashes = json.loads((out / 'windows-source-hashes.json').read_text())
paths = set(windows_hashes)
excluded = {'.git','build','node_modules','oh_modules','.hvigor','.cxx','__pycache__','libs','dependencies'}
for base, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if d not in excluded and not (Path(base)/d).is_symlink()]
    for name in files:
        p = Path(base)/name
        if p.suffix not in {'.hap','.hnp','.pyc','.dmp'}:
            paths.add(p.relative_to(repo).as_posix())
def digest(p):
    if p.is_symlink(): return 'symlink:' + os.readlink(p)
    if not p.is_file(): return None
    return hashlib.sha256(p.read_bytes()).hexdigest()
differences, same, errors = [], 0, []
for name in sorted(paths):
    try:
        a,b = windows_hashes.get(name),digest(repo/name)
        if a == b: same += 1
        else: differences.append({'path':name,'windows':a,'wsl':b,'wslBytes':(repo/name).lstat().st_size if (repo/name).exists() else 0})
    except OSError as e: errors.append({'path':name,'error':str(e)})
report={'windows':str(win),'wsl':str(repo),'same':same,'differences':differences,'errors':errors,'excludedDirectories':sorted(excluded),'note':'Hash differences can include line endings or machine configuration; do not blindly sync. Excluded build/src and git-only source trees must be preserved separately.'}
(out/'source-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print('Identical:',same,'Different or one-sided:',len(differences),'Errors:',len(errors))
for x in differences:
    if x['wsl'] is not None: print(x['path'])
subprocess.run(['du','-x','-B1','--max-depth=1',str(repo/'build')],stdout=(out/'wsl-build-bytes.tsv').open('w'),check=True)
