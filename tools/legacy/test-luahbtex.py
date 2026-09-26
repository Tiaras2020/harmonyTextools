"""Exercise the OHOS engine under QEMU against the frozen resource baseline."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

repo = Path(os.environ['BUILD_REPO'])
root = Path(os.environ['DELIVERY_ROOT'])
out = root / 'validation/luahbtex/qemu'
out.mkdir(parents=True, exist_ok=True)
work = repo / 'build/luahbtex-test'
work.mkdir(exist_ok=True)
base = repo / 'build/resource-release-1.0.19'
engine = repo / 'build/luahbtex-ohos/texk/web2c/luahbtex'
resources = json.loads((root / 'validation/luahbtex/resources.json').read_text())
trees = [str(repo / 'build/luahbtex-resources' / name) for name in resources['packages']]
trees.append(str(base / 'texmf'))
env = os.environ.copy()
env.update(TEXMFCNF=str(base / 'texmf/web2c'), TEXMFROOT=str(base), TEXMFDIST=str(base / 'texmf'),
           TEXMF='{' + ','.join(trees) + '}', TEXMFDBS=':'.join(trees),
           TEXMFVAR=str(work / 'var'), TEXMFCACHE=str(work / 'var/cache'), TEXMFCONFIG=str(work / 'config'),
           TEXFORMATS=str(work) + '//', LUAINPUTS='.;' + ';'.join(t + '/scripts//;' + t + '/tex//;' + t + '/web2c//' for t in trees))
env['TEXINPUTS'] = '.;' + ';'.join(t + '/tex/{plain,generic,latex,xelatex,xetex,luatex}//' for t in trees)
for name in ('var', 'var/cache', 'config'):
    (work / name).mkdir(parents=True, exist_ok=True)
cmd = ['qemu-aarch64', '-L', str(repo / 'build/perl-ohos-5.40.3/qemu-root'), '-E', 'LD_LIBRARY_PATH=' + str(base / 'lib'), str(engine)]
report = {'engineSha256': hashlib.sha256(engine.read_bytes()).hexdigest(), 'execution': 'OHOS ARM64 under QEMU; not device validation', 'checks': []}
if '--reuse-format' in sys.argv and (out / 'result.json').exists():
    previous = json.loads((out / 'result.json').read_text())
    assert previous['engineSha256'] == report['engineSha256']
    report['checks'] = previous['checks']
def run(name, args):
    p = subprocess.run(cmd + args, cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
    (out / (name + '.log')).write_bytes(p.stdout)
    report['checks'] = [c for c in report['checks'] if c['name'] != name]
    report['checks'].append({'name': name, 'exitCode': p.returncode})
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(name, p.returncode, flush=True)
    if p.returncode:
        print(p.stdout.decode(errors='replace')[-4000:])
        raise SystemExit(p.returncode)
run('version', ['--version'])
if '--reuse-format' not in sys.argv:
    run('format', ['--ini', '--interaction=nonstopmode', '--halt-on-error', '--jobname=lualatex', '--progname=lualatex', 'lualatex.ini'])
(work / 'probe.lua').write_text('kpse.set_program_name("luahbtex", "lualatex")\nprint("cache env",os.getenv("TEXMFCACHE"))\nprint("cache kpse",kpse.expand_var("$TEXMFCACHE"))\nrequire("lualibs")\nprint("writable",file.is_writable(os.getenv("TEXMFCACHE")))\n')
run('cache-probe', ['--luaonly', 'probe.lua'])
(work / 'smoke.tex').write_text(r'''\documentclass{article}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}[Renderer=HarfBuzz]
\begin{document}
LuaHBTeX on HarmonyOS: office, affine, café. $E=mc^2$.
\directlua{assert(status.luatex_engine == "luahbtex"); tex.print("Lua execution passed.")}
\end{document}
''')
if '--chinese-only' not in sys.argv:
    run('harfbuzz', ['--fmt=lualatex', '--progname=lualatex', '--interaction=nonstopmode', '--halt-on-error', 'smoke.tex'])
(out / 'smoke.pdf').write_bytes((work / 'smoke.pdf').read_bytes())
(work / 'chinese.tex').write_text(r'''\documentclass[fontset=fandol]{ctexart}
\begin{document}
鸿蒙 LuaLaTeX 中文排版验证。English and 中文混排。
\section{公式与交叉引用}\label{sec:test}
$\int_0^1 x^2\,dx=\frac13$。参见第\ref{sec:test}节。
\end{document}
''')
for i in range(2):
    run('chinese-' + str(i + 1), ['--fmt=lualatex', '--progname=lualatex', '--interaction=nonstopmode', '--halt-on-error', 'chinese.tex'])
(out / 'chinese.pdf').write_bytes((work / 'chinese.pdf').read_bytes())
assert 'undefined references' not in (work / 'chinese.log').read_text().lower()
report['passed'] = all(c['exitCode'] == 0 for c in report['checks'])
(out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
