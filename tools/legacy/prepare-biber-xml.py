"""Add XML bindings to isolated static Perl with explicit OHOS build inputs."""
import hashlib,json,os,pathlib,tarfile
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);work=repo/'build/biber-perl-5.40.3';prefix=repo/'build/biber-native/install'
lock=json.loads((root/'validation/biber/dependencies.lock.json').read_text());records={d['distribution']:d for d in lock['distributions']}
for name in ('XML-LibXML','XML-LibXSLT','XML-NamespaceSupport','XML-SAX','XML-SAX-Base'):
    dest=work/'cpan'/name
    if not dest.exists():
        dest.mkdir()
        with tarfile.open(root/'validation/biber/downloads'/records[name]['archive']) as t:
            for m in t.getmembers():
                parts=pathlib.PurePosixPath(m.name).parts
                if len(parts)<2:continue
                m.name=str(pathlib.PurePosixPath(*parts[1:]));t.extract(m,dest,filter='data')
for name,module,versionfile,libs in [('XML-LibXML','XML::LibXML','LibXML.pm','-lxml2 -lm'),('XML-LibXSLT','XML::LibXSLT','lib/XML/LibXSLT.pm','-lexslt -lxslt -lxml2 -lm')]:
    dest=work/'cpan'/name;makefile=dest/'Makefile.PL'
    original=dest/'Makefile.PL.upstream'
    if not original.exists():original.write_bytes(makefile.read_bytes())
    defines='-DHAVE_UTF8 -DNO_XML_LIBXML_THREADS'+(' -DHAVE_EXSLT' if name=='XML-LibXSLT' else '')
    makefile.write_text("# OHOS static adapter; upstream source is preserved in Makefile.PL.upstream.\nuse ExtUtils::MakeMaker;\nWriteMakefile(NAME=>'"+module+"', VERSION_FROM=>'"+versionfile+"', LICENSE=>'perl_5', OBJECT=>'$(O_FILES)', DEFINE=>'"+defines+"', INC=>'-I"+str(prefix/'include/libxml2')+' -I'+str(prefix/'include')+' -I'+str(work/'cpan/XML-LibXML')+"', LIBS=>['-L"+str(prefix/'lib')+' '+libs+"']);\n")
    # MakeMaker does not make .o files depend on DEFINE/INC changes.
    # Invalidate only this experimental module's generated objects/archive.
    signature=hashlib.sha256(makefile.read_bytes()).hexdigest();stamp=dest/'.ohos-static-adapter.sha256'
    static_archive=work/'lib/auto'/module.replace('::','/')/(module.split('::')[-1]+'.a')
    if not stamp.exists() or stamp.read_text()!=signature or not static_archive.exists():
        targets=list(dest.glob('*.o'))+[static_archive,dest/'pm_to_blib',work/'static.list',work/'ext.libs']
        for target in targets:
            assert target.resolve().is_relative_to(work.resolve())
            if target.exists():target.unlink()
        stamp.write_text(signature)
pm=work/'cpan/XML-LibXSLT/lib/XML/LibXSLT.pm';text=pm.read_text()
start=text.find('    require DynaLoader;');end=text.find('    # the following magic',start)
if start>=0:
    assert 'bootstrap XML::LibXSLT $VERSION;' in text[start:end]
    pm.with_suffix('.pm.upstream').write_text(text)
    text=text[:start]+"    # Statically registered OHOS XS module; no shared-library search.\n    require XSLoader;\n    XSLoader::load(__PACKAGE__, $VERSION);\n\n"+text[end:];pm.write_text(text)
build=root/'validation/biber/xs-bootstrap/build.sh'
text=build.read_text().replace('.configured-biber-xs-v1','.configured-biber-xml-v1')
build.write_text(text)
print('XML bindings prepared with explicit static OHOS libraries.')
