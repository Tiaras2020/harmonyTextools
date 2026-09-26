#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
mkdir -p "$BUILD_REPO/build/src"
cd "$BUILD_REPO/build/src"
curl -fL -C - --retry 3 --connect-timeout 30 --max-time 1800 'https://mirrors.tuna.tsinghua.edu.cn/qt/snapshots/qt/qt-for-harmonyos/5.12.12/qt-harmonyos-src-5.12.12-20260403.tar.xz' -o qt-harmonyos-src-5.12.12-20260403.tar.xz
echo '473fd069cbafad0b111701c00a74831abbfec24cb07495bf0d217368307df53a  qt-harmonyos-src-5.12.12-20260403.tar.xz' | sha256sum -c -
xz -t qt-harmonyos-src-5.12.12-20260403.tar.xz
tar -xf qt-harmonyos-src-5.12.12-20260403.tar.xz
ls -d qt*/
