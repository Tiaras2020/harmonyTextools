#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/crash-fix-1.0.30"
mkdir -p "$out/engines"
for name in xetex pdftex; do
  test -e "$out/engines/$name-before" || cp "$BUILD_REPO/build/build-texlive-ohos/texk/web2c/$name" "$out/engines/$name-before"
done
python3 "$DELIVERY_ROOT/texstudio-harmony/scripts/texlive/patch_dump_io.py" "$BUILD_REPO/build/src/texlive-source"
cd "$BUILD_REPO/build/build-texlive-ohos/texk/web2c"
make -j4 pdftex xetex > "$out/engine-build.log" 2>&1
for name in xetex pdftex; do
  cp "$name" "$out/engines/$name"
done
echo 'pdfTeX and XeTeX built with descriptor ownership repair'
