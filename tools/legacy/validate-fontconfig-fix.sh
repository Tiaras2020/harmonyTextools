#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export TEXMFROOT="$BUILD_REPO/build/build-texlive-ohos-dist"
export TEXMFDIST="$TEXMFROOT/texmf"
export TEXMF="$TEXMFDIST"
export TEXMFCNF="$TEXMFDIST/web2c"
export TEXMFVAR="$DELIVERY_ROOT/validation/fontconfig-fix/texmf-var"
export TEXMFCONFIG="$TEXMFVAR"
export FONTCONFIG_FILE="$DELIVERY_ROOT/validation/fontconfig-fix/fonts.conf"
mkdir -p "$TEXMFVAR" "$DELIVERY_ROOT/validation/fontconfig-fix/cache"
python3 - <<'PY'
import os,pathlib,xml.etree.ElementTree as ET
p=ET.Element('fontconfig')
for name in ['fonts/opentype','fonts/truetype']:
    ET.SubElement(p,'dir').text=os.environ['TEXMFDIST']+'/'+name
ET.SubElement(p,'dir').text='/system/fonts'
ET.SubElement(p,'cachedir').text=os.environ['DELIVERY_ROOT']+'/validation/fontconfig-fix/cache'
ET.ElementTree(p).write(os.environ['FONTCONFIG_FILE'],encoding='utf-8',xml_declaration=True)
PY
cd "$DELIVERY_ROOT/validation/fontconfig-fix"
fc-list -f '%{file}\n' > discovered-fonts.txt
python3 - <<'PY'
import os,pathlib
fonts=pathlib.Path('discovered-fonts.txt').read_text().splitlines()
assert fonts and all(p.startswith(os.environ['TEXMFDIST']+'/fonts/') for p in fonts)
assert any('Fandol' in p for p in fonts)
print('Fontconfig discovers',len(fonts),'font faces, all from delivered texmf resources.')
PY
fc-match -f '%{family}: %{file}\n' FandolSong-Regular
for passno in 1 2; do
"$BUILD_REPO/build/build-texlive-host/texk/web2c/xetex" -progname=xelatex -output-driver="$BUILD_REPO/build/build-texlive-host/texk/dvipdfm-x/xdvipdfmx -q -E" -interaction=nonstopmode -halt-on-error "$DELIVERY_ROOT/validation/xelatex-cjk.tex" > "xelatex-pass-$passno.stdout" 2>&1
done
"$BUILD_REPO/build/build-texlive-host/texk/web2c/pdftex" -progname=pdflatex -interaction=nonstopmode -halt-on-error "$DELIVERY_ROOT/validation/pdflatex-basic.tex" > pdflatex.stdout 2>&1
printf 'Both Chinese XeLaTeX passes and English pdfLaTeX passed with bundled-only fonts.\n'