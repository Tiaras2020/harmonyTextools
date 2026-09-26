#!/usr/bin/env bash
# Historical migration: retained for audit, not a release entry point.
echo 'Historical migration disabled. Use release.json and the current RUNBOOK baseline workflow.' >&2
exit 2
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
for f in utilsSystem.cpp utilsSystem.h execprogram.cpp pdfviewer/pdfrendermanager.cpp; do
  cp "$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src/$f" "$BUILD_REPO/third_party/texstudio/src/$f"
done
for f in scripts/common/build_texlive_hnp.sh scripts/texlive/build_pack_texmf.sh scripts/poppler/build_poppler.sh texstudio_harmony/AppScope/app.json5; do
  cp "$DELIVERY_ROOT/texstudio-harmony/$f" "$BUILD_REPO/$f"
done
python3 - <<'PY'
import os,pathlib,shutil
repo=pathlib.Path(os.environ['BUILD_REPO'])
dest=repo/'build/build-texlive-ohos-dist'
shutil.copytree('/usr/share/poppler',dest/'share/poppler',dirs_exist_ok=True)
shutil.copy2('/usr/share/doc/poppler-data/copyright',dest/'share/poppler/COPYRIGHT')
cnf=dest/'texmf/web2c/texmf.cnf'
cnf.write_text(cnf.read_text().replace('texlive_1.0.3','texlive_1.0.4'))
assert (dest/'share/poppler/cidToUnicode/Adobe-GB1').stat().st_size>0
PY
cmake -S "$BUILD_REPO/third_party/poppler" -B "$BUILD_REPO/build/build-poppler-ohos" -DENABLE_UNSTABLE_API_ABI_HEADERS=ON > "$DELIVERY_ROOT/logs/preview-fix-poppler-headers.log" 2>&1
cmake --install "$BUILD_REPO/build/build-poppler-ohos" >> "$DELIVERY_ROOT/logs/preview-fix-poppler-headers.log" 2>&1
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j6 > "$DELIVERY_ROOT/logs/preview-fix-build.log" 2>&1
printf 'TeXstudio preview rebuild passed\n'
cd "$BUILD_REPO"
bash scripts/common/build_texlive_hnp.sh > "$DELIVERY_ROOT/logs/preview-fix-hnp.log" 2>&1
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/logs/preview-fix-package.log" 2>&1
export PACKAGE_VERSION=1.0.4
python3 "$DELIVERY_ROOT/build-support/finalize-packages.py"
cp "$DELIVERY_ROOT/artifacts/texlive.hnp" "$DELIVERY_ROOT/artifacts/texlive-1.0.4.hnp"
