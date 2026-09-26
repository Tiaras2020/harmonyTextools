#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/project-cli-1.0.25"
g++ -std=c++17 -fPIC -I"$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src" "$out/test-project.cpp" $(pkg-config --cflags --libs Qt5Widgets Qt5Network) -o "$out/test-project"
"$out/test-project" > "$out/host-tests.log" 2>&1
cat "$out/host-tests.log"
g++ -std=c++17 -fPIC -I"$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src" "$DELIVERY_ROOT/build-support/test-automation.cpp" $(pkg-config --cflags --libs Qt5Core Qt5Network) -o "$out/test-automation"
python3 "$DELIVERY_ROOT/build-support/test-project-transport.py"
