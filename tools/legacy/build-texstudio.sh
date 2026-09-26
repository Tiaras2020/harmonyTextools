#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
for module in qtsvg qtdeclarative qttools qtohosextras qtmultimedia; do
  make -C "build/build-qt-ohos/$module" install
done
bash scripts/texstudio/build_texstudio.sh
