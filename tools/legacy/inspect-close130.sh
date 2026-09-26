#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/close-audit-1.0.30"
mkdir -p "$out"
bin="$BUILD_REPO/build/build-texstudio-ohos/libtexstudio.so"
find "$BUILD_REPO/build/build-texstudio-ohos" -maxdepth 2 -name 'libtexstudio.so' > "$out/binary-paths.txt"
"$NATIVE_OHOS_SDK/llvm/bin/llvm-objdump" -d --start-address=0x1e1a380 --stop-address=0x1e1a438 "$bin" > "$out/requestClose-disassembly.txt"
"$NATIVE_OHOS_SDK/llvm/bin/llvm-objdump" -d --start-address=0x2038300 --stop-address=0x2038370 "$bin" > "$out/currentChanged-disassembly.txt"
