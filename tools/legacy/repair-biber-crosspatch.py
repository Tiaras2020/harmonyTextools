"""Restore only three files in the fresh experimental tree before crosspatch."""
import os,pathlib,tarfile
root=pathlib.Path(__file__).resolve().parents[1]
work=pathlib.Path(os.environ['BUILD_REPO'])/'build/biber-perl-5.40.3'
assert not (work/'cnf/diffs/perl5-5.40.3/xconfig.applied').exists()
with tarfile.open(root/'validation/latexmk/downloads/perl-5.40.3.tar.xz') as t:
    for name in ('perl.h','locale.c','perl_langinfo.h'):
        p=work/name;p.chmod(p.stat().st_mode|0o200);p.write_bytes(t.extractfile('perl-5.40.3/'+name).read())
