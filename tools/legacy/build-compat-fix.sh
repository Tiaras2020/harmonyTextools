#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/compat-fix-1.0.21"
python3 "$DELIVERY_ROOT/build-support/prepare-compat-release.py" prepare
if ! bash "$out/perl/build.sh"; then
    grep -q 'Your Makefile has been rebuilt' "$out/perl/build.log" || exit 1
    bash "$out/perl/build.sh"
fi
bash "$out/perl/test.sh"
python3 "$DELIVERY_ROOT/build-support/prepare-compat-release.py" stage
