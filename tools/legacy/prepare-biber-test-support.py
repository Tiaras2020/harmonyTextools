"""Fetch missing pure-Perl test helpers into a separate, non-shipping directory."""
import gzip,hashlib,json,os,pathlib,re,tarfile,urllib.request
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);out=root/'validation/biber'
support=repo/'build/biber-test-support';support.mkdir(exist_ok=True)
index=gzip.decompress((out/'downloads/02packages.details.txt.gz').read_bytes()).decode()
packages={p[0]:p[2] for line in index.split('\n\n',1)[1].splitlines() if len(p:=line.split())==3}
queue=['Test::Exception'];seen=set();records=[]
for module in queue:
    if module in seen or module=='perl':continue
    seen.add(module);relative=module.replace('::','/')+'.pm'
    if any((base/relative).exists() for base in [support,repo/'build/biber-runtime/lib',repo/'build/biber-perl-5.40.3/lib']):continue
    path=packages[module];url='https://www.cpan.org/authors/id/'+path;archive=out/'downloads'/path.rsplit('/',1)[1]
    if not archive.exists():
        with urllib.request.urlopen(url,timeout=90) as r:archive.write_bytes(r.read())
    with tarfile.open(archive) as t:
        names=t.getnames();assert not any(n.endswith('.xs') for n in names),'Native test dependency needs explicit port'
        metas=[n for n in names if n.endswith('/META.json')]
        if metas:meta=json.load(t.extractfile(min(metas,key=lambda n:n.count('/'))))
        else:
            import yaml
            metas=[n for n in names if n.endswith('/META.yml')];meta=yaml.safe_load(t.extractfile(min(metas,key=lambda n:n.count('/')))) if metas else {}
        requires=(meta.get('prereqs',{}).get('runtime',{}).get('requires',{}) or meta.get('requires',{}));queue.extend(requires)
        for member in t.getmembers():
            if not member.isfile():continue
            parts=pathlib.PurePosixPath(member.name).parts
            if len(parts)>2 and parts[1]=='lib':target=support/pathlib.Path(*parts[2:])
            elif len(parts)==2 and member.name.endswith('.pm'):
                data=t.extractfile(member).read();m=re.search(rb'^package\s+([\w:]+)\s*;',data,re.M)
                if not m:continue
                target=support/(m[1].decode().replace('::','/')+'.pm')
            else:continue
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(t.extractfile(member).read())
    records.append({'module':module,'url':url,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'requirements':requires})
lock=out/'test-support.lock.json';previous=json.loads(lock.read_text()) if lock.exists() else []
by_url={r['url']:r for r in previous+records};lock.write_text(json.dumps(list(by_url.values()),indent=2)+'\n')
print('Non-shipping test helper archives:',len(by_url))
