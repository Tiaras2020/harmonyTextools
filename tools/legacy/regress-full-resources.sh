#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export HARMONY_TEST_DIST="$BUILD_REPO/build/full-runtime-v1"
export HARMONY_TEST_OUTPUT="$DELIVERY_ROOT/validation/full-resources/regression"
export HARMONY_EXTRA_FIXTURES="$DELIVERY_ROOT/validation/full-resources/fixtures"
mktexlsr "$HARMONY_TEST_DIST/texmf"
python3 "$DELIVERY_ROOT/build-support/regress-baseline.py"
