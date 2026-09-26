#!/usr/bin/env bash
set -euo pipefail
root=/mnt/e/CodeProjects/harmonytexlive
out="$root/validation/network-1.0.31"
g++ -std=c++17 -fPIC "$root/build-support/test-network.cpp" -I"$root/texstudio-harmony/third_party/texstudio/src" $(pkg-config --cflags --libs Qt5Core Qt5Network Qt5Widgets) -o "$out/test-network"
"$out/test-network" | tee "$out/host-tests.log"
