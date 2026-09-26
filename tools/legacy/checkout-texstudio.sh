#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
git -C "$BUILD_REPO/build/texstudio-git" -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=45 fetch --depth 1 origin efc191c5d66ffcd0ca3b41b05b4f83a279b184ae
git -C "$BUILD_REPO/build/texstudio-git" checkout --detach efc191c5d66ffcd0ca3b41b05b4f83a279b184ae
rsync -a --exclude=.git "$BUILD_REPO/build/texstudio-git/" "$BUILD_REPO/third_party/texstudio/"
rsync -a --exclude=.git "$DELIVERY_ROOT/texstudio-harmony/third_party/poppler/" "$BUILD_REPO/third_party/poppler/"
find "$BUILD_REPO/third_party/texstudio" "$BUILD_REPO/third_party/poppler" -name AGENTS.md -print
