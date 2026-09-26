"""Run selected upstream XML and all functional BibTeX tests on OHOS Perl."""
import hashlib,json,os,pathlib,re,subprocess,tarfile
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO'])
work=repo/'build/biber-perl-5.40.3';runtime=work/'stage/data/service/hnp/texlive.org/texlive_1.0.18'
out=root/'validation/biber/native/upstream';out.mkdir(exist_ok=True)
support=repo/'build/biber-native/test-support';support.mkdir(exist_ok=True)
lock=json.loads((root/'validation/biber/dependencies.lock.json').read_text())
record=next(r for r in lock['distributions'] if r['distribution']=='Capture-Tiny')
archive=root/'validation/biber/downloads'/record['archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==record['sha256']
with tarfile.open(archive) as t:
    for m in t.getmembers():
        parts=pathlib.PurePosixPath(m.name).parts
        if len(parts)>2 and parts[1]=='lib':
            m.name=str(pathlib.PurePosixPath(*parts[2:]));t.extract(m,support,filter='data')
env=os.environ.copy();env['LC_ALL']='en_US.UTF-8'
env['PERL5LIB']=':'.join(map(str,[runtime/'lib/perl5/5.40.3',runtime/'lib/perl5/5.40.3/aarch64-linux',support]))
suites={
 'Text-BibTeX':[p.name for p in sorted((work/'cpan/Text-BibTeX/t').glob('*.t')) if p.name!='00_system_info.t'],
 'XML-LibXML':['01basic.t','02parse.t','08findnodes.t','09xpath.t','19encoding.t','25relaxng.t','26schema.t'],
 'XML-LibXSLT':['01basic.t','04params.t','09exslt.t','11utf8.t','13error.t','14security.t']}
results=[]
for name,tests in suites.items():
    module=work/'cpan'/name
    for test in tests:
        timeout=False
        try:
            p=subprocess.run(['qemu-aarch64','-L',str(repo/'build/perl-ohos-5.40.3/qemu-root'),str(runtime/'bin/perl'),'t/'+test],cwd=module,env=env,capture_output=True,timeout=120)
            stdout,stderr,code=p.stdout,p.stderr,p.returncode
        except subprocess.TimeoutExpired as e:
            stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;timeout=True
        base=out/(name+'-'+test)
        base.with_suffix(base.suffix+'.stdout').write_bytes(stdout);base.with_suffix(base.suffix+'.stderr').write_bytes(stderr)
        text=stdout.decode(errors='replace');plans=re.findall(r'^1\.\.(\d+)',text,re.M)
        assertions=re.findall(r'^(?:not )?ok\b',text,re.M)
        ok=code==0 and not re.search(r'^not ok|^Bail out!',text,re.M) and bool(plans) and len(assertions)==int(plans[-1])
        results.append({'module':name,'test':test,'exitCode':code,'passed':ok,'timeout':timeout,'planned':int(plans[-1]) if plans else None,'assertions':len(assertions)})
        print(name,test,ok,flush=True)
        (out/'result.json').write_text(json.dumps({'complete':False,'tests':results},indent=2)+'\n')
report={'complete':True,'passed':all(r['passed'] for r in results),'scope':'selected upstream tests under OHOS Perl and QEMU with device libc; no device installation',
 'interpreterSha256':hashlib.sha256((runtime/'bin/perl').read_bytes()).hexdigest(),'tests':results}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
if not report['passed']:raise SystemExit(1)
