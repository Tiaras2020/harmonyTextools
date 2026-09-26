"""Preserve the unsigned pre-audit draft and rebuild it from the corrected stage."""
import hashlib, os, shutil, subprocess
from pathlib import Path
repo = Path(os.environ['BUILD_REPO'])
root = Path(os.environ['DELIVERY_ROOT'])
assert not (root / 'artifacts/TeXstudioHarmony-1.0.20-arm64-device-signed.hap').exists()
archive = root / 'validation/luahbtex/pre-audit-draft'
archive.mkdir()
for name in ('texlive-1.0.20.hnp', 'TeXstudioHarmony-1.0.20-arm64-unsigned.hap', 'package-check-1.0.20.json', 'SHA256SUMS-1.0.20.txt'):
    source = root / 'artifacts' / name
    source.resolve().relative_to(root.resolve())
    shutil.move(source, archive / name)
candidate = repo / 'build/resource-release-1.0.20'
stage = repo / 'build/build-texlive-ohos-hnp'
shutil.copy2(candidate / 'bin/luajithbtex', stage / 'bin/luajithbtex')
for rel in ('bin/luajithbtex', 'bin/luahbtex', 'bin/lualatex', 'texmf/web2c/luahbtex/lualatex.fmt'):
    assert hashlib.sha256((stage / rel).read_bytes()).digest() == hashlib.sha256((candidate / rel).read_bytes()).digest()
tool = Path(os.environ['TOOL_HOME']) / 'sdk/default/openharmony/toolchains/hnpcli'
subprocess.run([str(tool), 'pack', '-i', str(stage), '-o', str(repo / 'build'), '-n', 'texlive', '-v', '1.0.20'], check=True)
subprocess.run(['python3', str(root / 'build-support/finalize-packages.py')], check=True)
