#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
test "$PACKAGE_VERSION" = 1.0.22
test "$(python3 "$BUILD_REPO/scripts/release_config.py" --field runtimeVersion)" = 1.0.21
# The accepted HNP is reused byte for byte; do not rebuild or overwrite it.
python3 - <<'PY'
import hashlib, os, pathlib
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(8*1024*1024): h.update(block)
    return h.digest()
assert digest(pathlib.Path(os.environ['BUILD_REPO'])/'build/texlive.hnp') == digest(pathlib.Path(os.environ['DELIVERY_ROOT'])/'artifacts/texlive-1.0.21.hnp')
print('Accepted runtime SHA256 verified',flush=True)
PY
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/validation/ui-polish-1.0.22/package.log" 2>&1
python3 "$DELIVERY_ROOT/build-support/finalize-packages.py"
