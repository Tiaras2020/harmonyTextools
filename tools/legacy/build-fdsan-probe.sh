#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
"$NATIVE_OHOS_SDK/llvm/bin/clang" --target=aarch64-linux-ohos --sysroot="$NATIVE_OHOS_SDK/sysroot" -fPIC -shared -Wall -Werror "$DELIVERY_ROOT/build-support/fdsan-fatal-probe.c" -o "$DELIVERY_ROOT/validation/crash-fix-1.0.30/engines/libstrictfdsan.so"
