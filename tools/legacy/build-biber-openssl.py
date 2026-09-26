"""Build pinned OpenSSL LTS for OHOS, isolated from host SSL libraries."""
import hashlib,json,os,pathlib,subprocess,tarfile,urllib.request
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK'])
native=repo/'build/biber-native';out=root/'validation/biber/native';version='3.5.8';name='openssl-'+version
url='https://github.com/openssl/openssl/releases/download/'+name+'/'+name+'.tar.gz';archive=root/'validation/biber/downloads'/(name+'.tar.gz')
checksum=out/(name+'.sha256')
for remote,path in [(url+'.sha256',checksum),(url,archive)]:
    if not path.exists():
        with urllib.request.urlopen(remote,timeout=120) as r:path.with_suffix(path.suffix+'.part').write_bytes(r.read())
        path.with_suffix(path.suffix+'.part').replace(path)
digest=hashlib.sha256(archive.read_bytes()).hexdigest();assert digest==checksum.read_text().split()[0]
source=native/name
if not source.exists():
    with tarfile.open(archive) as t:t.extractall(native,filter='data')
prefix=native/'install';tc=sdk/'llvm/bin';env=os.environ.copy()
env.update(CC=str(tc/'clang')+' --target=aarch64-linux-ohos --sysroot='+str(sdk/'sysroot'),AR=str(tc/'llvm-ar'),RANLIB=str(tc/'llvm-ranlib'))
args=['perl','Configure','linux-aarch64','no-shared','no-module','no-tests','no-async','no-zlib','no-comp','no-engine','no-apps',
 '--prefix='+str(prefix),'--openssldir='+str(prefix/'ssl'),'--libdir=lib','-fPIC']
with (out/'openssl-build.log').open('w') as log:
    for command in [args,['make','-j6','build_libs'],['make','install_dev']]:
        subprocess.run(command,cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
(out/'openssl-source.lock.json').write_text(json.dumps({'name':'OpenSSL','version':version,'url':url,'sha256':digest,
 'upstreamChecksumVerified':True,'license':'Apache-2.0','target':'aarch64-linux-ohos','configuration':args,'executionValidated':False},indent=2)+'\n')
print('OpenSSL OHOS static libraries built:',version)
