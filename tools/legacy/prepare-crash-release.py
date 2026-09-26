from pathlib import Path
import json,os,shutil
r=Path(__file__).resolve().parents[1]
repo=Path(os.environ['BUILD_REPO']);out=r/'validation/crash-fix-1.0.30'
p=r/'texstudio-harmony/release.json';d=json.loads(p.read_text());d.update(version='1.0.30',versionCode=1000030,runtimeVersion='1.0.30');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
old=repo/'build/biber-perl-1.0.21';work=repo/'build/biber-perl-1.0.30'
if not work.exists():shutil.copytree(old,work,symlinks=True,ignore=shutil.ignore_patterns('stage'))
for p in work.rglob('*'):
    if p.is_file() and p.name in ('Makefile','Makefile.PL','config.sh','config.h','config_heavy.pl','Config.pm','config.mk'):
        b=p.read_bytes();c=b.replace(str(old).encode(),str(work).encode())
        if b!=c:p.write_bytes(c)
(out/'perl').mkdir(exist_ok=True)
s=(r/'validation/compat-fix-1.0.21/perl/build.sh').read_text().replace('compat-fix-1.0.21','crash-fix-1.0.30').replace('1.0.21','1.0.30')
(out/'perl/build.sh').write_text(s)
print('Prepared new version and isolated Perl prefix build')
