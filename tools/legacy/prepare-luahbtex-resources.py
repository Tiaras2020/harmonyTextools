"""Stage the explicitly reviewed Lua resource subset from the locked TL database."""
import json
import lzma
import os
from pathlib import Path
import sys
import tarfile
import hashlib

root = Path(os.environ['DELIVERY_ROOT'])
repo = Path(os.environ['BUILD_REPO'])
sys.path.insert(0, str(root / 'texstudio-harmony/scripts/texlive'))
from full_resources import digest, read_database, download, extract_package, relative, path_allowed

policy = json.loads((root / 'texstudio-harmony/scripts/texlive/resource-policy.json').read_text())
metadata = root / 'validation/full-resources/texlive.tlpdb.xz'
assert digest(metadata) == policy['metadataSha256']
db = read_database(lzma.decompress(metadata.read_bytes()).decode())
names = ['luaotfload', 'lua-alt-getopt', 'lua-uni-algos', 'lualibs', 'luatexbase', 'ctablestack', 'luatexja', 'chinese-jfm', 'ctex']
# This is a build-only allowlist for these pinned packages. The application's
# ZIP import policy and the unsupported collection-luatex policy stay unchanged.
prefixes = ['tex/luatex/' + name + '/' for name in names if name != 'lua-alt-getopt']
prefixes += ['scripts/luaotfload/', 'scripts/lua-alt-getopt/']
policy['allowedPrefixes'] += prefixes
policy.setdefault('reviewedResourceExtensions', {}).update({p: ['lua', 'cnf'] for p in prefixes})
policy['reviewedResourceExtensions']['tex/latex/ctex/dictionary/'] = ['dict']
stage = repo / 'build/luahbtex-resources'
stage.mkdir(exist_ok=True)
cache = root / 'validation/luahbtex/archives'
cache.mkdir(exist_ok=True)
out = root / 'validation/luahbtex'
out.mkdir(exist_ok=True)
report = {'metadataSha256': digest(metadata), 'packages': {}, 'status': 'staging'}
for name in names:
    p = db[name]
    invalid = [relative(f) for f in p['runfiles'] if not path_allowed(relative(f), policy)]
    if invalid:
        raise ValueError(f'{name}: review resource paths first: {invalid}')
    archive = download(name, p, cache, policy['repository'])
    package_stage = stage / name
    if not package_stage.exists():
        package_stage.mkdir()
        extract_package(archive, p, package_stage, policy)
    files = {f.relative_to(package_stage).as_posix(): digest(f) for f in package_stage.rglob('*') if f.is_file()}
    assert set(files) == {relative(f) for f in p['runfiles']}
    with tarfile.open(archive, 'r:xz') as tar:
        for member in tar:
            if not member.isfile() or member.name.startswith('tlpkg/'):
                continue
            rel = relative(member.name) or (member.name if p.get('relocated') == '1' else None)
            assert rel in files
            assert hashlib.sha256(tar.extractfile(member).read()).hexdigest() == files[rel], rel
    report['packages'][name] = {'revision': p['revision'], 'archiveSha512': digest(archive, 'sha512'), 'dependencies': p['depend'], 'files': files}
    print(name, len(files), flush=True)
report['status'] = 'staged-not-yet-runtime-validated'
(out / 'resources.json').write_text(json.dumps(report, indent=2) + '\n')
