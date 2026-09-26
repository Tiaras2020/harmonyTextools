"""Fetch pinned upstream source archives for the B3.1 cross-build."""
import hashlib
import json
from pathlib import Path
import urllib.request

root=Path(__file__).resolve().parents[1]
out=root/'validation/latexmk'; out.mkdir(exist_ok=True)
cache=out/'downloads';cache.mkdir(exist_ok=True)
urls={
 'perl-5.40.3.tar.xz':'https://www.cpan.org/src/5.0/perl-5.40.3.tar.xz',
 'perl-5.40.3.tar.xz.sha256.txt':'https://www.cpan.org/src/5.0/perl-5.40.3.tar.xz.sha256.txt',
 'perl-cross-1.6.4.tar.gz':'https://github.com/arsv/perl-cross/releases/download/1.6.4/perl-cross-1.6.4.tar.gz',
}
for name,url in urls.items():
    path=cache/name
    if not path.exists():
        with urllib.request.urlopen(url,timeout=90) as stream: data=stream.read()
        path.write_bytes(data)
    print('Fetched',name,path.stat().st_size,flush=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(cache/'perl-cross-1.6.4.tar.gz')=='b6202173b0a8a43fb312867d85a8cd33527f3f234b1b6e591cdaa9895c9920c7'
assert sha(cache/'perl-5.40.3.tar.xz') in (cache/'perl-5.40.3.tar.xz.sha256.txt').read_text()
(out/'sources.json').write_text(json.dumps({n:{'url':u,'sha256':sha(cache/n)} for n,u in urls.items()},indent=2)+'\n')
