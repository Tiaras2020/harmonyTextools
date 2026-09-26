#!/usr/bin/env python3
from pathlib import Path
import json,zipfile,shutil,hashlib
r=Path(__file__).resolve().parents[1];version=json.loads((r/'release.json').read_text());v=version['version']
core=r/'texstudio_harmony/entry/build/default/outputs/default/entry-default-unsigned.hap'
runtime=r/'build/downloads'/('texlive-'+version['runtimeVersion']+'.hnp')
out=r/'dist'/('TeXstudioHarmony-'+v+'-arm64-unsigned.hap');out.parent.mkdir(exist_ok=True)
if out.exists():raise SystemExit('Output exists; increment version or explicitly move previous artifact: '+str(out))
assert core.is_file() and runtime.is_file(),'Build core and restore runtime first'
shutil.copyfile(core,out)
with zipfile.ZipFile(out,'a',compression=zipfile.ZIP_STORED) as z:
 assert 'hnp/arm64-v8a/texlive.hnp' not in z.namelist()
 z.write(runtime,'hnp/arm64-v8a/texlive.hnp')
print('Unsigned package:',out)
