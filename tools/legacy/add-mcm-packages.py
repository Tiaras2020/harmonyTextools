"""Add TeX Live 2025 runtime packages required by the user's MCM project."""
import concurrent.futures, hashlib, json, os, pathlib, tarfile, urllib.request, re, subprocess
from release_config import release

repo=pathlib.Path(os.environ['BUILD_REPO'])
dist=repo/'build/build-texlive-ohos-dist'
texmf=dist/'texmf'
cache=dist/'.tlpkg-cache'
out=pathlib.Path(os.environ['DELIVERY_ROOT'])/'validation/mcm-project'
out.mkdir(parents=True,exist_ok=True)
packages=['mcmthesis','biblatex','todonotes','tocloft','fancybox','appendix','paralist','bera','jknapltx','rsfs','logreq','xpatch','marginnote','amscls','carlisle','trimspaces','tex-gyre','symbol','mweights','kastrup']
mirror=release()['texliveRepository']

def fetch(package):
    archive=cache/(package+'.tar.xz')
    if not archive.exists():
        request=urllib.request.Request(f'{mirror}/{package}.tar.xz',headers={'User-Agent':'TeXstudio-Harmony-build'})
        with urllib.request.urlopen(request,timeout=90) as r:
            data=r.read()
        with tarfile.open(fileobj=__import__('io').BytesIO(data),mode='r:xz'):
            pass
        archive.write_bytes(data)
    subprocess.run(['python3', str(repo/'scripts/verify_archives.py'), str(archive)], check=True)
    return package,archive

records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    for package,archive in executor.map(fetch,packages):
        files=[]
        with tarfile.open(archive) as tar:
            for member in tar:
                path=pathlib.PurePosixPath(member.name)
                if path.parts and path.parts[0]=='texmf-dist':
                    path=pathlib.PurePosixPath(*path.parts[1:])
                if not path.parts or path.parts[0] not in ('tex','fonts','bibtex','makeindex') or not member.isfile():
                    continue
                assert not path.is_absolute() and '..' not in path.parts
                dest=texmf/path
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(tar.extractfile(member).read())
                files.append(str(path))
        records.append({'package':package,'url':f'{mirror}/{package}.tar.xz','sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':files})
        print(package,len(files),'runtime files',flush=True)

# Merge font maps by font name, matching the existing packaging workflow.
entries={}
maps=texmf/'fonts/map'
for path in sorted(maps.rglob('*.map')):
    if 'updmap' in path.parts or path.relative_to(maps).parts[0] not in ('dvips','pdftex'):
        continue
    for line in path.read_text(errors='replace').splitlines():
        line=line.strip()
        fields=line.split()
        if not fields or line.startswith(('%','#')):
            continue
        if len(fields)>len(entries.get(fields[0],'').split()):
            entries[fields[0]]=line
# Embed available Type 1 font programs even for the PDF standard fonts.
# The Harmony previewer has no desktop system-font substitution inventory.
pfbs={p.stem:p.name for p in (texmf/'fonts/type1').rglob('*.pfb')}
font_programs={}
for afm in (texmf/'fonts/afm').rglob('*.afm'):
    if afm.stem not in pfbs:
        continue
    match=re.search(r'^FontName\s+(\S+)',afm.read_text(errors='replace'),re.M)
    if match:
        font_programs[match[1]]=pfbs[afm.stem]
for name,line in entries.items():
    fields=line.split()
    if len(fields)>1 and fields[1] in font_programs and '.pfb' not in line.lower():
        entries[name]=line+' <'+font_programs[fields[1]]
text='\n'.join(entries[k] for k in sorted(entries))+'\n'
for relative in ('pdftex/updmap/pdftex.map','dvips/updmap/psfonts.map'):
    (maps/relative).write_text(text)
(out/'added-packages.json').write_text(json.dumps(records,indent=2)+'\n')
cnf=texmf/'web2c/texmf.cnf'
configuration=cnf.read_text()
if 'VFFONTS =' not in configuration:
    configuration+='\nVFFONTS = .;$TEXMFDIST/fonts/vf//\n'
cnf.write_text(configuration)
