#!/usr/bin/env bash
set -euo pipefail
root=/mnt/e/CodeProjects/harmonytexlive
out="$root/validation/workbench-1.0.33"
python3 "$root/build-support/prepare-ui33-test.py"
g++ -std=c++17 -fPIC "$root/build-support/test-ui33.cpp" -I"$out" -I"$root/texstudio-harmony/third_party/texstudio/src" $(pkg-config --cflags --libs Qt5Widgets Qt5Network) -o "$out/test-ui33"
QT_QPA_PLATFORM=offscreen "$out/test-ui33" > "$out/ui-host-tests.log" 2>&1
cat "$out/ui-host-tests.log"
