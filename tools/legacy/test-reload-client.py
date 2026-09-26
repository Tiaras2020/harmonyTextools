import contextlib,io,importlib.util,json,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];o=r/'validation/reload-cli-1.0.29'
spec=importlib.util.spec_from_file_location('ctl',r/'tools/texstudioctl.py');ctl=importlib.util.module_from_spec(spec);spec.loader.exec_module(ctl)
session=o/'dummy-session.json';session.write_text('{}')
calls=[]
def request(*args,**kw):calls.append((args,kw));return {'ok':True}
ctl.request=request
def run(*args):
    sys.argv=['texstudioctl.py','--session',str(session),*args]
    with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        try:return ctl.main()
        except SystemExit as e:return e.code
assert run('document.reload','--path','main.tex','--discard-local')==2 and not calls
assert run('build','--discard-local','--expected-revision','REV')==2 and not calls
assert run('document.reload','--path','main.tex','--discard-local','--expected-revision','REV')==0
assert calls[-1][1]=={'path':'main.tex','discardLocal':True,'expectedRevision':'REV'}
assert run('document.reload','--path','main.tex')==0 and calls[-1][1]=={'path':'main.tex','discardLocal':False}
(o/'client-tests.json').write_text(json.dumps({'passed':True,'checks':['required revision before connecting','reload-only parameters','camelCase wire parameters','safe default']},indent=2))
print('PASS: client validation and reload wire parameters')
