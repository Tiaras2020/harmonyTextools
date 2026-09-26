from pathlib import Path
import shutil
src=Path('/storage/Users/currentUser/Documents/ProjectCli30')
dst=Path('/storage/Users/currentUser/Documents/CloseAudit130')
dst.mkdir(exist_ok=True)
for name in ('main.tex','child.tex','plain.tex','engine-test/main.tex','root3.tex','child3.tex'):
    p=src/name
    if p.is_file():
        q=dst/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
print('Fixture copied',len(list(dst.rglob('*.tex'))))
