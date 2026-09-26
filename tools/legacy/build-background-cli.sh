#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$DELIVERY_ROOT/validation/background-cli-1.0.28"
python3 "$DELIVERY_ROOT/build-support/generate-cli-help.py"
python3 "$DELIVERY_ROOT/texstudio-harmony/scripts/release_config.py" --write
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j4 > "$DELIVERY_ROOT/validation/background-cli-1.0.28/app-build.log" 2>&1
echo 'UI application build passed'
