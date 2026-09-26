#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export TEXMFROOT="$BUILD_REPO/build/build-texlive-ohos-dist"
export TEXMF="$TEXMFROOT/texmf" TEXMFDIST="$TEXMFROOT/texmf" TEXMFCNF="$TEXMFROOT/texmf/web2c"
export TEXMFVAR="$DELIVERY_ROOT/validation/mcm-project/texmf-var"
export TEXMFCONFIG="$TEXMFVAR"
mkdir -p "$TEXMFVAR"
python3 "$DELIVERY_ROOT/build-support/write-texmf-index.py" "$TEXMFDIST"
kpse="$BUILD_REPO/build/build-texlive-host/texk/kpathsea/kpsewhich"
"$kpse" --show-path ls-R > "$DELIVERY_ROOT/validation/mcm-project/index-path.txt"
for file in mcmthesis.cls biblatex.sty todonotes.sty tocloft.sty newtxtext.sty amsmath.sty; do
  "$kpse" "$file"
done > "$DELIVERY_ROOT/validation/mcm-project/package-lookup.txt"
cd "$DELIVERY_ROOT/validation/mcm-project/project"
engine="$BUILD_REPO/build/build-texlive-host/texk/web2c/pdftex"
for pass in 1 2 3; do
  "$engine" -progname=pdflatex -recorder -interaction=nonstopmode -halt-on-error mcmthesis-demo.tex > "../pdflatex-pass-$pass.stdout" 2>&1
done
printf 'MCM project compiled in three passes using packaged TeX resources\n'
