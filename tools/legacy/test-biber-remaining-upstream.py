"""Selected upstream tests for the second batch of OHOS static modules."""
import hashlib,json,os,pathlib,re,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);work=repo/'build/biber-perl-5.40.3'
runtime=work/'stage/data/service/hnp/texlive.org/texlive_1.0.18';out=root/'validation/biber/remaining-upstream';out.mkdir(exist_ok=True)
env=os.environ.copy();env['LC_ALL']='en_US.UTF-8';env['PERL5LIB']=':'.join(map(str,[repo/'build/biber-test-support',repo/'build/biber-runtime/lib',runtime/'lib/perl5/5.40.3',runtime/'lib/perl5/5.40.3/aarch64-linux']))
suites={'PerlIO-utf8_strict':sorted(p.name for p in (work/'cpan/PerlIO-utf8_strict/t').glob('*.t')),
 'Sort-Key':['ints.t','floats.t','strings.t','natural.t','multi.t'],
 'Unicode-LineBreak':['01break.t','02hangul.t','04fold.t','08partial.t','10gcstring.t','15array.t','16regex.t'],
 'DateTime':['00load.t','01sanity.t','04epoch.t','07compare.t','14locale.t'],
 'Encode-HanExtra':['1-basic.t','2-alias.t'],
 'Net-SSLeay':['local/03_use.t','local/04_basic.t','local/09_ctx_new.t','local/10_rand.t','local/15_bio.t','local/20_functions.t']}
results=[];previous={}
if '--failed-only' in sys.argv and (out/'result.json').exists():
    old=json.loads((out/'result.json').read_text())
    assert old['interpreterSha256']==hashlib.sha256((runtime/'bin/perl').read_bytes()).hexdigest()
    previous={(r['module'],r['test']):r for r in old['tests'] if r['passed']}
for name,tests in suites.items():
    module=work/'cpan'/name
    for test in tests:
        if (name,test) in previous:
            results.append(previous[(name,test)]);print(name,test,'previous pass retained',flush=True);continue
        p=subprocess.run(['qemu-aarch64','-L',str(repo/'build/perl-ohos-5.40.3/qemu-root'),str(runtime/'bin/perl'),'-It/lib','t/'+test],cwd=module,env=env,capture_output=True,timeout=180)
        base=out/(name+'-'+test.replace('/','-'));path=pathlib.Path(str(base)+'.stdout');path.write_bytes(p.stdout);pathlib.Path(str(base)+'.stderr').write_bytes(p.stderr)
        text=p.stdout.decode(errors='replace');plans=re.findall(r'^1\.\.(\d+)',text,re.M);assertions=re.findall(r'^(?:not )?ok\b',text,re.M)
        ok=p.returncode==0 and not re.search(r'^not ok|^Bail out!',text,re.M) and bool(plans) and len(assertions)==int(plans[-1])
        results.append({'module':name,'test':test,'exitCode':p.returncode,'passed':ok,'planned':int(plans[-1]) if plans else None,'assertions':len(assertions),'skipped':bool(re.search(r'^1\.\.0\s+#\s*SKIP',text,re.I|re.M))})
        print(name,test,ok,flush=True)
        (out/'result.json').write_text(json.dumps({'complete':False,'tests':results},indent=2)+'\n')
report={'complete':True,'passed':all(t['passed'] for t in results),'scope':'selected upstream tests under OHOS Perl/QEMU',
 'interpreterSha256':hashlib.sha256((runtime/'bin/perl').read_bytes()).hexdigest(),'tests':results}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
if not report['passed']:raise SystemExit(1)
