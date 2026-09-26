#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export HARMONY_COMMON_IMPORT=1
if [[ "${1:-}" == --resume-verified ]]; then export HARMONY_RESUME_IMPORT=1; fi
python3 "$DELIVERY_ROOT/build-support/test-full-import.py"
