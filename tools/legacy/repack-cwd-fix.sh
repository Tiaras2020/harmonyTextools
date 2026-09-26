#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
bash "$DELIVERY_ROOT/build-support/test-harmony-cwd.sh"
python3 - <<'PY'
import hashlib,json,os,pathlib,shutil
root=pathlib.Path(os.environ['DELIVERY_ROOT']); repo=pathlib.Path(os.environ['BUILD_REPO'])
source=root/'texstudio-harmony/scripts/texlive/HarmonyCwd.pm'
target=repo/'build/resource-release-1.0.16/share/latexmk/HarmonyCwd.pm'
assert target.is_file()
shutil.copy2(source,target)
p=root/'validation/latexmk/payload.json'; d=json.loads(p.read_text())
assert d['version']=='1.0.16'
d['files']['share/latexmk/HarmonyCwd.pm']={'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
p.write_text(json.dumps(d,indent=2)+'\n')
PY
export TEXLIVE_DIST_DIR="$BUILD_REPO/build/resource-release-$PACKAGE_VERSION"
cd "$BUILD_REPO"
bash scripts/common/build_texlive_hnp.sh > "$DELIVERY_ROOT/validation/resources/hnp.log" 2>&1
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/validation/resources/hap.log" 2>&1
python3 "$DELIVERY_ROOT/build-support/finalize-packages.py"
