#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
host="$BUILD_REPO/build/build-poppler-preview-host"
src="$BUILD_REPO/third_party/poppler"
out="$DELIVERY_ROOT/validation/cjk-rendering"
cmake -S "$src" -B "$host" \
    -DENABLE_QT5=OFF -DENABLE_QT6=OFF -DENABLE_CPP=OFF -DENABLE_GLIB=OFF \
    -DENABLE_UTILS=OFF -DENABLE_GOBJECT_INTROSPECTION=OFF \
    -DENABLE_LIBOPENJPEG=none -DENABLE_CMS=none -DENABLE_DCTDECODER=unmaintained \
    -DENABLE_LIBCURL=OFF -DENABLE_ZLIB=OFF -DWITH_NSS3=OFF \
    -DFONT_CONFIGURATION=generic -DENABLE_BOOST=OFF \
    -DBUILD_GTK_TESTS=OFF -DBUILD_QT5_TESTS=OFF -DBUILD_QT6_TESTS=OFF -DBUILD_CPP_TESTS=OFF \
    -DCMAKE_DISABLE_FIND_PACKAGE_Cairo=ON > "$out/host-configure.log" 2>&1
cmake --build "$host" --target poppler -j4 > "$out/host-build.log" 2>&1
g++ -std=c++17 -I"$src" -I"$src/poppler" -I"$host" -I"$host/poppler" \
    "$DELIVERY_ROOT/build-support/probe-poppler-preview.cpp" \
    -L"$host" -lpoppler -Wl,-rpath,"$host" -o "$host/probe-preview"
mkdir -p "$host/empty-data"
"$host/probe-preview" "$out/device-original.pdf" "$host/empty-data" "$out/poppler-before.ppm" > "$out/poppler-before.log" 2>&1
"$host/probe-preview" "$out/device-original.pdf" "$BUILD_REPO/build/build-texlive-ohos-dist/share/poppler" "$out/poppler-after.ppm" > "$out/poppler-after.log" 2>&1
grep -q "Missing language pack for 'Adobe-GB1'" "$out/poppler-before.log"
if grep -E "Missing language pack|Unknown font" "$out/poppler-after.log"; then exit 1; fi
printf 'Same-version Poppler missing-data reproduction and repaired rendering passed\n'
