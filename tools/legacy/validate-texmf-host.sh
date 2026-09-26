#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export TEXMFROOT="$BUILD_REPO/build/build-texlive-ohos-dist"
export TEXMFCNF="$TEXMFROOT/texmf/web2c"
export TEXMF="$TEXMFROOT/texmf"
export TEXMFDIST="$TEXMFROOT/texmf"
export TEXMFVAR="$DELIVERY_ROOT/validation/texmf-var"
export TEXMFCONFIG="$DELIVERY_ROOT/validation/texmf-config"
export FONTCONFIG_FILE="$TEXMFROOT/texmf/fonts/conf/fonts.conf"
export PATH="$BUILD_REPO/build/build-texlive-host/texk/dvipdfm-x:$PATH"
mkdir -p "$DELIVERY_ROOT/validation/host-output" "$TEXMFVAR" "$TEXMFCONFIG"
cd "$DELIVERY_ROOT/validation"
"$BUILD_REPO/build/build-texlive-host/texk/web2c/pdftex" -progname=pdflatex -interaction=nonstopmode -halt-on-error -output-directory=host-output pdflatex-basic.tex
"$BUILD_REPO/build/build-texlive-host/texk/web2c/xetex" -progname=xelatex -output-driver="$BUILD_REPO/build/build-texlive-host/texk/dvipdfm-x/xdvipdfmx -q -E" -interaction=nonstopmode -halt-on-error -output-directory=host-output xelatex-cjk.tex
"$BUILD_REPO/build/build-texlive-host/texk/web2c/xetex" -progname=xelatex -output-driver="$BUILD_REPO/build/build-texlive-host/texk/dvipdfm-x/xdvipdfmx -q -E" -interaction=nonstopmode -halt-on-error -output-directory=host-output xelatex-cjk.tex
