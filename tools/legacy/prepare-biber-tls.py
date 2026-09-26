"""Register Net::SSLeay against the isolated OHOS OpenSSL static prefix."""
import os,pathlib,re,shutil
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);work=repo/'build/biber-perl-5.40.3'
prefix=repo/'build/biber-native/install';dest=work/'cpan/Net-SSLeay'
assert (prefix/'lib/libssl.a').is_file() and (prefix/'lib/libcrypto.a').is_file()
if not dest.exists():shutil.copytree(repo/'build/biber-deps/Net-SSLeay',dest)
makefile=dest/'Makefile.PL'
if not (dest/'Makefile.PL.upstream').exists():shutil.copy2(makefile,dest/'Makefile.PL.upstream')
makefile.write_text("use ExtUtils::MakeMaker;\nWriteMakefile(NAME=>'Net::SSLeay', VERSION_FROM=>'lib/Net/SSLeay.pm', OBJECT=>'SSLeay$(OBJ_EXT)', DEFINE=>'-DNET_SSLEAY_PERL_VERSION=5040003 -DOPENSSL_API_COMPAT=908', INC=>'-I"+str(prefix/'include')+"', LIBS=>['-L"+str(prefix/'lib')+" -lssl -lcrypto -ldl -lpthread']);\n")
build=root/'validation/biber/xs-bootstrap/build.sh';text=build.read_text();text=re.sub(r'\.configured-biber-[a-z0-9-]+','.configured-biber-tls-v1',text);build.write_text(text)
print('Net::SSLeay OHOS static adapter prepared.')
