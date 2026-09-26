#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$DELIVERY_ROOT/validation/project-cli-1.0.25"
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j4 > "$DELIVERY_ROOT/validation/project-cli-1.0.25/app-build.log" 2>&1
echo 'UI application build passed'
