#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
python3 - <<'PY'
from pathlib import Path
p=Path('scripts/texlive/build_texlive_ohos.sh')
s=p.read_text().replace('libbrotlidec.a','libbrotlidec-static.a').replace('libbrotlicommon.a','libbrotlicommon-static.a')
p.write_text(s)
PY
bash -o pipefail scripts/texlive/build_texlive_ohos.sh
