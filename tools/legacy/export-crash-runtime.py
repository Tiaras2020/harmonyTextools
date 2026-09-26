from pathlib import Path
import os,shutil,subprocess
r=Path(__file__).resolve().parents[1];out=r/'validation/crash-fix-1.0.30'
repo=Path(os.environ['BUILD_REPO']);dest=out/'runtime-overlay';dest.mkdir(exist_ok=True)
stage=repo/'build/biber-perl-1.0.30/stage/data/service/hnp/texlive.org/texlive_1.0.30'
files=['bin/perl']+['lib/perl5/5.40.3/aarch64-linux/'+s for s in ('Config.pm','.packlist','CORE/libperl.a','CORE/config.h','Config_heavy.pl')]
for rel in files:
    target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(stage/rel,target)
for name in ('pdftex','xetex','latexmk','biber'):
    shutil.copy2(out/'engines'/name,dest/'bin'/name)
for name in ('pdftex','xetex','latexmk','biber','perl'):
    subprocess.run([os.environ['NATIVE_OHOS_SDK']+'/llvm/bin/llvm-strip',str(dest/'bin'/name)],check=True)
for alias,engine in {'pdflatex':'pdftex','latex':'pdftex','xelatex':'xetex'}.items():shutil.copy2(dest/'bin'/engine,dest/'bin'/alias)
print('Exported isolated runtime overlay; old artifacts unchanged')
