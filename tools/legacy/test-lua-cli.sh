#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
bash "$DELIVERY_ROOT/build-support/test-resources.sh"
python3 "$DELIVERY_ROOT/build-support/test-lua-user-resources.py"
