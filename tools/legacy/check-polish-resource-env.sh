#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
src="$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src"
out="$DELIVERY_ROOT/validation/biber/polish-1.0.19"
g++ -std=c++17 -fPIC -Wall -Wextra -I"$src" "$src/harmonyresources.cpp" "$DELIVERY_ROOT/validation/resources/resource-cli.cpp" $(pkg-config --cflags --libs Qt5Core quazip1-qt5) -o "$out/resource-cli"
python3 "$DELIVERY_ROOT/build-support/check-polish-resource-env.py"
