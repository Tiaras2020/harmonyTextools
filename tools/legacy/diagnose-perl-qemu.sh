#!/usr/bin/env bash
set -uo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
set +e
work="$BUILD_REPO/build/perl-ohos-5.40.3"
runtime="$work/stage/data/service/hnp/texlive.org/texlive_1.0.15"
export PERL5LIB="$runtime/lib/perl5/5.40.3:$runtime/lib/perl5/5.40.3/aarch64-linux" LC_ALL=C
ulimit -c 0
qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" -e 'print "CORE OK\n"'
for module in Config File::Basename File::Copy File::Spec::Functions File::Glob File::Path FileHandle File::Find List::Util Cwd Digest::MD5 Time::HiRes Encode Unicode::Normalize utf8 feature sigtrap; do
    echo "MODULE $module"
    qemu-aarch64 -L "$work/qemu-root" "$runtime/bin/perl" -M"$module" -e 'print "OK\n"'
    echo "EXIT $?"
done
