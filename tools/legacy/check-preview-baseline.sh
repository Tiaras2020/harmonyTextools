#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
host="$BUILD_REPO/build/build-poppler-preview-host"
out="$DELIVERY_ROOT/validation/baseline/preview"
mkdir -p "$out"
test -x "$host/probe-preview"
"$host/probe-preview" "$DELIVERY_ROOT/validation/cjk-rendering/device-original.pdf" \
  "$BUILD_REPO/build/build-texlive-ohos-dist/share/poppler" "$out/cjk.ppm" > "$out/render.log" 2>&1
if grep -E 'Missing language pack|Unknown font' "$out/render.log"; then exit 1; fi
echo 'Same-version Poppler baseline rendering passed'
