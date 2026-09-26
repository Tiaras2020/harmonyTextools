#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
PACKAGE_VERSION="$(python3 "$PROJECT_ROOT/scripts/release_config.py" --field version)"
python3 "$PROJECT_ROOT/scripts/release_config.py"
RUNTIME_VERSION="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("runtimeVersion",d["version"]))' "$PROJECT_ROOT/release.json")"
if [ "$RUNTIME_VERSION" != "$PACKAGE_VERSION" ]; then
    echo "This application reuses runtime $RUNTIME_VERSION; use package-ui-polish.sh instead of rebuilding the accepted HNP." >&2
    exit 1
fi

DIST_DIR="${TEXLIVE_DIST_DIR:-${PROJECT_ROOT}/build/build-texlive-ohos-dist}"
HNP_DIR="${PROJECT_ROOT}/build/build-texlive-ohos-hnp"
grep -Fxq "TEXMFROOT = /data/service/hnp/texlive.org/texlive_$PACKAGE_VERSION" "$DIST_DIR/texmf/web2c/texmf.cnf" || {
  echo 'Runtime texmf.cnf version differs from release.json; rebuild resources first.' >&2
  exit 1
}

# TeXstudio discovers installed packages through Kpathsea's ls-R database.
for style in plain abbrv unsrt alpha; do
    test -s "$DIST_DIR/texmf/bibtex/bst/base/$style.bst" || {
        echo "Missing mandatory BibTeX resource: $style.bst" >&2
        exit 1
    }
done

python3 - "$DIST_DIR/texmf" <<'PY'
import os,pathlib,sys
root=pathlib.Path(sys.argv[1])
lines=['% ls-R -- filename database for kpathsea; do not change this line.','']
for directory,dirs,files in os.walk(root):
    dirs.sort(); files.sort()
    relative=pathlib.Path(directory).relative_to(root).as_posix()
    lines += [('.' if relative=='.' else './'+relative)+':',*dirs,*files,'']
(root/'ls-R').write_text('\n'.join(lines)+'\n')
PY

if [ -d "$HNP_DIR" ]; then
    rm -r "$HNP_DIR"
fi

mkdir -p $HNP_DIR

# 拷贝 dist-ohos 内容
cp -r $DIST_DIR/bin $HNP_DIR/
cp -r $DIST_DIR/lib $HNP_DIR/
cp -r $DIST_DIR/share $HNP_DIR/
cp -r $DIST_DIR/texmf $HNP_DIR/

cat > $HNP_DIR/hnp.json << EOF
{
  "type": "hnp-config",
  "name": "texlive",
  "version": "$PACKAGE_VERSION",
  "install": {
    "links": [
      { "source": "bin/pdftex",    "target": "bin/pdftex" },
      { "source": "bin/tex",       "target": "bin/tex" },
      { "source": "bin/xetex",     "target": "bin/xetex" },
      { "source": "bin/bibtex",    "target": "bin/bibtex" },
      { "source": "bin/makeindex", "target": "bin/makeindex" },
      { "source": "bin/dvipdfmx",  "target": "bin/dvipdfmx" },
      { "source": "bin/xdvipdfmx", "target": "bin/xdvipdfmx" },
      { "source": "bin/dvips",     "target": "bin/dvips" },
      { "source": "bin/kpsewhich", "target": "bin/kpsewhich" },
      { "source": "bin/latex", "target": "bin/latex" },
      { "source": "bin/pdflatex", "target": "bin/pdflatex" },
      { "source": "bin/xelatex", "target": "bin/xelatex" },
      { "source": "bin/perl", "target": "bin/perl" },
      { "source": "bin/latexmk", "target": "bin/latexmk" },
      { "source": "bin/biber", "target": "bin/biber" }
    ]
  }
}

EOF

python3 - "$HNP_DIR" <<'PY'
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]); path=root/'hnp.json'; config=json.loads(path.read_text())
lua=('luahbtex','lualatex')
if any((root/'bin'/name).exists() for name in lua):
    assert all((root/'bin'/name).is_file() for name in lua), 'Incomplete Lua command payload'
    assert (root/'texmf/web2c/luahbtex/lualatex.fmt').is_file(), 'Missing LuaLaTeX format'
    config['install']['links'] += [{'source':'bin/'+name,'target':'bin/'+name} for name in lua]
    path.write_text(json.dumps(config,indent=2)+'\n')
PY

"$TOOL_HOME/sdk/default/openharmony/toolchains/hnpcli" pack -i "$HNP_DIR" -o "${PROJECT_ROOT}/build" -n texlive -v "$PACKAGE_VERSION"
