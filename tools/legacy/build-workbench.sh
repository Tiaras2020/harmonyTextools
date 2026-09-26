#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/workbench-1.0.36"
python3 "$DELIVERY_ROOT/texstudio-harmony/scripts/release_config.py" --write
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j4 > "$out/app-build.log" 2>&1
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$out/package.log" 2>&1
cp "$BUILD_REPO/texstudio_harmony/entry/build/default/outputs/default/entry-default-unsigned.hap" "$out/app-core.hap"
echo 'Workbench app core built and packaged'
