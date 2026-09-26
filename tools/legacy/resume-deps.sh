#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
python3 - <<'PY'
from pathlib import Path
p=Path('scripts/texlive/hpk_builds/bzip2/HPKBUILD')
p.write_text(p.read_text().replace('https://github.com/libarchive/bzip2/archive/refs/tags/bzip2-${pkgver}.tar.gz','https://codeload.github.com/libarchive/bzip2/tar.gz/refs/tags/bzip2-${pkgver}'))
PY
cd third_party/lycium
for pkg in bzip2 libpng brotli expat freetype2 graphite2 harfbuzz icu teckit fontconfig; do
  echo "START dependency: $pkg"
  bash build.sh "$pkg"
  test -d "$BUILD_REPO/build/build-hpkbuilds-ohos-install/$pkg/arm64-v8a"
  echo "DONE dependency: $pkg"
done
