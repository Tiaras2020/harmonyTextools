#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
bash -n "$BUILD_REPO/scripts/common/build_texlive_hnp.sh"
bash -n "$BUILD_REPO/scripts/texlive/build_pack_texmf.sh"
bash "$DELIVERY_ROOT/build-support/run-baseline.sh"
