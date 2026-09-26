#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
out="$DELIVERY_ROOT/validation/network-1.0.31"
mkdir -p "$out/qt-before"
export OHOS_SDK_ROOT="$OHOS_SDK"
export OHOS_NDK_ROOT="$NATIVE_OHOS_SDK"
cd "$BUILD_REPO/build/build-qt-ohos"
for f in config.opt config.summary; do
  test -e "$out/qt-before/$f" || cp "$f" "$out/qt-before/$f"
done
test -e "$out/qt-before/libQt5Network.so" || cp -L ../build-qt-ohos-install/lib/libQt5Network.so "$out/qt-before/libQt5Network.so"
python3 - <<'PY' > "$out/qt-configure.log" 2>&1
import os,pathlib,subprocess
r=pathlib.Path(os.environ['BUILD_REPO']); b=r/'build/build-qt-ohos'
p=r/'build/biber-native/install'
args=(pathlib.Path(os.environ['DELIVERY_ROOT'])/'validation/network-1.0.31/qt-before/config.opt').read_text().splitlines()
args += ['-openssl-linked','OPENSSL_INCDIR='+str(p/'include'), 'OPENSSL_LIBS='+str(p/'lib/libssl.a')+' '+str(p/'lib/libcrypto.a')+' -ldl -pthread -Wl,--exclude-libs,libssl.a:libcrypto.a']
subprocess.run([str(r/'build/src/qt-harmonyos-5.12.12/configure')]+args,cwd=b,check=True)
PY
network=src/network
test -d "$network" || network=qtbase/src/network
make -C "$network" -j4 > "$out/qt-network-build.log" 2>&1
make -C "$network" install > "$out/qt-network-install.log" 2>&1
grep 'QT_FEATURE_ssl 1' ../build-qt-ohos-install/include/QtNetwork/qtnetwork-config.h
echo 'Qt Network TLS build completed'
