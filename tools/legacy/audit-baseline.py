"""WSL: freeze or verify the actual baseline, without rebuilding or downloading."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('--verify', action='store_true')
args = parser.parse_args()
repo = pathlib.Path(os.environ['BUILD_REPO'])
delivery = pathlib.Path(os.environ['DELIVERY_ROOT'])
out = delivery / 'validation/baseline'
out.mkdir(parents=True, exist_ok=True)
lock_path = delivery / 'texstudio-harmony/dependencies.lock.json'
dist = repo / 'build/build-texlive-ohos-dist'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def records(paths, root):
    return {str(p.relative_to(root)): {'sha256': digest(p), 'bytes': p.stat().st_size}
            for p in sorted(set(paths)) if p.is_file()}


if args.verify:
    lock = json.loads(lock_path.read_text())
    failures = []
    for group in ('archives', 'runtime', 'buildConfiguration', 'engineSources'):
        for name, expected in lock[group].items():
            p = repo / name
            if not p.is_file() or digest(p) != expected['sha256']:
                failures.append(name)
    runtime_now = {str(p.relative_to(repo)) for folder in ('bin', 'lib', 'share', 'texmf')
                   for p in (dist / folder).rglob('*') if p.is_file()}
    failures.extend(sorted(runtime_now - set(lock['runtime'])))
    (out / 'lock-verification.json').write_text(json.dumps({'passed': not failures, 'failures': failures}, indent=2) + '\n')
    print('Dependency lock verification:', 'PASS' if not failures else 'FAIL', len(failures))
    raise SystemExit(bool(failures))

if lock_path.exists():
    raise SystemExit('Lock already exists; review changes explicitly before replacing it')
archives = list((dist / '.tlpkg-cache').glob('*.tar.xz')) + list((repo / 'build/src').glob('*.tar.xz'))
runtime = [p for folder in ('bin', 'lib', 'share', 'texmf') for p in (dist / folder).rglob('*') if p.is_file()]
configs = list((repo / 'build/build-texlive-host').rglob('config.status')) + list((repo / 'build/build-texlive-ohos').rglob('config.status'))
sources = list((repo / 'build/src/texlive-source/texk/web2c').glob('texmfmp.*'))
lock = {'schema': 1, 'compatibilityId': 'tl2025-harmony-baseline-1.0.5',
        'scope': 'Observed working tree, not an upstream pristine release; hashes freeze local payloads, not independent source authentication.',
        'archives': records(archives, repo), 'runtime': records(runtime, repo),
        'buildConfiguration': records(configs, repo), 'engineSources': records(sources, repo)}
lock_path.write_text(json.dumps(lock, indent=2) + '\n')
audit = {'archiveCount': len(archives), 'runtimeFileCount': len(runtime), 'engines': {}, 'configure': {}, 'packages': {}, 'kernelFiles': {}}
for name in ('pdftex', 'xetex', 'tex', 'bibtex'):
    binary = repo / 'build/build-texlive-host/texk/web2c' / name
    proc = subprocess.run([str(binary), '--version'], capture_output=True, text=True)
    audit['engines'][name] = {'exitCode': proc.returncode, 'banner': proc.stdout.splitlines()[:2]}
for kind in ('host', 'ohos'):
    proc = subprocess.run([str(repo / f'build/build-texlive-{kind}/config.status'), '--config'], capture_output=True, text=True)
    audit['configure'][kind] = proc.stdout.strip()
for package in ('latex', 'latex-base-dev', 'biblatex', 'l3kernel'):
    with tarfile.open(dist / '.tlpkg-cache' / (package + '.tar.xz')) as tar:
        metadata = next((m for m in tar if m.name.endswith('.tlpobj')), None)
        audit['packages'][package] = tar.extractfile(metadata).read().decode() if metadata else 'no metadata'
        matches = []
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith('/latex.ltx'):
                relative = member.name.removeprefix('texmf-dist/')
                actual = dist / 'texmf' / relative
                matches.append({'archivePath': member.name, 'installed': actual.exists(),
                                'matchesArchive': actual.exists() and digest(actual) == hashlib.sha256(tar.extractfile(member).read()).hexdigest()})
        if matches:
            audit['kernelFiles'][package] = matches
audit['hostAndTargetConfigureMatch'] = audit['configure']['host'] == audit['configure']['ohos']
audit['deviceValidation'] = 'not_run'
(out / 'dependency-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps({k: audit[k] for k in ('archiveCount', 'runtimeFileCount', 'engines', 'kernelFiles')}, indent=2))
