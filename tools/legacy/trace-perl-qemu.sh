#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
work="$BUILD_REPO/build/perl-ohos-5.40.3"
export LC_ALL=C
ulimit -c 0
printf 'print "FILE OK\\n";\n' > "$work/smoke.pl"
qemu-aarch64 -strace -L "$work/qemu-root" "$work/perl" "$work/smoke.pl" > "$DELIVERY_ROOT/validation/latexmk/qemu-trace.log" 2>&1
