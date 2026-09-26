"""Check Biber's direct module requirements against the assembled OHOS runtime."""
import hashlib,json,os,pathlib,re,subprocess
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);out=pathlib.Path(os.environ.get('BIBER_TEST_OUT',root/'validation/biber'))
work=repo/'build/biber-perl-5.40.3';runtime=pathlib.Path(os.environ.get('BIBER_RUNTIME',work/'stage/data/service/hnp/texlive.org/texlive_1.0.18'));overlay=pathlib.Path(os.environ.get('BIBER_OVERLAY',repo/'build/biber-runtime'))
source=(root/'validation/biber/Build.PL').read_text();section=source.split('    requires => {',1)[1].split('\n                },',1)[0]
requirements=dict(re.findall(r"'([^']+)'\s*=>\s*'?([\d.]+)'?",section));requirements.pop('perl')
probe=out/'assembled-module-probe.pl'
probe.write_text('use strict; use warnings; use JSON::PP; my @r;\n'+
 '\n'.join("{ my $m='"+module+"'; my $ok=eval \"require $m; $m->VERSION("+minimum+"); 1\"; push @r,{module=>$m,minimum=>'"+minimum+"',available=>$ok?JSON::PP::true:JSON::PP::false,error=>$ok?'':\"$@\"}; }" for module,minimum in requirements.items())+
 '\nprint encode_json(\\@r),"\\n";\n')
env=os.environ.copy();env['LC_ALL']='en_US.UTF-8';env['PERL5LIB']=':'.join(map(str,[overlay/'lib',runtime/'lib/perl5/5.40.3',runtime/'lib/perl5/5.40.3/aarch64-linux']))
p=subprocess.run(['qemu-aarch64','-L',str(repo/'build/perl-ohos-5.40.3/qemu-root'),str(runtime/'bin/perl'),str(probe)],env=env,capture_output=True,timeout=180)
(out/'assembled-module-probe.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode(errors='replace')
modules=json.loads(p.stdout);report={'passed':all(m['available'] for m in modules) and not p.stderr,'modules':modules,'directModules':len(modules),
 'available':sum(m['available'] for m in modules),'interpreterSha256':hashlib.sha256((runtime/'bin/perl').read_bytes()).hexdigest()}
(out/'assembled-dependency-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='modules'},indent=2))
for m in modules:
    if not m['available']:print(m['module'],m['error'][:500])
if not report['passed']:raise SystemExit(1)
