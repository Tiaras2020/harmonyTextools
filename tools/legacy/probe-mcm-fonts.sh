#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export TEXMFROOT="$BUILD_REPO/build/build-texlive-ohos-dist"
export TEXMF="$TEXMFROOT/texmf" TEXMFDIST="$TEXMFROOT/texmf" TEXMFCNF="$TEXMFROOT/texmf/web2c"
kpse="$BUILD_REPO/build/build-texlive-host/texk/kpathsea/kpsewhich"
"$kpse" --show-path=vf
"$kpse" pcrr8c.vf || true
grep '^pcrr8' "$TEXMF/fonts/map/pdftex/updmap/pdftex.map" || true
find "$TEXMF" -name 'pcrr8c*'
