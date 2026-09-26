#!/usr/bin/env bash
# Historical migration: retained for audit, not a release entry point.
echo 'Historical migration disabled. Use release.json and the current RUNBOOK baseline workflow.' >&2
exit 2
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cp "$DELIVERY_ROOT/texstudio-harmony/texstudio_harmony/AppScope/app.json5" "$BUILD_REPO/texstudio_harmony/AppScope/app.json5"
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/logs/fontconfig-fix-package.log" 2>&1
export PACKAGE_VERSION=1.0.1
python3 "$DELIVERY_ROOT/build-support/finalize-packages.py"