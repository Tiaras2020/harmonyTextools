"""Generate bundled encoding tables with matching Perl sources, then cross-build XS."""
import os,pathlib,re,shutil,subprocess
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);work=repo/'build/biber-perl-5.40.3'
out=root/'validation/biber'
for name in ('EUCJPASCII','JIS2K','HanExtra'):
    dest=work/'cpan'/('Encode-'+name)
    if not dest.exists():shutil.copytree(repo/'build/biber-deps'/('Encode-'+name),dest)
    makefile=dest/'Makefile.PL';backup=dest/'Makefile.PL.upstream'
    if not backup.exists():shutil.copy2(makefile,backup)
    text=backup.read_text()
    declaration='my ($enc2xs, $encode_h) = ();';start=text.index(declaration)+len(declaration);last='print "encode.h is at $encode_h\\n";';end=text.index(last,start)+len(last)
    text=text[:start]+"$enc2xs = '"+str(work/'cpan/Encode/bin/enc2xs')+"';\n$encode_h = '"+str(work/'cpan/Encode/Encode')+"';\n"+text[end:]
    # Module::Install is packaging machinery; retain its upstream MY::* table
    # generation methods but use MakeMaker directly for the OHOS adapter.
    if name=='HanExtra':
        text=text.replace('use inc::Module::Install;','use ExtUtils::MakeMaker;')
        start=text.index("name        'Encode-HanExtra';");end=text.index('package MY;',start)
        text=text[:start]+"WriteMakefile(NAME=>'Encode::HanExtra', VERSION_FROM=>'lib/Encode/HanExtra.pm', INC=>\"-I$encode_h\", OBJECT=>'$(O_FILES)', XSOPT=>'-nolinenumbers');\n\n"+text[end:]
    makefile.write_text(text)
    # Host Perl only generates portable .xs and table .c/.h inputs. No host
    # objects or libraries are compiled or copied into the target runtime.
    with (out/('encoding-'+name+'-generate.log')).open('w') as log:
        subprocess.run(['perl','Makefile.PL'],cwd=dest,stdout=log,stderr=subprocess.STDOUT,check=True)
        for fnm in sorted(dest.glob('*.fnm')):
            subprocess.run(['perl',str(work/'cpan/Encode/bin/enc2xs'),'-Q','-o',fnm.stem+'.c','-f',fnm.name],cwd=dest,stdout=log,stderr=subprocess.STDOUT,check=True)
    (dest/'Makefile').unlink()
    assert (dest/(name+'.xs')).is_file()
    print('Generated target encoding sources:',name,flush=True)
build=out/'xs-bootstrap/build.sh';text=build.read_text();text=re.sub(r'\.configured-biber-[a-z0-9-]+','.configured-biber-encodings-v1',text);build.write_text(text)
