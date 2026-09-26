#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/lua-cli-1.0.23"
g++ -std=c++17 -fPIC -Wall -Wextra -I"$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src" "$DELIVERY_ROOT/build-support/test-automation.cpp" $(pkg-config --cflags --libs Qt5Core Qt5Network) -o "$out/test-automation"
python3 "$DELIVERY_ROOT/build-support/test-automation.py"
