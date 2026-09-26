#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
"$NATIVE_OHOS_SDK/llvm/bin/llvm-addr2line" -f -C -e "$BUILD_REPO/build/build-texlive-ohos/texk/web2c/pdftex" 0xc17a0 0xadea8
grep -R -n 'gzdopen' "$BUILD_REPO/build/src/texlive-source/texk/web2c" --include='*.c' --include='*.h' --include='*.ch' --include='*.web' | head -35