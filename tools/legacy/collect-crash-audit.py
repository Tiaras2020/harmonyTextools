"""Copy only the user-designated crash evidence to public Downloads for audit."""
from pathlib import Path
import shutil
src = Path.home() / '.dsh/work/crash-evidence'
dst = Path.home() / 'Download/CrashAudit130'
dst.mkdir(exist_ok=True)
for p in src.iterdir():
    if p.is_file() and not p.is_symlink():
        shutil.copy2(p, dst / p.name)
print('Crash evidence copied:', len(list(dst.iterdir())))
