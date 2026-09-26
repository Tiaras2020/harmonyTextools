#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/verify-latexmk-payload.py"
