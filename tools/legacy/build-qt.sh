#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
if [ ! -d build/src/qt-harmonyos-5.12.12 ]; then
  mv build/src/qt-harmonyos-src-5.12.12 build/src/qt-harmonyos-5.12.12
fi
bash scripts/qt/patch_qt.sh
bash -o pipefail scripts/qt/build_qt.sh
