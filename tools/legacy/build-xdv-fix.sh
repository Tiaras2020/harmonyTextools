#!/usr/bin/env bash
# Historical migration: retained for audit, not a release entry point.
echo 'Historical migration disabled. Use release.json and the current RUNBOOK baseline workflow.' >&2
exit 2
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
for f in utilsSystem.cpp utilsSystem.h execprogram.cpp; do
  cp "$DELIVERY_ROOT/texstudio-harmony/third_party/texstudio/src/$f" "$BUILD_REPO/third_party/texstudio/src/$f"
done
for f in scripts/common/build_texlive_hnp.sh scripts/texlive/build_pack_texmf.sh texstudio_harmony/AppScope/app.json5; do
  cp "$DELIVERY_ROOT/texstudio-harmony/$f" "$BUILD_REPO/$f"
done
python3 - <<'PY'
import os,pathlib,shutil
repo=pathlib.Path(os.environ['BUILD_REPO'])
dest=repo/'build/build-texlive-ohos-dist'
mapping=dest/'texmf/fonts/misc/xetex/fontmapping/tex-text.tec'
mapping.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(repo/'build/src/texlive-source/libs/teckit/tex-text.tec',mapping)
cnf=dest/'texmf/web2c/texmf.cnf'
text=cnf.read_text().replace('texlive_1.0.0','texlive_1.0.3').replace('TECINPUTS =','MISCFONTS =')
if 'MISCFONTS =' not in text:
    text += '\nMISCFONTS = .;$TEXMFDIST/fonts/misc//\n'
cnf.write_text(text)
for name in ('xetex','xdvipdfmx'):
    assert (dest/'bin'/name).stat().st_size > 0
PY
cd "$BUILD_REPO/build/build-texstudio-ohos"
make -j6 > "$DELIVERY_ROOT/logs/xdv-fix-build.log" 2>&1
printf 'TeXstudio rebuild passed\n'
cd "$BUILD_REPO"
bash scripts/common/build_texlive_hnp.sh > "$DELIVERY_ROOT/logs/xdv-fix-hnp.log" 2>&1
bash "$DELIVERY_ROOT/build-support/package-hap.sh" > "$DELIVERY_ROOT/logs/xdv-fix-package.log" 2>&1
export PACKAGE_VERSION=1.0.3
python3 "$DELIVERY_ROOT/build-support/finalize-packages.py"
cp "$DELIVERY_ROOT/artifacts/texlive.hnp" "$DELIVERY_ROOT/artifacts/texlive-1.0.3.hnp"
