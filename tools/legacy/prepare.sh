#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$BUILD_REPO" "$DELIVERY_ROOT/logs"
rsync -a --exclude=.git --exclude=build /mnt/e/CodeProjects/harmonytexlive/texstudio-harmony/ "$BUILD_REPO/"
find "$BUILD_REPO" -type f \( -name '*.sh' -o -name HPKBUILD \) -exec sed -i 's/\r$//' {} +
# Limit compilation to six jobs within the available WSL memory.
find "$BUILD_REPO/scripts" -type f \( -name '*.sh' -o -name HPKBUILD \) -exec sed -i 's/$(nproc)/${JOBS:-6}/g' {} +
sed -i 's/make -j32/make -j6/;s/ninja -j32/ninja -j6/' "$BUILD_REPO/third_party/lycium/build.sh"
mkdir -p "$BUILD_REPO/.build-tools"
ln -sfn /usr/bin/python3 "$BUILD_REPO/.build-tools/python"
cd "$BUILD_REPO"
printf 'Prepared %s\n' "$BUILD_REPO"
