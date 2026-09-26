"""Fail closed if a cached build input differs from the reviewed dependency lock."""
import argparse
import hashlib
import json
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+')
args = parser.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
lock = json.loads((root / 'dependencies.lock.json').read_text())
for value in args.files:
    path = pathlib.Path(value).resolve()
    key = path.relative_to(root).as_posix()
    if key not in lock['archives']:
        raise SystemExit('Unreviewed archive: ' + key)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    if h.hexdigest() != lock['archives'][key]['sha256']:
        raise SystemExit('Archive hash mismatch: ' + key)
print('Locked archives verified:', len(args.files))
