"""Build LuaHBTeX separately, reusing the reviewed OHOS dependency flags."""
import os
from pathlib import Path
import subprocess

repo = Path(os.environ['BUILD_REPO'])
delivery = Path(os.environ['DELIVERY_ROOT'])
original = (delivery / 'texstudio-harmony/scripts/texlive/build_texlive_ohos.sh').read_text()
build = repo / 'build/luahbtex-ohos'
build.mkdir(parents=True, exist_ok=True)
subprocess.run(['python3', str(delivery / 'texstudio-harmony/scripts/texlive/patch_luahbtex_io.py'), str(repo / 'build/src/texlive-source')], check=True)
env = original[original.index('SOURCE_DIR='):original.index('# ============================================================', original.index('export CFLAGS='))]
# Only declarations are reused; source patching belongs to the baseline builder.
env = '\n'.join(line for line in env.splitlines() if not line.startswith('python3 '))
env = env.replace('build/build-texlive-ohos"', 'build/luahbtex-ohos"')
configure = original[original.index('"${SOURCE_DIR}/configure"'):original.index('\nstep_end', original.index('"${SOURCE_DIR}/configure"'))]
configure = configure.replace('--disable-luahbtex', '--enable-luahbtex')
for engine in ('pdftex', 'bibtex', 'makeindex', 'dvipdfmx', 'mp', 'xetex'):
    configure = configure.replace('--enable-' + engine + ' ', '--disable-' + engine + ' ')
configure = configure.replace('--enable-web2c', '--disable-all-pkgs --enable-web2c')
script = '''#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
PROJECT_ROOT="$BUILD_REPO"
''' + env + '\ncd "$BUILD_DIR"\n' + configure + '''
make -j"${JOBS}" TANGLE="$HOST_BUILD_DIR/texk/web2c/tangle" CTANGLE="$HOST_BUILD_DIR/texk/web2c/ctangle" OTANGLE="$HOST_BUILD_DIR/texk/web2c/otangle" TIE="$HOST_BUILD_DIR/texk/web2c/tie" 2>&1 | tee make-luahbtex.log
file texk/web2c/luahbtex
"$TOOLCHAIN_BIN/llvm-readelf" -d texk/web2c/luahbtex
'''
(build / 'build.sh').write_text(script)
subprocess.run(['bash', str(build / 'build.sh')], check=True)
