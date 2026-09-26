#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
"$NATIVE_OHOS_SDK/llvm/bin/llvm-addr2line" -f -C -e "$BUILD_REPO/build/build-texlive-ohos/texk/web2c/xetex" 0x432f0 0x30888
"$NATIVE_OHOS_SDK/llvm/bin/llvm-addr2line" -f -C -e "$BUILD_REPO/build/build-hpkbuilds-ohos-install/zlib/arm64-v8a/lib/libz.so.1" 0x23a20 0x21158
df -h / /mnt/e
