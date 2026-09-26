#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/prepare-crash-release.py"
unset PACKAGE_VERSION
source "$DELIVERY_ROOT/build-support/env.sh"
out="$DELIVERY_ROOT/validation/crash-fix-1.0.30"
if ! bash "$out/perl/build.sh"; then
  grep -q 'Your Makefile has been rebuilt' "$out/perl/build.log" || exit 1
  bash "$out/perl/build.sh"
fi
for name in latexmk biber; do
  "$NATIVE_OHOS_SDK/llvm/bin/clang" --target=aarch64-linux-ohos --sysroot="$NATIVE_OHOS_SDK/sysroot" -O2 -Wall -Wextra -Werror '-DHARMONY_RUNTIME_ROOT="/data/service/hnp/texlive.org/texlive_1.0.30"' "$DELIVERY_ROOT/texstudio-harmony/scripts/texlive/${name}_launcher.c" -o "$out/engines/$name"
done
echo 'New runtime prefix and launchers built'
