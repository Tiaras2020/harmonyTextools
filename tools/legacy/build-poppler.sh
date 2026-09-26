#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
make -C build/build-qt-ohos/qtbase install
bash scripts/poppler/build_poppler.sh
