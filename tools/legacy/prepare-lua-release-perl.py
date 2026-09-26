"""Rebuild the accepted Biber Perl tree for the 1.0.20 installation prefix."""
import os
from pathlib import Path
import shutil
repo = Path(os.environ['BUILD_REPO'])
root = Path(os.environ['DELIVERY_ROOT'])
old = repo / 'build/biber-perl-1.0.19'
work = repo / 'build/biber-perl-1.0.20'
out = root / 'validation/luahbtex/perl'
out.mkdir(exist_ok=True)
if not work.exists():
    shutil.copytree(old, work, symlinks=True, ignore=shutil.ignore_patterns('stage'))
for path in work.rglob('*'):
    if path.is_file() and path.name in ('Makefile', 'Makefile.PL', 'config.sh', 'config.h', 'config_heavy.pl', 'Config.pm', 'config.mk'):
        data = path.read_bytes()
        changed = data.replace(str(old).encode(), str(work).encode())
        if changed != data:
            path.write_bytes(changed)
text = (root / 'validation/biber/polish-1.0.19/build.sh').read_text()
text = text.replace('validation/biber/polish-1.0.19', 'validation/luahbtex/perl').replace('1.0.19', '1.0.20')
(out / 'build.sh').write_text(text)
print('Prepared isolated Perl 1.0.20 build')
