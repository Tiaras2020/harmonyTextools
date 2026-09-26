#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/test-resource-management.py"
python3 "$DELIVERY_ROOT/build-support/test-user-resources.py"
