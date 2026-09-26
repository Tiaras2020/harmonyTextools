"""Run the staged public command with only host-location overrides."""
import json, os, subprocess
from pathlib import Path
repo = Path(os.environ['BUILD_REPO'])
root = Path(os.environ['DELIVERY_ROOT'])
candidate = repo / 'build/resource-release-1.0.20'
out = root / 'validation/luahbtex/candidate'
out.mkdir(exist_ok=True)
work = repo / 'build/luahbtex-candidate-test'
work.mkdir(exist_ok=True)
(work / 'home').mkdir(exist_ok=True)
(work / 'plain.tex').write_text(r'\documentclass{article}\begin{document}Public LuaLaTeX command.\end{document}' + '\n')
env = {k: v for k, v in os.environ.items() if not k.startswith(('TEX', 'LUA', 'LD_'))}
env.update(HOME=str(work / 'home'), TEXMFROOT=str(candidate), TEXMFCNF=str(candidate / 'texmf/web2c'))
cmd = ['qemu-aarch64', '-L', str(repo / 'build/perl-ohos-5.40.3/qemu-root'), str(candidate / 'bin/lualatex'), '-interaction=nonstopmode', '-halt-on-error', 'plain.tex']
p = subprocess.run(cmd, cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
(out / 'public-command.log').write_bytes(p.stdout)
cache = work / 'home/.texstudio/luahbtex-1.21'
report = {'exitCode': p.returncode, 'defaultCacheCreated': cache.is_dir(), 'publicCommand': 'lualatex', 'hostOverrides': ['HOME', 'TEXMFROOT', 'TEXMFCNF'], 'explicitFormatOrLibraryPath': False}
report['passed'] = p.returncode == 0 and cache.is_dir() and (work / 'plain.pdf').is_file()
(out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
if not report['passed']:
    print(p.stdout.decode(errors='replace')[-3500:])
    raise SystemExit(1)
