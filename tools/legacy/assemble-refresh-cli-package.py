"""Assemble a full HAP on Windows without slow WSL tiny writes."""
from pathlib import Path
import shutil, zipfile
r=Path(__file__).resolve().parents[1]
hap=r/'artifacts/TeXstudioHarmony-1.0.26-arm64-unsigned.hap'
assert not hap.exists(), 'Archive candidate before rebuilding'
shutil.copy2(r/'validation/refresh-cli-1.0.26/app-core.hap',hap)
with zipfile.ZipFile(hap,'a',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
    assert 'hnp/arm64-v8a/texlive.hnp' not in z.namelist()
    z.write(r/'artifacts/texlive-1.0.21.hnp','hnp/arm64-v8a/texlive.hnp')
print('Full UI HAP assembled; run check-refresh-cli-package.py before signing')
