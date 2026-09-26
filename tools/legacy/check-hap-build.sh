#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/configure-project.py"
cd "$BUILD_REPO/texstudio_harmony"
ohpm install
hvigorw --mode module -p module=entry@default -p product=default -p requiredDeviceType=2in1 assembleHap --no-daemon
