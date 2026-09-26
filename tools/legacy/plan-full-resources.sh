#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/texstudio-harmony/scripts/texlive/full_resources.py" \
  --metadata "$DELIVERY_ROOT/validation/full-resources/texlive.tlpdb.xz" \
  --baseline-cache "$BUILD_REPO/build/build-texlive-ohos-dist/.tlpkg-cache" \
  --report "$DELIVERY_ROOT/validation/full-resources/plan.json" "$@"
