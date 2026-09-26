#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
rsync -a --exclude=.git --exclude=build --exclude=third_party --exclude=.build-tools --exclude=.hvigor --exclude=oh_modules --exclude=local.properties "$BUILD_REPO/" "$DELIVERY_ROOT/texstudio-harmony/"
rsync -a --exclude=.git "$BUILD_REPO/third_party/lycium/" "$DELIVERY_ROOT/texstudio-harmony/third_party/lycium/"
