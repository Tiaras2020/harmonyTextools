#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/crash-fix-1.0.30"
"$NATIVE_OHOS_SDK/llvm/bin/llvm-objdump" -d --start-address=0x432d0 --stop-address=0x43300 "$out/engines/xetex-before" > "$out/format-close-disassembly.txt"
grep -R -n 'fdsan_set_error_level\|FDSAN_ERROR_LEVEL_FATAL' "$NATIVE_OHOS_SDK/sysroot/usr/include" | head -15
"$NATIVE_OHOS_SDK/llvm/bin/llvm-nm" "$out/engines/xetex" | grep 'harmony_dump_open'
"$NATIVE_OHOS_SDK/llvm/bin/llvm-nm" "$out/engines/pdftex" | grep 'harmony_dump_open'
