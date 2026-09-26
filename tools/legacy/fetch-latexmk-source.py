"""Use the same pinned TeX Live catalogue for the executable latexmk script."""
import json
import lzma
import os
from pathlib import Path
import sys
import tarfile
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'texstudio-harmony/scripts/texlive'))
from full_resources import read_database,download,digest
metadata=root/'validation/full-resources/texlive.tlpdb.xz'
policy=json.loads((root/'texstudio-harmony/scripts/texlive/resource-policy.json').read_text())
assert digest(metadata)==policy['metadataSha256']
db=read_database(lzma.decompress(metadata.read_bytes()).decode())
cache=Path(os.environ['BUILD_REPO'])/'build/full-resources-cache/archives'
archive=download('latexmk',db['latexmk'],cache,policy['repository'])
out=root/'validation/latexmk'
with tarfile.open(archive,'r:xz') as t:
    matches=[m for m in t.getmembers() if m.name.endswith('/latexmk.pl') and m.isfile()]
    assert len(matches)==1
    (out/'latexmk.pl').write_bytes(t.extractfile(matches[0]).read())
(out/'latexmk-source.json').write_text(json.dumps({'revision':db['latexmk']['revision'],'archiveSha512':digest(archive,'sha512'),'scriptSha256':digest(out/'latexmk.pl'),'metadataSha256':digest(metadata)},indent=2)+'\n')
print('Pinned latexmk script extracted and verified')
