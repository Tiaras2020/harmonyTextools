"""WSL host regression against frozen Harmony resources, with recorder isolation."""
import json
import os
import pathlib
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

root = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
dist = pathlib.Path(os.environ.get('HARMONY_TEST_DIST', str(repo / 'build/build-texlive-ohos-dist')))
out = pathlib.Path(os.environ.get('HARMONY_TEST_OUTPUT', str(root / 'validation/baseline/regression')))
out.mkdir(parents=True, exist_ok=True)
fixtures = root / 'validation/baseline/fixtures'
fixtures.mkdir(exist_ok=True)
for name in ('pdflatex-basic.tex', 'xelatex-cjk.tex'):
    if not (fixtures / name).exists():
        shutil.copy2(root / 'validation' / name, fixtures / name)
mcm = fixtures / 'mcm'
if not mcm.exists():
    shutil.copytree(root / 'validation/mcm-project/project', mcm,
                    ignore=shutil.ignore_patterns('*.aux', '*.log', '*.fls', '*.out', '*.toc', '*.bcf', '*.run.xml', '*.synctex.gz', 'mcmthesis-demo.pdf', '*-blx.bib'))
env = os.environ.copy()
for key in list(env):
    if key.startswith(('TEX', 'BIB', 'BST', 'FONT', 'TFM', 'VFF', 'LUAINPUTS')):
        del env[key]
texmf = dist / 'texmf'
env.update(TEXMFROOT=str(dist), TEXMFDIST=str(texmf), TEXMF=str(texmf), TEXMFCNF=str(texmf / 'web2c'),
           TEXMFHOME=str(out / 'empty-home'), TEXMFVAR=str(out / 'var'), TEXMFCONFIG=str(out / 'config'))
for name in ('empty-home', 'var', 'config', 'font-cache'):
    (out / name).mkdir(exist_ok=True)
fc = ET.Element('fontconfig')
for name in ('opentype', 'truetype'):
    ET.SubElement(fc, 'dir').text = str(texmf / 'fonts' / name)
ET.SubElement(fc, 'cachedir').text = str(out / 'font-cache')
ET.ElementTree(fc).write(out / 'fonts.conf', encoding='utf-8', xml_declaration=True)
env['FONTCONFIG_FILE'] = str(out / 'fonts.conf')
web2c = repo / 'build/build-texlive-host/texk/web2c'
driver = repo / 'build/build-texlive-host/texk/dvipdfm-x/xdvipdfmx'
env['PATH'] = str(driver.parent) + ':' + env['PATH']
report = {'scope': 'host engines with Harmony runtime resources; not device acceptance', 'cases': {}, 'passed': False}
release = json.loads((root / 'texstudio-harmony/release.json').read_text())


def pdf_tool(name, path):
    native = shutil.which(name)
    if native:
        return subprocess.check_output([native, str(path)], text=True)
    windows = {'pdfinfo': '/mnt/c/Users/1/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdfinfo.exe',
               'pdffonts': '/mnt/e/texlive/2024/bin/windows/pdffonts.exe'}
    converted = subprocess.check_output(['wslpath', '-w', str(path)], text=True).strip()
    return subprocess.check_output([windows[name], converted], text=True, encoding='utf-8', errors='replace')

try:
    fonts = subprocess.check_output(['fc-list', '-f', '%{file}\n'], env=env, text=True).splitlines()
    assert fonts and all(pathlib.Path(p).is_relative_to(texmf) for p in fonts), 'Foreign font discovered'
    report['fontFaces'] = len(fonts)
    cases = [
        ('english', fixtures, 'pdflatex-basic', 'pdftex', 1),
        ('中文 空格路径', fixtures, 'xelatex-cjk', 'xetex', 2),
        ('mcm', mcm, 'mcmthesis-demo', 'pdftex', 3),
    ]
    if os.environ.get('HARMONY_EXTRA_FIXTURES'):
        extra = pathlib.Path(os.environ['HARMONY_EXTRA_FIXTURES'])
        cases += [('new-packages', extra, 'new-packages', 'pdftex', 2),
                  ('new-type1-font', extra, 'new-type1-font', 'pdftex', 1)]
    if os.environ.get('HARMONY_COMMON_FIXTURES'):
        common = pathlib.Path(os.environ['HARMONY_COMMON_FIXTURES'])
        cases += [(name, common, name, engine, passes) for name, engine, passes in (
            ('beamer-zh', 'xetex', 2), ('pgfplots-test', 'pdftex', 2),
            ('newpx-test', 'pdftex', 2), ('bibtex-zh', 'xetex', 3))]
    for case, source, name, engine, passes in cases:
        work = out / case
        work.mkdir(exist_ok=True)
        if case == 'mcm':
            shutil.copytree(source, work, dirs_exist_ok=True)
        else:
            shutil.copy2(source / (name + '.tex'), work)
            if case in ('pgfplots-test', 'bibtex-zh'):
                for companion in source.glob('*.csv' if case == 'pgfplots-test' else '*.bib'):
                    shutil.copy2(companion, work)
        command = [str(web2c / engine), '-progname=' + ('xelatex' if engine == 'xetex' else 'pdflatex'),
                   '-recorder', '-interaction=nonstopmode', '-halt-on-error']
        if engine == 'xetex':
            command.append('-output-driver=' + str(driver) + ' -q -E')
        for index in range(passes):
            proc = subprocess.run(command + [name + '.tex'], cwd=work, env=env, capture_output=True)
            (work / f'pass-{index + 1}.stdout').write_bytes(proc.stdout + proc.stderr)
            assert proc.returncode == 0, f'{case}: TeX exit {proc.returncode}'
            if case == 'bibtex-zh' and index == 0:
                bib = subprocess.run([str(web2c / 'bibtex'), name], cwd=work, env=env, capture_output=True)
                (work / 'bibtex.stdout').write_bytes(bib.stdout + bib.stderr)
                assert bib.returncode == 0, f'BibTeX exit {bib.returncode}'
                bbl = (work / (name + '.bbl')).read_text()
                assert all(key in bbl for key in ('knuth1984', 'lamport1994')), 'Missing bibliography entry'
        foreign = []
        for line in (work / (name + '.fls')).read_text().splitlines():
            if line.startswith('INPUT '):
                path = pathlib.Path(line[6:])
                path = (work / path).resolve() if not path.is_absolute() else path.resolve()
                if not path.is_relative_to(texmf.resolve()) and not path.is_relative_to(work.resolve()):
                    foreign.append(str(path))
        assert not foreign, f'Foreign TeX inputs: {foreign}'
        log = (work / (name + '.log')).read_text()
        if case in ('beamer-zh', 'pgfplots-test', 'newpx-test', 'bibtex-zh'):
            assert not re.search(r'undefined (references|citations)|Missing character:|Font shape .*undefined', log), 'Unresolved references or missing glyph/font: ' + case
        assert release['formatKernel'] in log, 'Format kernel differs from locked compatibility profile'
        assert 'L3 programming layer <' + release['l3Layer'] + '>' in log, 'L3 layer differs from compatibility profile'
        info = pdf_tool('pdfinfo', work / (name + '.pdf'))
        pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M)[1])
        font_lines = pdf_tool('pdffonts', work / (name + '.pdf'))
        (work / 'pdffonts.txt').write_text(font_lines)
        font_rows = font_lines.splitlines()[2:]
        assert font_rows and all(row.split()[-5] == 'yes' for row in font_rows), 'Unembedded font'
        if case == 'mcm':
            assert pages == 17, f'MCM page count changed: {pages}'
        if engine == 'xetex':
            assert 'undefined references' not in (work / (name + '.log')).read_text(), 'Unresolved CJK reference'
        report['cases'][case] = {'passed': True, 'pages': pages, 'fontCount': len(font_rows), 'allFontsEmbedded': True, 'foreignInputs': foreign}
    report['passed'] = True
except Exception as exc:
    report['error'] = str(exc)
finally:
    (out / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(not report['passed'])
