"""Assemble an experimental offline Biber overlay without modifying release payloads."""
import hashlib,json,os,pathlib,re,shutil,subprocess,tarfile
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO'])
work=repo/'build/biber-perl-5.40.3';deps=repo/'build/biber-deps';overlay=repo/'build/biber-runtime';lib=overlay/'lib';lib.mkdir(parents=True,exist_ok=True)
lock=json.loads((root/'validation/biber/dependencies.lock.json').read_text());copied=[]
for r in lock['distributions']:
    name=r['distribution'];source=deps/name
    if r['containsXS'] or name.startswith(('Encode-HanExtra','Encode-JIS2K','Encode-EUCJPASCII','Alien-')):continue
    if (source/'lib').exists():shutil.copytree(source/'lib',lib,dirs_exist_ok=True)
    for p in source.glob('*.pm'):
        text=p.read_text(errors='replace');m=re.search(r'^package\s+([\w:]+)\s*[;{]',text,re.M)
        if m:
            target=lib/(m[1].replace('::','/')+'.pm');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    if (source/'share').is_dir():shutil.copytree(source/'share',lib/'auto/share/dist'/name,dirs_exist_ok=True)
    copied.append(name)
# The official Lingua::Translit build substitutes the shipped rule dump.
translit=deps/'Lingua-Translit'
subprocess.run(['perl',str(translit/'tools/substitute_tables.pl'),str(lib/'Lingua/Translit/Tables.pm')],cwd=translit,check=True,capture_output=True)
# Runtime pure modules and share files shipped together with native distributions.
for name in ('DateTime','Params-Validate'):
    source=deps/name
    if (source/'lib').exists():shutil.copytree(source/'lib',lib,dirs_exist_ok=True)
for name in ('DateTime-Locale','DateTime-TimeZone'):
    source=deps/name
    if (source/'share').exists():shutil.copytree(source/'share',lib/'auto/share/dist'/name,dirs_exist_ok=True)
archive=root/'validation/biber/downloads/biber-2.21.tar.gz';source=repo/'build/biber-2.21'
if not source.exists():
    source.mkdir()
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            parts=pathlib.PurePosixPath(m.name).parts
            if len(parts)<2:continue
            m.name=str(pathlib.PurePosixPath(*parts[1:]));t.extract(m,source,filter='data')
shutil.copytree(source/'lib',lib,dirs_exist_ok=True)
for p in (source/'data/schemata').glob('*.rn?'):shutil.copy2(p,lib/'Biber'/p.name)
for name in ('biber-tool.conf','bcf.xsl'):shutil.copy2(source/'data'/name,lib/'Biber'/name)
(overlay/'bin').mkdir(exist_ok=True);shutil.copy2(source/'bin/biber',overlay/'bin/biber')
# Older pure-Perl distributions keep callable subs after __END__.
# Generate their AutoLoader files rather than silently dropping those subs.
for p in lib.rglob('*.pm'):
    text=p.read_text(errors='replace')
    if re.search(r'^__END__\s*$',text,re.M) and re.search(r'\b(?:use|require)\s+AutoLoader\b',text):
        subprocess.run(['perl','-MAutoSplit','-e','AutoSplit::autosplit($ARGV[0],$ARGV[1],0,1,1)',str(p),str(lib/'auto')],check=True,capture_output=True)
# Preserve licensing material for every locked source; inclusion is not support.
for r in lock['distributions']:
    for p in (deps/r['distribution']).iterdir():
        if p.is_file() and p.name.upper().startswith(('LICENSE','COPYING','COPYRIGHT','README','ARTISTIC','GPL')):
            target=overlay/'licenses'/r['distribution']/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
report={'biberSourceSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'pureDistributionsCopied':copied,'overlay':str(overlay),'scope':'experimental assembly; no TLS native backend yet'}
(root/'validation/biber/assembly.json').write_text(json.dumps(report,indent=2)+'\n')
print('Biber overlay assembled:',overlay)
