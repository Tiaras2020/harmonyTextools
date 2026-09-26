"""Run upstream Text::CSV_XS tests with the OHOS interpreter, not host Perl."""
import hashlib,json,os,pathlib,re,subprocess
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);work=repo/'build/biber-perl-5.40.3'
runtime=work/'stage/data/service/hnp/texlive.org/texlive_1.0.18';module=work/'cpan/Text-CSV_XS'
out=root/'validation/biber/xs-bootstrap/upstream';out.mkdir(exist_ok=True)
env=os.environ.copy();env['LC_ALL']='en_US.UTF-8';env['PERL5LIB']=str(runtime/'lib/perl5/5.40.3')+':'+str(runtime/'lib/perl5/5.40.3/aarch64-linux')
results=[]
for test in sorted((module/'t').glob('*.t')):
    if test.name=='99_mem.t':continue # platform memory diagnostics are separate
    # Preserve earlier output as evidence, but only reuse runs with a matching
    # interpreter/source signature and recorded successful process exit.
    signature=hashlib.sha256((runtime/'bin/perl').read_bytes()+test.read_bytes()).hexdigest()
    record=out/(test.name+'.json')
    if record.exists():
        previous=json.loads(record.read_text())
        if previous.get('signature')==signature and previous.get('passed'):
            results.append(previous);print(test.name,'cached pass',flush=True);continue
    timeout=False
    try:
        p=subprocess.run(['qemu-aarch64','-L',str(repo/'build/perl-ohos-5.40.3/qemu-root'),str(runtime/'bin/perl'),str(test)],cwd=module,env=env,capture_output=True,timeout=600 if test.name=='70_rt.t' else 90)
        stdout,stderr,code=p.stdout,p.stderr,p.returncode
    except subprocess.TimeoutExpired as e:
        stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;timeout=True
    (out/(test.name+'.stdout')).write_bytes(stdout);(out/(test.name+'.stderr')).write_bytes(stderr)
    text=stdout.decode(errors='replace');plans=re.findall(r'^1\.\.(\d+)',text,re.M)
    assertions=re.findall(r'^(?:not )?ok\b',text,re.M)
    ok=code==0 and not re.search(r'^not ok|^Bail out!',text,re.M) and bool(plans) and len(assertions)==int(plans[-1])
    item={'test':test.name,'exitCode':code,'passed':ok,'timeout':timeout,'planned':int(plans[-1]) if plans else None,'assertions':len(assertions),'signature':signature}
    record.write_text(json.dumps(item,indent=2)+'\n');results.append(item)
    print(test.name,ok,flush=True)
report={'passed':all(r['passed'] for r in results),'scope':'upstream Text::CSV_XS under OHOS Perl and QEMU/device libc; excludes memory diagnostic','tests':results}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
if not report['passed']:raise SystemExit(1)
