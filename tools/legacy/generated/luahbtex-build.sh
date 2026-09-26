#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
PROJECT_ROOT="$BUILD_REPO"
SOURCE_DIR="${PROJECT_ROOT}/build/src/texlive-source"
BUILD_DIR="${PROJECT_ROOT}/build/luahbtex-ohos"
HOST_BUILD_DIR="${PROJECT_ROOT}/build/build-texlive-host"

export OHOS_SDK="$TOOL_HOME/sdk/default/openharmony"
export SYSROOT="${OHOS_SDK}/native/sysroot"
TOOLCHAIN_BIN="${OHOS_SDK}/native/llvm/bin"

export HPK_INSTALL_DIR="$PROJECT_ROOT/build/build-hpkbuilds-ohos-install"
ICU_PREFIX="${HPK_INSTALL_DIR}/icu/arm64-v8a"
FREETYPE_PREFIX="${HPK_INSTALL_DIR}/freetype2/arm64-v8a"
HARFBUZZ_PREFIX="${HPK_INSTALL_DIR}/harfbuzz/arm64-v8a"
GRAPHITE2_PREFIX="${HPK_INSTALL_DIR}/graphite2/arm64-v8a"
TECKIT_PREFIX="${HPK_INSTALL_DIR}/teckit/arm64-v8a"
ZLIB_PREFIX="${HPK_INSTALL_DIR}/zlib/arm64-v8a"
BZIP2_PREFIX="${HPK_INSTALL_DIR}/bzip2/arm64-v8a"
LIBPNG_PREFIX="${HPK_INSTALL_DIR}/libpng/arm64-v8a"
BROTLI_PREFIX="${HPK_INSTALL_DIR}/brotli/arm64-v8a"
FONTCONFIG_PREFIX="${HPK_INSTALL_DIR}/fontconfig/arm64-v8a"
EXPAT_PREFIX="${HPK_INSTALL_DIR}/expat/arm64-v8a"

# 合并所有依赖到编译参数
DEP_INCLUDES="-I${ICU_PREFIX}/include \
              -I${FREETYPE_PREFIX}/include/freetype2 \
              -I${HARFBUZZ_PREFIX}/include/harfbuzz \
              -I${GRAPHITE2_PREFIX}/include \
              -I${TECKIT_PREFIX}/include \
              -I${ZLIB_PREFIX}/include \
              -I${BZIP2_PREFIX}/include \
              -I${LIBPNG_PREFIX}/include \
              -I${BROTLI_PREFIX}/include \
              -I${FONTCONFIG_PREFIX}/include \
              -I${EXPAT_PREFIX}/include"
DEP_LIBDIRS="-L${ICU_PREFIX}/lib \
             -L${FREETYPE_PREFIX}/lib \
             -L${HARFBUZZ_PREFIX}/lib \
             -L${GRAPHITE2_PREFIX}/lib \
             -L${TECKIT_PREFIX}/lib \
             -L${ZLIB_PREFIX}/lib \
             -L${BZIP2_PREFIX}/lib \
             -L${LIBPNG_PREFIX}/lib \
             -L${BROTLI_PREFIX}/lib \
             -L${FONTCONFIG_PREFIX}/lib \
             -L${EXPAT_PREFIX}/lib"

export CC="${TOOLCHAIN_BIN}/clang --target=aarch64-linux-ohos --sysroot=${SYSROOT}"
export CXX="${TOOLCHAIN_BIN}/clang++ --target=aarch64-linux-ohos --sysroot=${SYSROOT}"
export AR="${TOOLCHAIN_BIN}/llvm-ar"
export RANLIB="${TOOLCHAIN_BIN}/llvm-ranlib"
export STRIP="${TOOLCHAIN_BIN}/llvm-strip"
export NM="${TOOLCHAIN_BIN}/llvm-nm"
export LD="${TOOLCHAIN_BIN}/ld.lld"

export CFLAGS="-O2 -fPIC ${DEP_INCLUDES}"
export CXXFLAGS="-O2 -fPIC ${DEP_INCLUDES}"
# export LDFLAGS="${DEP_LIBDIRS}"
# 在此处加入了你需要的 ldflags，并对 ${ORIGIN} 进行了转义
export LDFLAGS="${DEP_LIBDIRS} -Wl,-rpath='\$\$ORIGIN/../lib' -Wl,--disable-new-dtags"
export PKG_CONFIG_PATH="${ICU_PREFIX}/lib/pkgconfig:${FREETYPE_PREFIX}/lib/pkgconfig:${HARFBUZZ_PREFIX}/lib/pkgconfig:${GRAPHITE2_PREFIX}/lib/pkgconfig:${TECKIT_PREFIX}/lib/pkgconfig:${ZLIB_PREFIX}/lib/pkgconfig"

JOBS="${JOBS:-${JOBS:-6}}"

cd "$BUILD_DIR"
"${SOURCE_DIR}/configure" \
    --host=aarch64-linux-ohos \
    --build=x86_64-linux-gnu \
    \
    --disable-native-texlive-build \
    --disable-shared \
    --without-x \
    \
    --disable-all-pkgs --enable-web2c \
    --disable-pdftex \
    --disable-bibtex \
    --disable-makeindex \
    --disable-dvipdfmx \
    --disable-mp \
    --disable-xetex \
    \
    --disable-luatex \
    --disable-luajittex \
    --enable-luahbtex \
    --disable-mf \
    --disable-mf-nowin \
    --disable-aleph \
    --disable-eptex \
    --disable-euptex \
    --disable-ptex \
    --disable-uptex \
    --disable-hitex \
    --disable-xdvipsk \
    \
    --with-system-icu \
    --with-system-zlib \
    --without-system-libpng \
    --with-system-freetype2 \
    --with-system-harfbuzz \
    --without-system-cairo \
    --without-system-gd \
    --without-system-pixman \
    --with-system-graphite2 \
    --without-system-zziplib \
    --without-system-mpfr \
    --without-system-gmp \
    --without-system-potrace \
    --with-system-teckit \
    --without-system-paper \
    \
    CC="$CC" \
    CXX="$CXX" \
    AR="$AR" \
    RANLIB="$RANLIB" \
    STRIP="$STRIP" \
    NM="$NM" \
    CFLAGS="$CFLAGS" \
    CXXFLAGS="$CXXFLAGS" \
    LDFLAGS="$LDFLAGS" \
    \
    ZLIB_CFLAGS="-I${ZLIB_PREFIX}/include" \
    ZLIB_LIBS="${ZLIB_PREFIX}/lib/libz.a" \
    \
    ICU_CFLAGS="-I${ICU_PREFIX}/include" \
    ICU_CPPFLAGS="-I${ICU_PREFIX}/include" \
    ICU_LIBS="${ICU_PREFIX}/lib/libicui18n.a ${ICU_PREFIX}/lib/libicuuc.a ${ICU_PREFIX}/lib/libicudata.a -lc++ -lm" \
    \
    FREETYPE2_CFLAGS="-I${FREETYPE_PREFIX}/include/freetype2" \
    FREETYPE2_LIBS="${FREETYPE_PREFIX}/lib/libfreetype.a \
                    ${ZLIB_PREFIX}/lib/libz.a \
                    ${BZIP2_PREFIX}/lib/libbz2.a \
                    ${LIBPNG_PREFIX}/lib/libpng16.a \
                    ${BROTLI_PREFIX}/lib/libbrotlidec-static.a \
                    ${BROTLI_PREFIX}/lib/libbrotlicommon-static.a \
                    -lm" \
    \
    GRAPHITE2_CFLAGS="-I${GRAPHITE2_PREFIX}/include" \
    GRAPHITE2_LIBS="${GRAPHITE2_PREFIX}/lib/libgraphite2.a -lc++ -lm" \
    \
    HARFBUZZ_CFLAGS="-I${HARFBUZZ_PREFIX}/include/harfbuzz" \
    HARFBUZZ_LIBS="${HARFBUZZ_PREFIX}/lib/libharfbuzz.a \
                   ${FREETYPE_PREFIX}/lib/libfreetype.a \
                   ${GRAPHITE2_PREFIX}/lib/libgraphite2.a \
                   ${ICU_PREFIX}/lib/libicuuc.a \
                   ${ICU_PREFIX}/lib/libicudata.a \
                   ${ZLIB_PREFIX}/lib/libz.a \
                   ${BZIP2_PREFIX}/lib/libbz2.a \
                   ${LIBPNG_PREFIX}/lib/libpng16.a \
                   ${BROTLI_PREFIX}/lib/libbrotlidec-static.a \
                   ${BROTLI_PREFIX}/lib/libbrotlicommon-static.a \
                   -lc++ -lm" \
    \
    TECKIT_CFLAGS="-I${TECKIT_PREFIX}/include" \
    TECKIT_LIBS="${TECKIT_PREFIX}/lib/libTECkit.a \
                 ${ZLIB_PREFIX}/lib/libz.a \
                 -lc++ -lm" \
    \
    FONTCONFIG_CFLAGS="-I${FONTCONFIG_PREFIX}/include" \
    FONTCONFIG_LIBS="${FONTCONFIG_PREFIX}/lib/libfontconfig.a \
                     ${EXPAT_PREFIX}/lib/libexpat.a \
                     ${FREETYPE_PREFIX}/lib/libfreetype.a \
                     ${ZLIB_PREFIX}/lib/libz.a \
                     ${BZIP2_PREFIX}/lib/libbz2.a \
                     ${LIBPNG_PREFIX}/lib/libpng16.a \
                     ${BROTLI_PREFIX}/lib/libbrotlidec-static.a \
                     ${BROTLI_PREFIX}/lib/libbrotlicommon-static.a \
                     -lm" \
    \
    EXPAT_CFLAGS="-I${EXPAT_PREFIX}/include" \
    EXPAT_LIBS="${EXPAT_PREFIX}/lib/libexpat.a" \
    \
    2>&1 | tee configure-ohos.log

make -j"${JOBS}" TANGLE="$HOST_BUILD_DIR/texk/web2c/tangle" CTANGLE="$HOST_BUILD_DIR/texk/web2c/ctangle" OTANGLE="$HOST_BUILD_DIR/texk/web2c/otangle" TIE="$HOST_BUILD_DIR/texk/web2c/tie" 2>&1 | tee make-luahbtex.log
file texk/web2c/luahbtex
"$TOOLCHAIN_BIN/llvm-readelf" -d texk/web2c/luahbtex
