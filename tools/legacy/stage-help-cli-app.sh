#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
bash "$DELIVERY_ROOT/build-support/build-help-cli.sh"
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/validation/help-cli-1.0.27/package.log" 2>&1
cp "$BUILD_REPO/texstudio_harmony/entry/build/default/outputs/default/entry-default-unsigned.hap" "$DELIVERY_ROOT/validation/help-cli-1.0.27/app-core.hap"
