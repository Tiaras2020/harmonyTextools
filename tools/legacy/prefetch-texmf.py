import os, re, pathlib, subprocess, concurrent.futures, lzma
from release_config import release
repo=pathlib.Path(os.environ['BUILD_REPO'])
s=(repo/'scripts/texlive/build_pack_texmf.sh').read_text()
names=[]
for block in re.findall(r'^PACKAGES_\w+=\((.*?)^\)',s,re.M|re.S):
    for line in block.splitlines():
        names.extend(line.split('#',1)[0].split())
names=list(dict.fromkeys(names))
cache=repo/'build/build-texlive-ohos-dist/.tlpkg-cache'
cache.mkdir(parents=True,exist_ok=True)
base=release()['texliveRepository']+'/'
def fetch(name):
    p=cache/(name+'.tar.xz')
    if not p.exists():
        tmp=p.with_suffix('.xz.partial')
        result=subprocess.run(['curl','-fsSL','--retry','2','--connect-timeout','20','--max-time','120',base+p.name,'-o',str(tmp)],capture_output=True)
        if result.returncode:
            return name,False,result.stderr.decode(errors='replace')
        tmp.replace(p)
    try:
        with lzma.open(p) as f:
            while f.read(1048576): pass
        subprocess.run(['python3',str(repo/'scripts/verify_archives.py'),str(p)],check=True,capture_output=True)
        return name,True,str(p.stat().st_size)
    except Exception as e:
        return name,False,str(e)
failed=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for name,ok,detail in pool.map(fetch,names):
        print(('OK ' if ok else 'FAIL ')+name+' '+detail,flush=True)
        if not ok: failed.append(name)
print('PACKAGES:',len(names),'FAILED:',failed,flush=True)
raise SystemExit(bool(failed))
