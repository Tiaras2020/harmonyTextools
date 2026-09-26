"""Prepare an isolated perl-cross tree for the first real third-party XS module."""
import os,pathlib,shutil,tarfile
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO'])
work=repo/'build/biber-perl-5.40.3';out=root/'validation/biber/xs-bootstrap';out.mkdir(exist_ok=True)
work.mkdir(exist_ok=True)
def extract_strip(archive,destination):
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            parts=pathlib.PurePosixPath(m.name).parts
            if len(parts)<2:continue
            m.name=str(pathlib.PurePosixPath(*parts[1:]))
            t.extract(m,destination,filter='data')
if not (work/'.sources-ready').exists():
    for name in ('perl-5.40.3.tar.xz','perl-cross-1.6.4.tar.gz'):
        extract_strip(root/'validation/latexmk/downloads'/name,work)
    (work/'.sources-ready').touch()
module=work/'cpan/Text-CSV_XS'
if not module.exists():
    module.mkdir()
    extract_strip(root/'validation/biber/downloads/Text-CSV_XS-1.64.tgz',module)
text=(root/'build-support/build-perl-ohos.sh').read_text()
text=text.replace('[[ "$PACKAGE_VERSION" == 1.0.17 ]]', '[[ "$PACKAGE_VERSION" == 1.0.17 || "$PACKAGE_VERSION" == 1.0.18 ]]')
text=text.replace('out="$DELIVERY_ROOT/validation/latexmk"','out="$DELIVERY_ROOT/validation/biber/xs-bootstrap"')
text=text.replace('work="$BUILD_REPO/build/perl-ohos-5.40.3"','work="$BUILD_REPO/build/biber-perl-5.40.3"')
text=text.replace('.configured-v7-1.0.17','.configured-biber-xs-v1')
text=text.replace('--prefix=/data/service/hnp/texlive.org/texlive_1.0.17','--prefix=/data/service/hnp/texlive.org/texlive_1.0.18')
patch_line='python3 "$DELIVERY_ROOT/build-support/patch-perl-ohos.py" "$work"\n'
text=text.replace(patch_line,'')
text=text.replace('make SHELL=/bin/sh -j6', 'make crosspatch > "$out/crosspatch.log" 2>&1\n'+patch_line+'make SHELL=/bin/sh -j6')
text=text.replace('make SHELL=/bin/sh -j6', 'make SHELL=/bin/sh lib/unicore/CombiningClass.pl > "$out/unicode-tables.log" 2>&1\nmake SHELL=/bin/sh -j6')
(out/'build.sh').write_text(text)
print('Isolated XS bootstrap prepared:',work)
