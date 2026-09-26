#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/crash-fix-1.0.30"
g++ -std=c++17 -fPIC -I"$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src" "$DELIVERY_ROOT/build-support/test-crash-paths.cpp" $(pkg-config --cflags --libs Qt5Widgets Qt5Network) -o "$out/test-paths"
"$out/test-paths" > "$out/path-tests.log" 2>&1
bash "$DELIVERY_ROOT/build-support/test-dump-io.sh" > "$out/dump-tests.log" 2>&1
cat "$out/path-tests.log" "$out/dump-tests.log"
