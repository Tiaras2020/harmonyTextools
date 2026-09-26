#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
python3 - <<'PY'
from pathlib import Path
p=Path('scripts/common/build_texlive_hnp.sh')
s=p.read_text().replace('      { "source": "bin/lualatex", "target": "bin/lualatex" },\n','').replace(' -name texlive ', ' -n texlive ')
p.write_text(s)
PY
for binary in pdftex tex xetex bibtex makeindex dvipdfmx dvips kpsewhich; do
  test -s "build/build-texlive-ohos-dist/bin/$binary"
done
bash scripts/common/build_texlive_hnp.sh
