"""Extract locked dependencies for isolated Biber runtime assembly."""
import hashlib,json,os,pathlib,tarfile
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO'])
work=repo/'build/biber-deps';work.mkdir(exist_ok=True)
lock=json.loads((root/'validation/biber/dependencies.lock.json').read_text())
for record in lock['distributions']:
    archive=root/'validation/biber/downloads'/record['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==record['sha256'],archive
    dest=work/record['distribution']
    if dest.exists():continue
    dest.mkdir()
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            parts=pathlib.PurePosixPath(m.name).parts
            if len(parts)<2:continue
            m.name=str(pathlib.PurePosixPath(*parts[1:]));t.extract(m,dest,filter='data')
print('Extracted',len(lock['distributions']),'verified archives to',work)
out=root/'validation/biber/remaining-build-inputs.txt'
with out.open('w') as f:
    for record in lock['distributions']:
        if record['containsXS'] or record['distribution'].startswith('Encode-'):
            dest=work/record['distribution'];f.write('\n===== '+dest.name+' =====\n')
            for name in ('Makefile.PL','Build.PL'):
                p=dest/name
                if p.exists():f.write(p.read_text(errors='replace')+'\n')
