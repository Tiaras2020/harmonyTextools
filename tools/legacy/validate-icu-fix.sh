#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
host="$BUILD_REPO/build/build-hpkbuilds-ohos/icu/host-build"
out="$DELIVERY_ROOT/validation/icu-fix"
mkdir -p "$out"
# Use ICU's empty data stub first, so bundled host data cannot mask the bug.
export LD_LIBRARY_PATH="$host/stubdata:$host/lib"
ICU_DATA="$out/missing" python3 "$DELIVERY_ROOT/build-support/probe-icu-converters.py" failure > "$out/missing-data.json"
ICU_DATA="$out" python3 "$DELIVERY_ROOT/build-support/probe-icu-converters.py" success > "$out/with-data.json"
printf 'ICU negative control and three converter checks passed\n'
