#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
[[ "$PACKAGE_VERSION" == 1.0.19 ]]
python3 "$DELIVERY_ROOT/build-support/prepare-biber-polish.py"
out="$DELIVERY_ROOT/validation/biber/polish-1.0.19"
if ! bash "$out/build.sh"; then
    grep -q 'Your Makefile has been rebuilt' "$out/build.log" || exit 1
    bash "$out/build.sh"
fi
