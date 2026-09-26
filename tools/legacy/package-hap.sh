#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
python3 scripts/release_config.py
test "$PACKAGE_VERSION" = "$(python3 scripts/release_config.py --field version)"
bash scripts/common/copy_libs_entry.sh
cp "$NATIVE_OHOS_SDK/llvm/lib/aarch64-linux-ohos/libc++_shared.so" texstudio_harmony/entry/libs/arm64-v8a/
for name in libtexstudio.so libqohos.so libQt5Core.so libQt5Gui.so libQt5Widgets.so libQt5PrintSupport.so libQt5Svg.so libQt5Xml.so libQt5Qml.so libQt5Concurrent.so libQt5DBus.so libQt5Network.so libpoppler.so.108 libpoppler-qt5.so.1 libc++_shared.so; do
  test -s "texstudio_harmony/entry/libs/arm64-v8a/$name"
done
python3 "$DELIVERY_ROOT/build-support/check-elf.py"
cd texstudio_harmony
hvigorw --mode module -p module=entry@default -p product=default -p requiredDeviceType=2in1 assembleHap --no-daemon
