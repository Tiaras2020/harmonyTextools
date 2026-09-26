#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
python3 - <<'PY'
from pathlib import Path
p=Path('scripts/texlive/hpk_builds/harfbuzz/HPKBUILD')
s=p.read_text().replace('-DCMAKE_SHARED_LINKER_FLAGS="$extra_libs"','-DCMAKE_C_STANDARD_LIBRARIES="$extra_libs -lm"').replace('-DCMAKE_EXE_LINKER_FLAGS="$extra_libs"','-DCMAKE_CXX_STANDARD_LIBRARIES="$extra_libs -lm"')
p.write_text(s)
p=Path('third_party/lycium/script/build_hpk.sh')
p.write_text(p.read_text().replace('unzip ', 'unzip -o '))
PY
cd third_party/lycium
for pkg in harfbuzz icu teckit fontconfig; do
  echo "START dependency: $pkg"
  bash build.sh "$pkg"
  test -d "$BUILD_REPO/build/build-hpkbuilds-ohos-install/$pkg/arm64-v8a"
  echo "DONE dependency: $pkg"
done
