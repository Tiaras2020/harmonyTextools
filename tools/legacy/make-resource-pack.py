"""Build a deterministic additive-v1 ZIP from a reviewed texmf directory."""
import argparse
import hashlib
import json
import pathlib
import zipfile

def build(tree, output, package_id, version, title, compatibility):
    files = {}
    sources = {}
    for path in sorted(tree.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not allowed: ' + str(path))
        if not path.is_file():
            continue
        name = 'texmf/' + path.relative_to(tree).as_posix()
        data = path.read_bytes()
        files[name] = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        sources[name] = data
    manifest = {'schema': 1, 'profile': 'additive-v1', 'id': package_id, 'version': version,
                'title': title, 'compatibilityId': compatibility, 'files': files}
    if output.exists():
        raise FileExistsError('Refusing to overwrite ' + str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, data in [('manifest.json', (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()), *sources.items()]:
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return manifest

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--texmf', type=pathlib.Path, required=True)
    p.add_argument('--output', type=pathlib.Path, required=True)
    p.add_argument('--id', required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--title', required=True)
    args = p.parse_args()
    root = pathlib.Path(__file__).resolve().parent.parent
    release = json.loads((root/'texstudio-harmony/release.json').read_text())
    result = build(args.texmf, args.output, args.id, args.version, args.title, release['compatibilityId'])
    print('Resource pack:', args.output, 'files:', len(result['files']))
