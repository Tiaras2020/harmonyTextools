#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
work="$BUILD_REPO/build/perl-ohos-5.40.3"
runtime="$work/stage/data/service/hnp/texlive.org/texlive_1.0.17"
export PERL5LIB="$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux"
export LC_ALL=C
mkdir -p "$work/qemu-root/lib"
cp "$DELIVERY_ROOT/validation/latexmk/device-libc.so" "$work/qemu-root/lib/ld-musl-aarch64.so.1"
ln -sf ld-musl-aarch64.so.1 "$work/qemu-root/lib/libc.so"
qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" -v
qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" "$DELIVERY_ROOT/validation/latexmk/latexmk.pl" -v
qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" "$DELIVERY_ROOT/validation/latexmk/perl-smoke.pl" > "$DELIVERY_ROOT/validation/latexmk/qemu-result.json"
cat "$DELIVERY_ROOT/validation/latexmk/qemu-result.json"
cd "$work"
for loc in C C.UTF-8 en_US.UTF-8; do
    LC_ALL="$loc" qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" "$DELIVERY_ROOT/validation/latexmk/locale-test.pl" \
      > "$DELIVERY_ROOT/validation/latexmk/locale-$loc.json" 2> "$DELIVERY_ROOT/validation/latexmk/locale-$loc.stderr"
    test ! -s "$DELIVERY_ROOT/validation/latexmk/locale-$loc.stderr"
done
