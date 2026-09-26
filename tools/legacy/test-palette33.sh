#!/usr/bin/env bash
set -euo pipefail
root=/mnt/e/CodeProjects/harmonytexlive
out="$root/validation/workbench-1.0.33"
g++ -std=c++17 -fPIC -DQ_OS_OHOS "$root/build-support/test-palette33.cpp" -I"$root/texstudio-harmony/third_party/texstudio/src" $(pkg-config --cflags --libs Qt5Widgets) -o "$out/test-palette33"
QT_QPA_PLATFORM=offscreen "$out/test-palette33" > "$out/palette-host-tests.log" 2>&1
cat "$out/palette-host-tests.log"
