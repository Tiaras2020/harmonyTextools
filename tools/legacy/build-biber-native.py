"""Build pinned XML libraries for OHOS in an isolated static prefix."""
import hashlib,json,os,pathlib,subprocess,tarfile,urllib.request
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK'])
work=repo/'build/biber-native';prefix=work/'install';out=root/'validation/biber/native';out.mkdir(exist_ok=True);work.mkdir(exist_ok=True)
records=[]
for name,version,series in [('libxml2','2.15.4','2.15'),('libxslt','1.1.45','1.1')]:
    archive=f'{name}-{version}.tar.xz';url=f'https://download.gnome.org/sources/{name}/{series}/{archive}'
    path=root/'validation/biber/downloads'/archive
    if not path.exists():
        with urllib.request.urlopen(url,timeout=90) as r:path.write_bytes(r.read())
    checksumurl=url.replace('.tar.xz','.sha256sum')
    checksum=out/f'{name}-{version}.sha256sum'
    if not checksum.exists():
        with urllib.request.urlopen(checksumurl,timeout=90) as r:checksum.write_bytes(r.read())
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert any(line.split()[0]==digest and line.split()[-1]==archive for line in checksum.read_text().splitlines())
    source=work/f'{name}-{version}'
    if not source.exists():
        with tarfile.open(path) as t:t.extractall(work,filter='data')
    build=work/(name+'-build')
    args=['cmake','-S',str(source),'-B',str(build),'-DCMAKE_SYSTEM_NAME=Linux','-DCMAKE_SYSTEM_PROCESSOR=aarch64',
      '-DCMAKE_C_COMPILER='+str(sdk/'llvm/bin/clang'),'-DCMAKE_C_COMPILER_TARGET=aarch64-linux-ohos',
      '-DCMAKE_SYSROOT='+str(sdk/'sysroot'),'-DCMAKE_INSTALL_PREFIX='+str(prefix),'-DCMAKE_BUILD_TYPE=Release',
      '-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DBUILD_SHARED_LIBS=OFF','-DCMAKE_FIND_ROOT_PATH='+str(prefix)+';'+str(sdk/'sysroot'),
      '-DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY','-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY','-DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY',
      '-DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER']
    if name=='libxml2':args+=['-DLIBXML2_WITH_PYTHON=OFF','-DLIBXML2_WITH_TESTS=OFF','-DLIBXML2_WITH_PROGRAMS=OFF','-DLIBXML2_WITH_ICONV=OFF','-DLIBXML2_WITH_ZLIB=OFF','-DLIBXML2_WITH_LZMA=OFF','-DLIBXML2_WITH_ICU=OFF']
    else:args+=['-DLIBXSLT_WITH_PYTHON=OFF','-DLIBXSLT_WITH_TESTS=OFF','-DLIBXSLT_WITH_PROGRAMS=OFF','-DLIBXSLT_WITH_CRYPTO=OFF','-DLIBXML2_INCLUDE_DIR='+str(prefix/'include/libxml2'),'-DLIBXML2_LIBRARY='+str(prefix/'lib/libxml2.a')]
    with (out/(name+'-build.log')).open('w') as log:
        for command in (args,['cmake','--build',str(build),'-j6'],['cmake','--install',str(build)]):
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    records.append({'name':name,'version':version,'url':url,'sha256':digest,'upstreamChecksumVerified':True,'license':'MIT','prefix':str(prefix),'linkage':'static'})
    print(name,version,'OHOS build passed',flush=True)
(out/'sources.lock.json').write_text(json.dumps(records,indent=2)+'\n')
