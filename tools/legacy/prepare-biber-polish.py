"""Clone the validated source tree and rebuild Perl for the new HNP prefix."""
import os,pathlib,shutil,json
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO'])
out=root/'validation/biber/polish-1.0.19';out.mkdir(exist_ok=True)
old=repo/'build/biber-perl-5.40.3';work=repo/'build/biber-perl-1.0.19'
if not work.exists():shutil.copytree(old,work,symlinks=True,ignore=shutil.ignore_patterns('stage'))
text=(root/'validation/biber/xs-bootstrap/build.sh').read_text()
text=text.replace('== 1.0.18 ]]','== 1.0.19 ]]').replace('validation/biber/xs-bootstrap','validation/biber/polish-1.0.19')
text=text.replace('build/biber-perl-5.40.3','build/biber-perl-1.0.19').replace('texlive_1.0.18','texlive_1.0.19').replace('.configured-biber-tls-v1','.configured-biber-polish-1.0.19')
# The copied MakeMaker files contain absolute paths to the original tree.
# Rewrite those build-only paths; keep the accepted source/runtime untouched.
for path in work.rglob('*'):
    if path.is_file() and path.name in ('Makefile','Makefile.PL','config.sh','config.h','config_heavy.pl','Config.pm','config.mk'):
        data=path.read_bytes();new=data.replace(str(old).encode(),str(work).encode())
        if new!=data:path.write_bytes(new)
(out/'build.sh').write_text(text)
overlay=repo/'build/biber-runtime-1.0.19'
if not overlay.exists():shutil.copytree(repo/'build/biber-runtime',overlay)
entry=overlay/'bin/biber';original=entry.read_text()
before='use FindBin;\nuse lib $FindBin::RealBin;'
after='# The native HNP launcher supplies the absolute module directory with -I.\n# FindBin realpath is unavailable across OHOS sandbox ancestors.'
assert original.count(before)==1 or original.count(after)==1
entry.write_text(original.replace(before,after))
print('Isolated 1.0.19 source, overlay and build script prepared.')
