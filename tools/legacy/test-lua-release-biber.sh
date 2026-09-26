#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export BIBER_RUNTIME="$BUILD_REPO/build/biber-perl-1.0.20/stage/data/service/hnp/texlive.org/texlive_1.0.20"
export BIBER_OVERLAY="$BUILD_REPO/build/biber-runtime-1.0.19"
export BIBER_TEST_OUT="$DELIVERY_ROOT/validation/luahbtex/perl"
export BIBER_TEST_CASE="$BUILD_REPO/build/biber-workflow-1.0.20/中文 文献测试"
python3 "$DELIVERY_ROOT/build-support/test-biber-dependencies.py"
python3 "$DELIVERY_ROOT/build-support/test-biber-workflow.py"
export PERL5LIB="$BIBER_OVERLAY/lib:$BIBER_RUNTIME/lib/perl5/5.40.3:$BIBER_RUNTIME/lib/perl5/5.40.3/aarch64-linux"
env LC_ALL=en_US.UTF-8 qemu-aarch64 -L "$BUILD_REPO/build/perl-ohos-5.40.3/qemu-root" "$BIBER_RUNTIME/bin/perl" "$DELIVERY_ROOT/validation/biber/runtime-data-smoke.pl" > "$BIBER_TEST_OUT/runtime-data-result.json"
