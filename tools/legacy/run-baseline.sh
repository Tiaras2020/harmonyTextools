#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
if [ ! -f "$DELIVERY_ROOT/texstudio-harmony/dependencies.lock.json" ]; then
  python3 "$DELIVERY_ROOT/build-support/audit-baseline.py"
fi
python3 "$DELIVERY_ROOT/build-support/audit-baseline.py" --verify
python3 "$BUILD_REPO/scripts/release_config.py"
python3 "$DELIVERY_ROOT/build-support/regress-baseline.py"
python3 "$DELIVERY_ROOT/build-support/audit-baseline.py" --verify
