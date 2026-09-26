#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
python3 "$DELIVERY_ROOT/build-support/sync-baseline.py"
"$BUILD_REPO/build/build-qt-ohos-install/bin/lrelease" "$BUILD_REPO/third_party/texstudio/translation/texstudio_zh_CN.ts" -qm "$BUILD_REPO/third_party/texstudio/translation/texstudio_zh_CN.qm"
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j6 > "$DELIVERY_ROOT/validation/resources/release-build.log" 2>&1
if [[ "$PACKAGE_VERSION" == 1.0.21 ]]; then
    test -f "$DELIVERY_ROOT/validation/compat-fix-1.0.21/resources.json"
    test -d "$BUILD_REPO/build/resource-release-1.0.21"
elif [[ "$PACKAGE_VERSION" == 1.0.20 ]]; then
    python3 "$DELIVERY_ROOT/build-support/stage-luahbtex-release.py"
else
    python3 "$DELIVERY_ROOT/build-support/prepare-resource-release.py"
    python3 "$DELIVERY_ROOT/build-support/stage-latexmk.py"
fi
if [[ "$PACKAGE_VERSION" == 1.0.18 || "$PACKAGE_VERSION" == 1.0.19 ]]; then
    python3 "$DELIVERY_ROOT/build-support/stage-biber.py"
fi
export TEXLIVE_DIST_DIR="$BUILD_REPO/build/resource-release-$PACKAGE_VERSION"
cd "$BUILD_REPO"
bash scripts/common/build_texlive_hnp.sh > "$DELIVERY_ROOT/validation/resources/hnp.log" 2>&1
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/validation/resources/hap.log" 2>&1
python3 "$DELIVERY_ROOT/build-support/finalize-packages.py"
