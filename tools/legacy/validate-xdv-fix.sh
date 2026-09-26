#!/usr/bin/env bash
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
export CASE_ROOT="$BUILD_REPO/build/validation-xdv-1.0.3"
export OUT="$DELIVERY_ROOT/validation/xdv-fix"
mkdir -p "$CASE_ROOT" "$OUT"
python3 - <<'PY'
import os,pathlib,zipfile,json,shutil,hashlib,xml.etree.ElementTree as ET
repo=pathlib.Path(os.environ['BUILD_REPO']); case=pathlib.Path(os.environ['CASE_ROOT']); out=pathlib.Path(os.environ['OUT'])
with zipfile.ZipFile(repo/'build/texlive.hnp') as z:
    root=next(n[:-8] for n in z.namelist() if n.endswith('/hnp.json'))
    cfg=json.loads(z.read(root+'hnp.json'))
    assert cfg['version']=='1.0.3'
    links={entry['target']:entry['source'] for entry in cfg['install']['links']}
    assert links['bin/xdvipdfmx']=='bin/xdvipdfmx'
    assert all(root+src in z.namelist() for src in links.values())
    # Extract actual delivered resources, not the host TeX distribution.
    for name in z.namelist():
        if name.startswith(root+'texmf/') or name.startswith(root+'share/'):
            z.extract(name,case)
    tec=case/root/'texmf/fonts/misc/xetex/fontmapping/tex-text.tec'
    assert tec.stat().st_size>0
    cnf=(case/root/'texmf/web2c/texmf.cnf').read_text()
    assert 'MISCFONTS = .;$TEXMFDIST/fonts/misc//' in cnf
    assert 'texlive_1.0.3' in cnf
    assert z.read(root+'bin/xdvipdfmx')[:4]==b'\x7fELF'
    public=case/'public-bin'; public.mkdir(exist_ok=True)
    hosts={'bin/xelatex':'texk/web2c/xetex','bin/xdvipdfmx':'texk/dvipdfm-x/xdvipdfmx','bin/pdflatex':'texk/web2c/pdftex'}
    for target,host in hosts.items():
        assert target in links
        shutil.copy2(repo/'build/build-texlive-host'/host,public/pathlib.Path(target).name)
    (out/'package-check.json').write_text(json.dumps({'hnp_version':cfg['version'],'driver_exported':True,'mapping_bytes':tec.stat().st_size,'mapping_sha256':hashlib.sha256(tec.read_bytes()).hexdigest(),'host_replacements_for_runtime_test':hosts},indent=2)+'\n')
tree=ET.Element('fontconfig')
for sub in ('opentype','truetype'):
    ET.SubElement(tree,'dir').text=str(case/root/'texmf/fonts'/sub)
ET.SubElement(tree,'cachedir').text=str(case/'fontcache')
ET.ElementTree(tree).write(str(case/'fonts.conf'),encoding='utf-8',xml_declaration=True)
PY
export TEXMFROOT="$CASE_ROOT/build-texlive-ohos-hnp"
export TEXMF="$TEXMFROOT/texmf" TEXMFDIST="$TEXMFROOT/texmf" TEXMFCNF="$TEXMFROOT/texmf/web2c"
export FONTCONFIG_FILE="$CASE_ROOT/fonts.conf" ICU_DATA="$TEXMFROOT/share/icu"
export TEXMFVAR="$CASE_ROOT/texmf-var" TEXMFCONFIG="$CASE_ROOT/texmf-var"
export PATH="$CASE_ROOT/public-bin:$PATH"
mkdir -p "$TEXMFVAR"
cd "$OUT"
cp "$DELIVERY_ROOT/validation/xelatex-cjk.tex" .
# No output-driver override: XeTeX must find xdvipdfmx beside its public entry.
for passno in 1 2; do
    xelatex -interaction=nonstopmode -halt-on-error xelatex-cjk.tex > "xelatex-pass-$passno.stdout" 2>&1
done
pdflatex -interaction=nonstopmode -halt-on-error "$DELIVERY_ROOT/validation/pdflatex-basic.tex" > pdflatex.stdout 2>&1
if grep -E 'Font mapping |driver return code|Missing character|^!' xelatex-cjk.log; then
    echo 'Unexpected missing resource or driver error' >&2
    exit 1
fi
if command -v pdftoppm >/dev/null && command -v pdftotext >/dev/null; then
    pdftotext xelatex-cjk.pdf xelatex-cjk.txt
    pdftoppm -scale-to 1600 -singlefile -png xelatex-cjk.pdf xelatex-cjk-preview
else
    printf 'Run build-support/render-xdv-fix.py with Windows Python for PDF verification\n'
fi
printf 'Two Chinese passes with automatic driver lookup and English regression passed\n'
