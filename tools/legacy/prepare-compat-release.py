"""Build 1.0.21 from the accepted Lua runtime without touching 1.0.20."""
import hashlib, json, lzma, os, shutil, subprocess, sys
from pathlib import Path
root = Path(os.environ['DELIVERY_ROOT'])
repo = Path(os.environ['BUILD_REPO'])
out = root / 'validation/compat-fix-1.0.21'
out.mkdir(exist_ok=True)
old = repo / 'build/biber-perl-1.0.20'
work = repo / 'build/biber-perl-1.0.21'
if sys.argv[1] == 'prepare':
    if not work.exists():
        shutil.copytree(old, work, symlinks=True, ignore=shutil.ignore_patterns('stage'))
    for p in work.rglob('*'):
        if p.is_file() and p.name in ('Makefile','Makefile.PL','config.sh','config.h','config_heavy.pl','Config.pm','config.mk'):
            b=p.read_bytes(); c=b.replace(str(old).encode(),str(work).encode())
            if c!=b: p.write_bytes(c)
    (out/'perl').mkdir(exist_ok=True)
    s=(root/'validation/luahbtex/perl/build.sh').read_text().replace('validation/luahbtex/perl','validation/compat-fix-1.0.21/perl').replace('1.0.20','1.0.21')
    (out/'perl/build.sh').write_text(s)
    s=(root/'build-support/test-lua-release-biber.sh').read_text().replace('validation/luahbtex/perl','validation/compat-fix-1.0.21/perl').replace('1.0.20','1.0.21')
    (out/'perl/test.sh').write_text(s)
elif sys.argv[1] == 'stage':
    for name in ('assembled-dependency-audit.json','workflow/result.json','runtime-data-result.json'):
        assert json.loads((out/'perl'/name).read_text())['passed'], name
    candidate=repo/'build/resource-release-1.0.21'
    assert not (root/'artifacts/TeXstudioHarmony-1.0.21-arm64-device-signed.hap').exists(), 'Release is frozen'
    if not candidate.exists():
        shutil.copytree(repo/'build/resource-release-1.0.20',candidate,symlinks=True,
            ignore=lambda directory,names: ['perl5'] if Path(directory).name=='lib' and Path(directory).parent.name=='resource-release-1.0.20' else [])
    cnf=candidate/'texmf/web2c/texmf.cnf';cnf.write_text(cnf.read_text().replace('texlive_1.0.20','texlive_1.0.21'))
    font=candidate/'texmf/fonts/conf/fonts.conf';s=font.read_text()
    assert s.count('prefix="default"')==2 or s.count('prefix="relative"')==2
    font.write_text(s.replace('prefix="default"','prefix="relative"'))
    perl=work/'stage/data/service/hnp/texlive.org/texlive_1.0.21'
    shutil.copy2(perl/'bin/perl',candidate/'bin/perl')
    def copy_runtime_file(src,dst):
        src,dst=Path(src),Path(dst)
        if dst.exists() and src.read_bytes()==dst.read_bytes(): return str(dst)
        if dst.exists(): dst.chmod(dst.stat().st_mode | 0o200)
        return shutil.copy2(src,dst)
    shutil.copytree(perl/'lib/perl5',candidate/'lib/perl5',dirs_exist_ok=True,copy_function=copy_runtime_file)
    tc=Path(os.environ['NATIVE_OHOS_SDK'])/'llvm/bin'
    for name in ('latexmk','biber'):
        subprocess.run([str(tc/'clang'),'--target=aarch64-linux-ohos','--sysroot='+os.environ['NATIVE_OHOS_SDK']+'/sysroot','-O2','-Wall','-Wextra','-Werror','-DHARMONY_RUNTIME_ROOT="/data/service/hnp/texlive.org/texlive_1.0.21"',str(root/('texstudio-harmony/scripts/texlive/'+name+'_launcher.c')),'-o',str(candidate/'bin'/name)],check=True)
    for name in ('latexmk','biber','perl'): subprocess.run([str(tc/'llvm-strip'),str(candidate/'bin'/name)],check=True)
    sys.path.insert(0,str(root/'texstudio-harmony/scripts/texlive'))
    from full_resources import digest,read_database,download,extract_package,relative
    policy=json.loads((root/'texstudio-harmony/scripts/texlive/resource-policy.json').read_text())
    metadata=root/'validation/full-resources/texlive.tlpdb.xz'
    assert digest(metadata)==policy['metadataSha256']
    p=read_database(lzma.decompress(metadata.read_bytes()).decode())['bibtex']
    cache=out/'archives';cache.mkdir(exist_ok=True)
    archive=download('bibtex',p,cache,policy['repository'])
    extracted=out/'bibtex-resources';extracted.mkdir(exist_ok=True)
    extract_package(archive,p,extracted,policy)
    files={}
    for f in p['runfiles']:
        rel=relative(f);source=extracted/rel;dest=candidate/'texmf'/rel
        assert source.is_file()
        if dest.exists(): assert digest(dest)==digest(source), rel
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);files[rel]=digest(dest)
    report={'baseline':'1.0.20','version':'1.0.21','package':'bibtex','revision':p['revision'],'archiveSha512':digest(archive,'sha512'),'metadataSha256':digest(metadata),'files':files,'deviceValidated':False}
    (out/'resources.json').write_text(json.dumps(report,indent=2)+'\n')
    lic=candidate/'share/licenses/bibtex-base';lic.mkdir(parents=True,exist_ok=True)
    shutil.copy2(out/'resources.json',lic/'resources.json')
else: raise SystemExit('prepare or stage required')
