#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
[[ "$PACKAGE_VERSION" == 1.0.17 ]] || { echo 'Update the Perl installation prefix and configure marker for the new release.' >&2; exit 1; }
out="$DELIVERY_ROOT/validation/latexmk"
work="$BUILD_REPO/build/perl-ohos-5.40.3"
mkdir -p "$work"
if [[ ! -f "$work/.sources-ready" ]]; then
    tar -xJf "$out/downloads/perl-5.40.3.tar.xz" -C "$work" --strip-components=1
    tar -xzf "$out/downloads/perl-cross-1.6.4.tar.gz" -C "$work" --strip-components=1
    touch "$work/.sources-ready"
fi
cd "$work"
python3 "$DELIVERY_ROOT/build-support/patch-perl-ohos.py" "$work"
tc="$NATIVE_OHOS_SDK/llvm/bin"
export CC="$tc/clang --target=aarch64-linux-ohos --sysroot=$NATIVE_OHOS_SDK/sysroot"
export AR="$tc/llvm-ar" RANLIB="$tc/llvm-ranlib" NM="$tc/llvm-nm"
export STRIP="$tc/llvm-strip" OBJDUMP="$tc/llvm-objdump" READELF="$tc/llvm-readelf"
if [[ ! -f .configured-v7-1.0.17 ]]; then
    # perl-cross does not recognize the OHOS tuple; use its Linux/musl hints,
    # while CC still targets the actual HarmonyOS SDK ABI and sysroot.
    # OHOS returns 12 positional LC_ALL values separated by semicolons.
    # perl-cross defaults to glibc name=value pairs; that breaks non-C locales
    # when Perl forces its six unsupported optional categories back to C.
    ./configure --target=aarch64-linux-musl --hints=linux \
      --prefix=/data/service/hnp/texlive.org/texlive_1.0.17 \
      --all-static --no-dynaloader --disable-mod=ext/re -Uuseshrplib -Doptimize=-O2 \
      -Dd_nanosleep=define -Dsh=/system/bin/sh \
      -Ud_perl_lc_all_uses_name_value_pairs \
      -Dd_perl_lc_all_separator=define '-Dperl_lc_all_separator=";"' \
      -Dd_perl_lc_all_category_positions_init=define \
      '-Dperl_lc_all_category_positions_init={LC_CTYPE,LC_NUMERIC,LC_TIME,LC_COLLATE,LC_MONETARY,LC_MESSAGES,LC_PAPER,LC_NAME,LC_ADDRESS,LC_TELEPHONE,LC_MEASUREMENT,LC_IDENTIFICATION}' \
      '-Dccflags=-D_GNU_SOURCE -Werror=implicit-function-declaration -DNO_LOCALE_ADDRESS -DNO_LOCALE_IDENTIFICATION -DNO_LOCALE_MEASUREMENT -DNO_LOCALE_NAME -DNO_LOCALE_PAPER -DNO_LOCALE_TELEPHONE' \
      > "$out/configure.log" 2>&1
    touch .configured-v7-1.0.17
fi
make SHELL=/bin/sh -j6 > "$out/build.log" 2>&1
# perl-cross's static target links XS but does not copy their companion .pm files.
for module in cpan/* dist/* ext/*; do
    [[ "$module" == ext/re ]] && continue
    if [[ -f "$module/Makefile" && -f "$module/pm_to_blib" ]]; then
        # perl-cross touches this stamp even when the module copy never ran.
        rm "$module/pm_to_blib"
        make -C "$module" SHELL=/bin/sh pm_to_blib >> "$out/build.log" 2>&1
    fi
done
make SHELL=/bin/sh DESTDIR="$work/stage" install.perl > "$out/install.log" 2>&1
"$tc/llvm-readelf" -h -l -d perl > "$out/perl-elf.txt"
echo 'Perl cross-build completed'
