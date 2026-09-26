"""Add the independently tested Perl runtime to a versioned candidate only."""
import hashlib,json,os,pathlib,shutil,subprocess
from release_config import release
root=pathlib.Path(os.environ['DELIVERY_ROOT']); repo=pathlib.Path(os.environ['BUILD_REPO'])
version=release()['version']
assert version in ('1.0.17','1.0.18','1.0.19'),'Rebuild Perl with the new HNP installation prefix before changing version'
proof=json.loads((root/'validation/latexmk/qemu-result.json').read_text()); assert proof['passed']
assert json.loads((root/'validation/latexmk/host-regression/result.json').read_text())['passed']
work=repo/'build'/('biber-perl-1.0.19' if version=='1.0.19' else 'biber-perl-5.40.3' if version=='1.0.18' else 'perl-ohos-5.40.3'); prefix=f'/data/service/hnp/texlive.org/texlive_{version}'
runtime=work/'stage'/prefix.lstrip('/'); candidate=repo/'build'/('resource-release-'+version)
if version in ('1.0.18','1.0.19'):
    audit=json.loads((root/('validation/biber/polish-1.0.19/assembled-dependency-audit.json' if version=='1.0.19' else 'validation/biber/assembled-dependency-audit.json')).read_text());assert audit['passed']
    assert audit['interpreterSha256']==hashlib.sha256((runtime/'bin/perl').read_bytes()).hexdigest()
assert candidate.is_dir()
shutil.copy2(runtime/'bin/perl',candidate/'bin/perl')
shutil.copytree(runtime/'lib/perl5',candidate/'lib/perl5')
scripts=candidate/'share/latexmk'; scripts.mkdir()
shutil.copy2(root/'validation/latexmk/latexmk.pl',scripts/'latexmk.pl')
shutil.copy2(root/'texstudio-harmony/scripts/texlive/HarmonyCwd.pm',scripts/'HarmonyCwd.pm')
licenses=candidate/'share/licenses/perl'; licenses.mkdir(parents=True)
for name in ('Artistic','Copying','README','AUTHORS'): shutil.copy2(work/name,licenses/name)
sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK']); cc=sdk/'llvm/bin/clang'
subprocess.run([str(cc),'--target=aarch64-linux-ohos','--sysroot='+str(sdk/'sysroot'),'-O2','-Wall','-Wextra','-Werror',
    '-DHARMONY_RUNTIME_ROOT="'+prefix+'"',str(root/'texstudio-harmony/scripts/texlive/latexmk_launcher.c'),'-o',str(candidate/'bin/latexmk')],check=True)
for name in ('perl','latexmk'):
    subprocess.run([str(sdk/'llvm/bin/llvm-strip'),str(candidate/'bin'/name)],check=True)
    elf=subprocess.check_output([str(sdk/'llvm/bin/llvm-readelf'),'-h','-l','-d',str(candidate/'bin'/name)],text=True)
    assert 'AArch64' in elf and '/lib/ld-musl-aarch64.so.1' in elf
    (root/f'validation/latexmk/{name}-release-elf.txt').write_text(elf)
files={}
for base in (candidate/'bin/perl',candidate/'bin/latexmk',candidate/'lib/perl5',scripts,licenses):
    for path in ([base] if base.is_file() else sorted(base.rglob('*'))):
        if path.is_file(): files[str(path.relative_to(candidate))]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
output=root/('validation/biber/polish-1.0.19/latexmk-payload.json' if version=='1.0.19' else 'validation/biber/latexmk-payload.json' if version=='1.0.18' else 'validation/latexmk/payload.json')
output.write_text(json.dumps({'version':version,'prefix':prefix,'files':files},indent=2)+'\n')
print('Perl and latexmk payload staged:',len(files),'files')
