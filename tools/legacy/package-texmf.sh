#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
bash scripts/texlive/build_pack_texmf.sh
for fmt in pdftex/pdflatex.fmt pdftex/latex.fmt xetex/xelatex.fmt; do
  test -s "build/build-texlive-ohos-dist/texmf/web2c/$fmt"
done
python3 "$DELIVERY_ROOT/build-support/check-elf.py"
