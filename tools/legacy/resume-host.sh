#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO/build/build-texlive-host"
make -j"$JOBS"
for tool in tangle ctangle otangle tie pdftex xetex; do
  test -x "texk/web2c/$tool"
done
texk/web2c/pdftex --version | head -2
texk/web2c/xetex --version | head -2
