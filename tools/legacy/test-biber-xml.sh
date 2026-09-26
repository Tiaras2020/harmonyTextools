#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
work="$BUILD_REPO/build/biber-perl-5.40.3"
runtime="$work/stage/data/service/hnp/texlive.org/texlive_1.0.18"
export PERL5LIB="$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux"
LC_ALL=en_US.UTF-8 qemu-aarch64 -L "$BUILD_REPO/build/perl-ohos-5.40.3/qemu-root" "$runtime/bin/perl" "$DELIVERY_ROOT/validation/biber/xml-smoke.pl" > "$DELIVERY_ROOT/validation/biber/xs-bootstrap/xml-result.json" 2> "$DELIVERY_ROOT/validation/biber/xs-bootstrap/xml.stderr"
test ! -s "$DELIVERY_ROOT/validation/biber/xs-bootstrap/xml.stderr"
cat "$DELIVERY_ROOT/validation/biber/xs-bootstrap/xml-result.json"
