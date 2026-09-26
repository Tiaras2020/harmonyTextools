#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export JOBS=3
cd "$BUILD_REPO/third_party/lycium"
for pkg in zlib bzip2 libpng brotli expat freetype2 graphite2 harfbuzz icu teckit fontconfig; do
  echo "START dependency: $pkg"
  bash build.sh "$pkg"
  test -d "$BUILD_REPO/build/build-hpkbuilds-ohos-install/$pkg/arm64-v8a"
  echo "DONE dependency: $pkg"
done
