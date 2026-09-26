import importlib.util,json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];o=r/'validation/background-cli-1.0.28';o.mkdir(parents=True,exist_ok=True)
client=r/'tools/texstudioctl.py'
def run(*args):return subprocess.run([sys.executable,str(client),*args],capture_output=True,encoding='utf-8')
catalog=json.loads(run('help','--json').stdout)
assert len(catalog['commands'])==19
assert run().returncode==0 and '使用约定' in run().stdout
assert run('--help').returncode==0 and 'build.clean' in run('--help').stdout
for name,item in catalog['commands'].items():
    p=run('help',name,'--json');assert p.returncode==0 and json.loads(p.stdout)['command']==name
    assert run('help',name).returncode==0
    if name!='help':assert item['request']['command']==name and 'token' not in item['request']
assert run('help','nonexistent').returncode!=0
assert run('status').returncode!=0
assert run('--session','does-not-exist.json','help','build').returncode==0
header=(r/'texstudio-harmony/third_party/texstudio/src/harmonyclihelp.h').read_text(encoding='utf-8')
assert json.loads(header.split('R"CLIHELP(',1)[1].split(')CLIHELP"',1)[0])==catalog
session=(r/'build-support/project-session-function.txt').read_text(encoding='utf-8')
assert '{"help",harmonyCliHelp()}' in session
report={'passed':True,'commands':len(catalog['commands']),'checks':['offline no-argument and --help usage','all text/JSON command topics','missing session rejected for execution','help does not open missing session file','invalid topic rejected','client and C++ export catalogues identical','examples contain no token']}
(o/'host-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 19 help topics, offline usage, errors, JSON and native catalogue parity')
