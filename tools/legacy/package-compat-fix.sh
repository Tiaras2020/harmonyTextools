#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/prepare-compat-release.py" stage
bash "$DELIVERY_ROOT/build-support/package-resource-release.sh"
