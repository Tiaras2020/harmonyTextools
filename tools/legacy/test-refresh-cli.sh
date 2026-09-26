#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/refresh-cli-1.0.26"
mkdir -p "$out/watcher-host"
src="$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src"
cp "$src/qcodeedit/lib/qreliablefilewatch.cpp" "$src/qcodeedit/lib/qreliablefilewatch.h" "$out/watcher-host/"
printf '#include <QtCore>\n' > "$out/watcher-host/mostQtHeaders.h"
printf '#define QCE_EXPORT\n' > "$out/watcher-host/qce-config.h"
cp "$DELIVERY_ROOT/build-support/test-refresh-cli.cpp" "$out/watcher-host/"
moc -DQ_OS_OHOS "$out/watcher-host/qreliablefilewatch.h" -o "$out/watcher-host/moc_watch.cpp"
moc -DQ_OS_OHOS "$out/watcher-host/test-refresh-cli.cpp" -o "$out/watcher-host/test-refresh-cli.moc"
g++ -std=c++17 -fPIC -DQ_OS_OHOS -I"$src" -I"$out/watcher-host" "$out/watcher-host/"*.cpp $(pkg-config --cflags --libs Qt5Widgets Qt5Network) -o "$out/test-refresh"
"$out/test-refresh" > "$out/host-tests.log" 2>&1
cat "$out/host-tests.log"
