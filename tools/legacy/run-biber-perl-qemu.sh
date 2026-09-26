#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
runtime="$BUILD_REPO/build/biber-perl-5.40.3/stage/data/service/hnp/texlive.org/texlive_1.0.18"
export PERL5LIB="$BUILD_REPO/build/biber-runtime/lib:$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux"
exec env LC_ALL=en_US.UTF-8 qemu-aarch64 -L "$BUILD_REPO/build/perl-ohos-5.40.3/qemu-root" "$runtime/bin/perl" "$@"
