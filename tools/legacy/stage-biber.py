"""Stage the validated Biber runtime and public native command into candidate 1.0.18."""
import hashlib,json,os,pathlib,shutil,subprocess
from release_config import release
root=pathlib.Path(os.environ['DELIVERY_ROOT']);repo=pathlib.Path(os.environ['BUILD_REPO']);version=release()['version'];assert version in ('1.0.18','1.0.19')
out=root/'validation/biber';candidate=repo/'build'/('resource-release-'+version);overlay=repo/'build'/('biber-runtime-1.0.19' if version=='1.0.19' else 'biber-runtime')
for name in ('assembled-dependency-audit.json','workflow/result.json','remaining-upstream/result.json','tls/result.json','runtime-data-result.json'):
    assert json.loads((out/name).read_text())['passed'],name
proofout=out/'polish-1.0.19' if version=='1.0.19' else out
if version=='1.0.19':
    for name in ('assembled-dependency-audit.json','workflow/result.json','runtime-data-result.json'):
        assert json.loads((proofout/name).read_text())['passed'],name
assert candidate.is_dir();payload=json.loads((proofout/'latexmk-payload.json').read_text());prefix=payload['prefix']
dest=candidate/'share/biber';shutil.copytree(overlay,dest,ignore=shutil.ignore_patterns('*.xs','*.c','*.h','*.o','*.a','*.bs'))
licenses=candidate/'share/licenses/biber-native';licenses.mkdir(parents=True)
sources={'OpenSSL':repo/'build/biber-native/openssl-3.5.8','libxml2':repo/'build/biber-native/libxml2-2.15.4',
 'libxslt':repo/'build/biber-native/libxslt-1.1.45','sombok':repo/'build/biber-deps/Unicode-LineBreak/sombok',
 'Biber':repo/'build/biber-2.21'}
for name,source in sources.items():
    for p in source.iterdir():
        if p.is_file() and p.name.upper().startswith(('COPYING','COPYRIGHT','LICENSE','ARTISTIC','NOTICE')):
            target=licenses/name/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
for name in ('dependencies.lock.json','license-audit.json','assembly.json'):shutil.copy2(out/name,licenses/name)
sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK']);tc=sdk/'llvm/bin';binary=candidate/'bin/biber'
subprocess.run([str(tc/'clang'),'--target=aarch64-linux-ohos','--sysroot='+str(sdk/'sysroot'),'-O2','-Wall','-Wextra','-Werror',
 '-DHARMONY_RUNTIME_ROOT="'+prefix+'"',str(root/'texstudio-harmony/scripts/texlive/biber_launcher.c'),'-o',str(binary)],check=True)
subprocess.run([str(tc/'llvm-strip'),str(binary)],check=True)
elf=subprocess.check_output([str(tc/'llvm-readelf'),'-h','-l','-d',str(binary)],text=True);assert 'AArch64' in elf and '/lib/ld-musl-aarch64.so.1' in elf
(out/'biber-release-elf.txt').write_text(elf)
for base in (binary,dest,licenses):
    for path in ([base] if base.is_file() else sorted(base.rglob('*'))):
        if path.is_file():payload['files'][str(path.relative_to(candidate))]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(out/('payload-'+version+'.json')).write_text(json.dumps(payload,indent=2)+'\n')
print('Biber, Perl and latexmk staged:',len(payload['files']),'files')
