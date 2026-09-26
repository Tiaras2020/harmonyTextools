"""Audit official Biber 2.21 requirements against the actual OHOS Perl build."""
import hashlib, json, os, pathlib, re, subprocess
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'validation/biber'
source=out/'Build.PL'
section=source.read_text().split('    requires => {',1)[1].split('\n                },',1)[0]
requirements=dict(re.findall(r"'([^']+)'\s*=>\s*'?([\d.]+)'?",section))
requirements.pop('perl')
probe=out/'module-probe.pl'
probe.write_text('use strict; use warnings; use JSON::PP; my @r;\n'+
 '\n'.join("{ my $m='"+module+"'; my $ok=eval \"require $m; $m->VERSION("+minimum+"); 1\"; push @r,{module=>$m,minimum=>'"+minimum+"',available=>$ok?JSON::PP::true:JSON::PP::false,error=>$ok?'':\"$@\"}; }" for module,minimum in requirements.items())+
 '\nprint encode_json(\\@r),"\\n";\n')
repo=pathlib.Path(os.environ['BUILD_REPO']); work=repo/'build/perl-ohos-5.40.3'
runtime=work/'stage/data/service/hnp/texlive.org/texlive_1.0.17'
env=os.environ.copy();env['LC_ALL']='en_US.UTF-8'
env['PERL5LIB']=str(runtime/'lib/perl5/5.40.3')+':'+str(runtime/'lib/perl5/5.40.3/aarch64-linux')
p=subprocess.run(['qemu-aarch64','-L',str(work/'qemu-root'),str(runtime/'bin/perl'),str(probe)],env=env,capture_output=True,text=True,check=True)
assert not p.stderr,p.stderr
modules=json.loads(p.stdout)
result={'biberVersion':'2.21','biblatexVersion':'3.21','source':'https://github.com/plk/biber/blob/v2.21/Build.PL',
 'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'OHOS Perl under QEMU, dependency loading only; not Biber execution or device acceptance',
 'runtimeRequirements':len(modules),'available':sum(m['available'] for m in modules),'modules':modules}
(out/'dependency-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='modules'},indent=2))
