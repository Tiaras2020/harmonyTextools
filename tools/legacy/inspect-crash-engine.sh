#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
tool="$NATIVE_OHOS_SDK/llvm/bin"
engine="$BUILD_REPO/build/build-texlive-ohos/texk/web2c/xetex"
"$tool/llvm-objdump" -d --start-address=0x43290 --stop-address=0x43320 "$engine"
rg -n 'gzdopen|gzclose|harmony_dump_open' "$BUILD_REPO/build/src/texlive-source/texk/web2c/texmfmp.h"
find "$BUILD_REPO/build" -maxdepth 3 -name '*texstudio*' -type d
