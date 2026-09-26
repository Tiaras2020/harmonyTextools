#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
work="$BUILD_REPO/build/perl-ohos-5.40.3"
runtime="$work/stage/data/service/hnp/texlive.org/texlive_1.0.15"
export LC_ALL=C PERL5LIB="$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux"
qemu-aarch64 -g 12349 -L "$work/qemu-root" "$work/perl" -MConfig -e 'print "OK\n"' &
debug_pid=$!
trap 'kill "$debug_pid" 2>/dev/null || true' EXIT
"$NATIVE_OHOS_SDK/llvm/bin/lldb" --batch "$work/perl" -o 'gdb-remote 12349' -o continue -k 'thread backtrace' -k 'register read pc x0 x1 x2 x24' -k 'disassemble -n Perl_scan_str' > "$DELIVERY_ROOT/validation/latexmk/backtrace.log" 2>&1
