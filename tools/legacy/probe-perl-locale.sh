#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
work="$BUILD_REPO/build/perl-ohos-5.40.3"
runtime="$work/stage/data/service/hnp/texlive.org/texlive_1.0.17"
export PERL5LIB="$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux"
"$NATIVE_OHOS_SDK/llvm/bin/clang" --target=aarch64-linux-ohos --sysroot="$NATIVE_OHOS_SDK/sysroot" "$DELIVERY_ROOT/validation/latexmk/locale-probe.c" -o "$work/locale-probe"
qemu-aarch64 -L "$work/qemu-root" "$work/locale-probe"
for loc in C C.UTF-8 en_US.UTF-8; do
    echo "Testing $loc"
    LC_ALL="$loc" qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" -MPOSIX -e 'print POSIX::setlocale(LC_ALL),qq(\n);'
done
