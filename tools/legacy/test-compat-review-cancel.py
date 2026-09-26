"""Wait for the isolated Lua CPU fixture, click Stop, verify group cleanup."""
import json, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parents[1]
out = root / 'validation/compat-review-2026-09-25'
hdc = r'E:\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe'
x, y = map(int, sys.argv[1:3])  # supplied from a fresh device screenshot
def shell(command):
    return subprocess.check_output([hdc, 'shell', command]).decode('utf-8', errors='replace')
def processes():
    result = []
    for line in shell('ps -eo pid,ppid,pgid,args').splitlines():
        fields = line.split(None, 3)
        if len(fields) == 4 and all(f.isdigit() for f in fields[:3]):
            result.append({'pid': int(fields[0]), 'ppid': int(fields[1]), 'pgid': int(fields[2]), 'command': fields[3]})
    return result
deadline = time.monotonic() + 60
while time.monotonic() < deadline:
    before = processes()
    engine = next((p for p in before if 'lualatex' in p['command'] and '04-cancel' in p['command'] and '/bin/perl' not in p['command']), None)
    if engine and any(p['pgid'] == engine['pgid'] and 'latexmk.pl' in p['command'] for p in before): break
    time.sleep(0.5)
else: raise SystemExit('Lua cancellation fixture did not start')
group = [p for p in before if p['pgid'] == engine['pgid']]
assert any('latexmk.pl' in p['command'] for p in group), group
shell(f'uitest uiInput click {x} {y}')
time.sleep(2)
remaining = [p for p in processes() if p['pgid'] == engine['pgid']]
report = {'passed': not remaining, 'groupBefore': group, 'remaining': remaining}
(out / 'cancel-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
assert report['passed'], 'Cancelled Lua build left child processes running'
