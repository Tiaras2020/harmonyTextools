"""Read-only filesystem inventory; never follow symlinks or print file contents."""
import collections, datetime, json, os, stat, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2])
groups = collections.defaultdict(lambda: {'bytes': 0, 'files': 0})
large, errors, links, inventory = [], [], [], []
for base, dirs, files in os.walk(root, followlinks=False, onerror=lambda e: errors.append(str(e))):
    for name in dirs[:]:
        path = Path(base) / name
        if path.is_symlink():
            links.append(str(path.relative_to(root)))
            dirs.remove(name)
    for name in files:
        path = Path(base) / name
        rel = path.relative_to(root)
        try:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                links.append(str(rel))
                continue
            inventory.append((str(rel), info.st_size))
            for depth in (1, 2, 3):
                key = '/'.join(rel.parts[:depth]) if len(rel.parts) > depth else '/'.join(rel.parts[:-1]) or '.'
                # Depth stored separately so small root files are not double counted.
                group = groups[str(depth) + ':' + key]
                group['bytes'] += info.st_size
                group['files'] += 1
            if info.st_size >= 100 * 1024**2:
                large.append({'path': str(rel), 'bytes': info.st_size})
        except OSError as error:
            errors.append(str(error))
report = {'root': str(root), 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sizeMeaning':'logical file bytes; not allocated disk size; no symlink traversal', 'groups':dict(sorted(groups.items(), key=lambda x: -x[1]['bytes'])), 'largeFiles':sorted(large,key=lambda x:-x['bytes']), 'symlinks':links, 'errors':errors}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
output.with_suffix('.files.tsv').write_text('bytes\tpath\n' + ''.join(str(size)+'\t'+name+'\n' for name,size in sorted(inventory)),encoding='utf-8')
print(json.dumps({'root':str(root),'top':{k:v for k,v in report['groups'].items() if k.startswith('1:')},'errors':errors},ensure_ascii=False))
