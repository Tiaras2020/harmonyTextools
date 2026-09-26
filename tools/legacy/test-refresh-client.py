import contextlib,importlib.util,io,json,sys,tempfile
from pathlib import Path
r=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ctl',r/'tools/texstudioctl.py');ctl=importlib.util.module_from_spec(spec);spec.loader.exec_module(ctl)
checks=[]
with contextlib.nullcontext(r/'validation/refresh-cli-1.0.26/client-fixture') as tmp:
    Path(tmp).mkdir(exist_ok=True)
    descriptor=Path(tmp)/'session.json';descriptor.write_text('{}')
    for command in ['build','build.clean']:
        for state,code in [('succeeded',0),('failed',1),('cancelled',1)]:
            responses=iter([{'ok':True,'job':'one','state':'queued','buildSucceeded':None},
                {'ok':True,'job':'one','state':state,'terminal':True,'buildSucceeded':state=='succeeded'}])
            calls=[]
            def request(session,cmd,engine=None,**kw):calls.append((cmd,engine,kw));return next(responses)
            ctl.request=request
            sys.argv=['ctl','--session',str(descriptor),command,'--engine','pdflatex','--wait']
            with contextlib.redirect_stdout(io.StringIO()): actual=ctl.main()
            assert actual==code and calls[0][0]==command and calls[0][1]=='pdflatex' and calls[1][2]['job']=='one'
            checks.append(command+':'+state)
(r/'validation/refresh-cli-1.0.26/client-tests.json').write_text(json.dumps({'passed':True,'checks':checks},indent=2))
print('PASS: client build/build.clean waits and success/failure/cancellation exit codes')
