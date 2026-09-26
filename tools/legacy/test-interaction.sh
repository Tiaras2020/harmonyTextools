#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
bash "$DELIVERY_ROOT/build-support/test-resources.sh"
python3 "$DELIVERY_ROOT/build-support/test-resource-merge.py"
src="$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src"
for name in harmonyuserresourcesdialog harmonyresourcesdialog; do
  g++ -std=c++17 -fPIC -fsyntax-only -I"$src" $(pkg-config --cflags Qt5Widgets Qt5Concurrent Qt5PrintSupport Qt5Xml Qt5Network) "$src/$name.cpp"
done
