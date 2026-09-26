#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
src="$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src"
out="$DELIVERY_ROOT/validation/resources"
g++ -std=c++17 -fPIC -Wall -Wextra -I"$src" \
  "$src/harmonyresources.cpp" "$out/resource-cli.cpp" \
  $(pkg-config --cflags --libs Qt5Core quazip1-qt5) -o "$out/resource-cli"
python3 "$DELIVERY_ROOT/build-support/test-resources.py"
