"""Extend a copied 1.0.19 runtime; preserve all accepted engine binaries."""
import hashlib, json, os, shutil, subprocess
from pathlib import Path
repo = Path(os.environ['BUILD_REPO'])
root = Path(os.environ['DELIVERY_ROOT'])
out = root / 'validation/luahbtex'
candidate = repo / 'build/resource-release-1.0.20'
base = repo / 'build/resource-release-1.0.19'
assert not candidate.exists(), 'Preserve existing candidate; inspect before retrying'
proof = json.loads((out / 'qemu/result.json').read_text())
assert proof['passed']
engine = repo / 'build/luahbtex-ohos/texk/web2c/luahbtex'
assert hashlib.sha256(engine.read_bytes()).hexdigest() == proof['engineSha256']
perl = repo / 'build/biber-perl-1.0.20/stage/data/service/hnp/texlive.org/texlive_1.0.20'
assert (perl / 'bin/perl').is_file()
audit = json.loads((out / 'perl/assembled-dependency-audit.json').read_text())
assert audit['passed'] and audit['interpreterSha256'] == hashlib.sha256((perl / 'bin/perl').read_bytes()).hexdigest()
for name in ('workflow/result.json', 'runtime-data-result.json'):
    assert json.loads((out / 'perl' / name).read_text())['passed']
shutil.copytree(base, candidate, symlinks=True,
                ignore=lambda directory, names: ['perl5'] if Path(directory) == base / 'lib' else [])
cnf = candidate / 'texmf/web2c/texmf.cnf'
text = cnf.read_text().replace('texlive_1.0.19', 'texlive_1.0.20')
text += '''
% Lua engine resources and per-user writable caches.
TEXINPUTS.lualatex = .;$TEXMFDIST/tex/{plain,generic,latex,luatex}//
TEXINPUTS.luahbtex = .;$TEXMFDIST/tex/{plain,generic,latex,luatex}//
LUAINPUTS = .;$TEXMFDIST/{tex,scripts}//
TEXMFVAR.lualatex = $HOME/.texstudio/luahbtex-1.21
TEXMFVAR.luahbtex = $HOME/.texstudio/luahbtex-1.21
TEXMFCACHE = $TEXMFVAR
'''
cnf.write_text(text)
resources = json.loads((out / 'resources.json').read_text())
added = []
for name, package in resources['packages'].items():
    for rel, digest in package['files'].items():
        source = repo / 'build/luahbtex-resources' / name / rel
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
        dest = candidate / 'texmf' / rel
        if dest.exists():
            assert dest.read_bytes() == source.read_bytes(), 'Frozen resource collision: ' + rel
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            added.append(rel)
fmt = candidate / 'texmf/web2c/luahbtex/lualatex.fmt'
fmt.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(repo / 'build/luahbtex-test/lualatex.fmt', fmt)
tc = Path(os.environ['NATIVE_OHOS_SDK']) / 'llvm/bin'
for name in ('luahbtex', 'lualatex'):
    # Baseline lualatex is a legacy symlink. Never write through it to its target.
    if (candidate / 'bin' / name).is_symlink():
        (candidate / 'bin' / name).unlink()
    shutil.copy2(engine, candidate / 'bin' / name)
    subprocess.run([str(tc / 'llvm-strip'), str(candidate / 'bin' / name)], check=True)
shutil.copy2(perl / 'bin/perl', candidate / 'bin/perl')
shutil.copytree(perl / 'lib/perl5', candidate / 'lib/perl5')
for name in ('latexmk', 'biber'):
    subprocess.run([str(tc / 'clang'), '--target=aarch64-linux-ohos', '--sysroot=' + os.environ['NATIVE_OHOS_SDK'] + '/sysroot', '-O2', '-Wall', '-Wextra', '-Werror', '-DHARMONY_RUNTIME_ROOT="/data/service/hnp/texlive.org/texlive_1.0.20"', str(root / ('texstudio-harmony/scripts/texlive/' + name + '_launcher.c')), '-o', str(candidate / 'bin' / name)], check=True)
for name in ('perl', 'latexmk', 'biber'):
    subprocess.run([str(tc / 'llvm-strip'), str(candidate / 'bin' / name)], check=True)
licenses = candidate / 'share/licenses/luahbtex'
licenses.mkdir(parents=True)
source = repo / 'build/src/texlive-source'
for rel in ('COPYING', 'texk/web2c/luatexdir/COPYING'):
    path = source / rel
    if path.is_file(): shutil.copy2(path, licenses / (path.parent.name + '-COPYING'))
shutil.copy2(out / 'resources.json', licenses / 'resources.json')
report = {'version': '1.0.20', 'baseline': str(base), 'candidate': str(candidate), 'addedResources': added, 'deviceValidated': False}
(out / 'staging.json').write_text(json.dumps(report, indent=2) + '\n')
print('Lua candidate staged with', len(added), 'additional resource files')
