import hashlib,json
from pathlib import Path
r=Path.cwd();out=r/'validation/workbench-1.0.34';paths=['texstudio-harmony/release.json']+['texstudio-harmony/third_party/texstudio/src/'+f for f in ['harmonyaiworkbench.h','harmonyproofpanel.h','texstudio.cpp','harmonyRelease.h']]
(out/'source-hashes.json').write_text(json.dumps({p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
s=json.loads((r/'validation/device-signing-1.0.34/result.json').read_text());(r/'artifacts/SHA256SUMS-1.0.34.txt').write_text(s['sha256']+'  '+s['signed_file']+'\n'+s['unsigned_sha256']+'  TeXstudioHarmony-1.0.34-arm64-unsigned.hap\n')
