"""Cross-build upstream btparse and add its static Text::BibTeX XS adapter."""
import hashlib,json,os,pathlib,shutil,subprocess,tarfile
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK'])
work=repo/'build/biber-perl-5.40.3';module=work/'cpan/Text-BibTeX';native=repo/'build/biber-native';prefix=native/'install';out=root/'validation/biber/native'
archive=root/'validation/biber/downloads/Text-BibTeX-0.91.tar.gz'
if not module.exists():
    module.mkdir()
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            parts=pathlib.PurePosixPath(m.name).parts
            if len(parts)<2:continue
            m.name=str(pathlib.PurePosixPath(*parts[1:]));t.extract(m,module,filter='data')
src=module/'btparse/src';objects=native/'btparse-objects';objects.mkdir(exist_ok=True)
cc=[str(sdk/'llvm/bin/clang'),'--target=aarch64-linux-ohos','--sysroot='+str(sdk/'sysroot'),'-D_GNU_SOURCE','-Werror=implicit-function-declaration','-O2','-fPIC']
features={}
for name,code in {'ALLOCA_H':'#include <alloca.h>\nint main(){return alloca(3)==0;}','VSNPRINTF':'#include <stdio.h>\nint main(){return vsnprintf==0;}','STRLCAT':'#include <string.h>\nint main(){char b[8]={0};return strlcat(b,"x",8);}'}.items():
    p=objects/('probe-'+name+'.c');p.write_text(code)
    result=subprocess.run(cc+[str(p),'-o',str(p.with_suffix(''))],capture_output=True)
    (out/('btparse-probe-'+name+'.log')).write_bytes(result.stdout+result.stderr)
    features[name]=result.returncode==0
text=(src/'bt_config.h.in').read_text()
values={'PACKAGE':'"libbtparse"','FPACKAGE':'"libbtparse 0.91"','VERSION':'"0.91"'}
values.update({name:('define HAVE_'+name+' 1' if ok else 'undef HAVE_'+name) for name,ok in features.items()})
for name,value in values.items():text=text.replace('[% '+name+' %]',value)
assert '[%' not in text
(src/'bt_config.h').write_text(text)
obj=[]
with (out/'btparse-build.log').open('w') as log:
    for p in sorted(src.glob('*.c')):
        target=objects/(p.stem+'.o');subprocess.run(cc+['-I'+str(src),'-I'+str(module/'btparse/pccts'),'-c',str(p),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True);obj.append(str(target))
    subprocess.run([str(sdk/'llvm/bin/llvm-ar'),'rcs',str(prefix/'lib/libbtparse.a'),*obj],stdout=log,stderr=subprocess.STDOUT,check=True)
for p in (module/'xscode').iterdir():
    if p.suffix in ('.c','.h','.xs') or p.name=='typemap':shutil.copy2(p,module/p.name)
(module/'Makefile.PL').write_text("# OHOS static adapter; upstream Build.PL retained.\nuse ExtUtils::MakeMaker;\nWriteMakefile(NAME=>'Text::BibTeX', VERSION_FROM=>'lib/Text/BibTeX.pm', LICENSE=>'perl_5', OBJECT=>'$(O_FILES)', INC=>'-I"+str(src)+"', LIBS=>['-L"+str(prefix/'lib')+" -lbtparse -lm']);\n")
pm=module/'lib/Text/BibTeX.pm';text=pm.read_text()
if 'require DynaLoader;' in text:
    pm.with_suffix('.pm.upstream').write_text(text)
    text=text.replace('require DynaLoader;','require XSLoader;').replace('@ISA = qw(Exporter DynaLoader);','@ISA = qw(Exporter);').replace('bootstrap Text::BibTeX;','XSLoader::load(__PACKAGE__, $VERSION);')
    pm.write_text(text)
build=root/'validation/biber/xs-bootstrap/build.sh';text=build.read_text().replace('.configured-biber-xml-v1','.configured-biber-bibtex-v1');build.write_text(text)
(out/'btparse-result.json').write_text(json.dumps({'compiled':True,'version':'0.91','sourceSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'featureProbes':features,'objects':len(obj),'executionValidated':False},indent=2)+'\n')
print('btparse static library and Text::BibTeX adapter prepared.')
