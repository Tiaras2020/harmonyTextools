#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$BUILD_REPO/build/downloads"
cd "$BUILD_REPO/build/downloads"
curl -fL --retry 3 --connect-timeout 30 --max-time 600 https://codeload.github.com/baitianyu-kun/texstudio/tar.gz/efc191c5d66ffcd0ca3b41b05b4f83a279b184ae -o texstudio-efc191c5.tar.gz
sha256sum texstudio-efc191c5.tar.gz
tar -xzf texstudio-efc191c5.tar.gz --strip-components=1 -C "$BUILD_REPO/third_party/texstudio"
rsync -a --exclude=.git "$DELIVERY_ROOT/texstudio-harmony/third_party/poppler/" "$BUILD_REPO/third_party/poppler/"
find "$BUILD_REPO/third_party" -name AGENTS.md -print
