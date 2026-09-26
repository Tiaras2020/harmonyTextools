"""Reviewed case-sensitive filesystem adaptation, preserving upstream files."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

runtime=Path(sys.argv[1])
tree=runtime/'texmf'
aliases=[]
for kind in ('tfm','vf','type1'):
    for source in sorted((tree/'fonts'/kind/'public/cmathbb').glob('cmathbb-*')):
        target=source.with_name('C'+source.name[1:])
        if target.exists(): assert target.read_bytes()==source.read_bytes()
        else: shutil.copy2(source,target)
        aliases.append({'source':source.relative_to(tree).as_posix(),'alias':target.relative_to(tree).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
assert aliases, 'cmathbb adaptation has no matching inputs'
(runtime/'font-adaptations.json').write_text(json.dumps({'reason':'Upstream font declaration and virtual font references use uppercase Cmathbb while archive filenames use lowercase cmathbb','aliases':aliases},indent=2)+'\n')
print('Verified font aliases:',len(aliases))
