#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
for f in "$BUILD_REPO/scripts/common/build_texlive_hnp.sh" "$BUILD_REPO/scripts/texlive/build_pack_texmf.sh" "$DELIVERY_ROOT/build-support/"*.sh; do
  bash -n "$f"
done
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j6 > "$DELIVERY_ROOT/validation/baseline/texstudio-build.log" 2>&1
echo 'TeXstudio incremental ARM64 build passed'
