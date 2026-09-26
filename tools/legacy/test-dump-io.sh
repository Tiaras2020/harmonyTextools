#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/baseline/fdsan"
mkdir -p "$out"
header="$DELIVERY_ROOT/texstudio-harmony/scripts/texlive/patches"
testsource="$DELIVERY_ROOT/validation/baseline/test-dump-io.c"
gcc -Wall -Wextra -Werror -include stdlib.h -I"$header" "$testsource" -lz -o "$out/test-host"
(cd "$out" && ./test-host) > "$out/host-result.txt"
"$NATIVE_OHOS_SDK/llvm/bin/clang" --target=aarch64-linux-ohos --sysroot="$NATIVE_OHOS_SDK/sysroot" \
  -Wall -Wextra -Werror -include stdlib.h -I"$header" \
  -I"$BUILD_REPO/build/build-hpkbuilds-ohos-install/zlib/arm64-v8a/include" \
  "$testsource" "$BUILD_REPO/build/build-hpkbuilds-ohos-install/zlib/arm64-v8a/lib/libz.a" -o "$out/test-ohos"
cat "$out/host-result.txt"
g++ -Wall -Wextra -Werror -include stdlib.h -I"$header" "$testsource" -lz -o "$out/test-host-cpp"
(cd "$out" && ./test-host-cpp) > "$out/host-cpp-result.txt"
mkdir -p "$out/staged-source/texk/web2c"
if [ ! -f "$out/staged-source/texk/web2c/texmfmp.h" ]; then
  cp "$BUILD_REPO/build/src/texlive-source/texk/web2c/texmfmp.h" "$out/staged-source/texk/web2c/texmfmp.h"
fi
python3 "$DELIVERY_ROOT/texstudio-harmony/scripts/texlive/patch_dump_io.py" "$out/staged-source"
python3 "$DELIVERY_ROOT/texstudio-harmony/scripts/texlive/patch_dump_io.py" "$out/staged-source"
