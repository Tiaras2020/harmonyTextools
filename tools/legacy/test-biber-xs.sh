#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
work="$BUILD_REPO/build/biber-perl-5.40.3"
runtime="$work/stage/data/service/hnp/texlive.org/texlive_1.0.18"
qroot="$BUILD_REPO/build/perl-ohos-5.40.3/qemu-root"
export PERL5LIB="$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux"
LC_ALL=en_US.UTF-8 qemu-aarch64 -L "$qroot" "$runtime/bin/perl" "$DELIVERY_ROOT/validation/biber/xs-smoke.pl" > "$DELIVERY_ROOT/validation/biber/xs-bootstrap/qemu-result.json" 2> "$DELIVERY_ROOT/validation/biber/xs-bootstrap/qemu.stderr"
test ! -s "$DELIVERY_ROOT/validation/biber/xs-bootstrap/qemu.stderr"
cat "$DELIVERY_ROOT/validation/biber/xs-bootstrap/qemu-result.json"
