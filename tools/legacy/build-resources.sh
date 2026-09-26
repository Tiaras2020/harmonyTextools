#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$DELIVERY_ROOT/validation/resources"
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
pkg-config --modversion Qt5Core || true
find "$BUILD_REPO/build/src" -name 'qstandardpaths*ohos*' -o -name '*filedialog*ohos*' > "$DELIVERY_ROOT/validation/resources/qt-path-sources.txt"
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j6 > "$DELIVERY_ROOT/validation/resources/build.log" 2>&1
echo 'Resource manager ARM64 build passed'
