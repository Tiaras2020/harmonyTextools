"""One-time guard for historical mutation scripts; retain their code as history."""
import pathlib
root = pathlib.Path(__file__).resolve().parent
names = ['build-fontconfig-fix.sh', 'package-fontconfig-fix.sh', 'build-icu-fix.sh',
         'build-xdv-fix.sh', 'build-preview-fix.sh', 'build-mcm-fix.sh']
for name in names:
    path = root / name
    content = path.read_text(encoding='utf-8')
    marker = '# Historical migration: retained for audit, not a release entry point.'
    if marker not in content:
        first, rest = content.split('\n', 1)
        content = first + '\n' + marker + '\n' + "echo 'Historical migration disabled. Use release.json and the current RUNBOOK baseline workflow.' >&2\nexit 2\n" + rest
        path.write_text(content, encoding='utf-8', newline='\n')
print('Historical version migration scripts guarded')
