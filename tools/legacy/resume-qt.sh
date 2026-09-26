#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$BUILD_REPO/.build-tools"
ln -sfn /usr/bin/python3 "$BUILD_REPO/.build-tools/python"
cd "$BUILD_REPO/build/build-qt-ohos"
make -j"$JOBS"
make install
printf 'Qt build and installation complete.\n'
