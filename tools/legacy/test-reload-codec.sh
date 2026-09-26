#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/reload-cli-1.0.29"
mkdir -p "$out"
g++ -std=c++17 -fPIC -I"$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src" "$DELIVERY_ROOT/build-support/test-reload-codec.cpp" $(pkg-config --cflags --libs Qt5Core) -o "$out/test-codec"
"$out/test-codec" > "$out/codec-tests.log" 2>&1
cat "$out/codec-tests.log"
