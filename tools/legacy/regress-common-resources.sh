#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export HARMONY_TEST_DIST="$BUILD_REPO/build/full-runtime-v2"
export HARMONY_TEST_OUTPUT="$DELIVERY_ROOT/validation/common-resources/regression"
export HARMONY_COMMON_FIXTURES="$DELIVERY_ROOT/validation/common-resources/fixtures"
export HARMONY_EXTRA_FIXTURES="$DELIVERY_ROOT/validation/full-resources/fixtures"
python3 "$DELIVERY_ROOT/build-support/regress-baseline.py"
