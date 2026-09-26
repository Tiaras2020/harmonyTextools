#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
perl -I "$DELIVERY_ROOT/texstudio-harmony/scripts/texlive" "$DELIVERY_ROOT/validation/latexmk/test-harmony-cwd.pl" > "$DELIVERY_ROOT/validation/latexmk/cwd-tests.txt"
python3 "$DELIVERY_ROOT/build-support/test-latexmk-launcher.py"
