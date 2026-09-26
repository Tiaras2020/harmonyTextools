#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/background-cli-1.0.28"
g++ -std=c++17 -fPIC -I"$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src" "$DELIVERY_ROOT/build-support/test-background-scope.cpp" $(pkg-config --cflags --libs Qt5Widgets Qt5Network) -o "$out/test-scope"
"$out/test-scope" > "$out/scope-tests.log" 2>&1
cat "$out/scope-tests.log"
