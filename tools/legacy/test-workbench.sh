#!/usr/bin/env bash
set -euo pipefail
root=/mnt/e/CodeProjects/harmonytexlive
out="$root/validation/workbench-1.0.33"
printf '<RCC><qresource prefix="/"><file alias="dictionaries/zh_CN.dic">%s</file></qresource></RCC>' "$root/texstudio-harmony/third_party/texstudio/utilities/dictionaries/zh_CN.dic" > "$out/test.qrc"
rcc "$out/test.qrc" -o "$out/test-resource.cpp"
g++ -std=c++17 -fPIC "$root/build-support/test-workbench.cpp" "$out/test-resource.cpp" -I"$root/texstudio-harmony/third_party/texstudio/src" $(pkg-config --cflags --libs Qt5Core) -o "$out/test-workbench"
"$out/test-workbench" | tee "$out/host-tests.log"
