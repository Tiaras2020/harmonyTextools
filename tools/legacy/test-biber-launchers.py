"""Host-side argument and process-group regression for the two C entry points."""
import json,os,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);prefix=repo/'build/biber-launcher-test'
(prefix/'bin').mkdir(parents=True,exist_ok=True)
fake=prefix/'bin/perl';fake.write_text('''#!/usr/bin/python3
import json,os,pathlib,subprocess,sys
r={"argv":sys.argv[1:],"pid":os.getpid(),"pgid":os.getpgrp()}
if any(a.endswith("latexmk.pl") for a in sys.argv):
    r["child"]=json.loads(subprocess.check_output([str(pathlib.Path(__file__).parent/"biber"),"child with spaces.bcf"]))
print(json.dumps(r))
''');fake.chmod(0o755)
for name in ('latexmk','biber'):
    subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror','-DHARMONY_RUNTIME_ROOT="'+str(prefix)+'"',str(root/'texstudio-harmony/scripts/texlive'/(name+'_launcher.c')),'-o',str(prefix/'bin'/name)],check=True)
env=os.environ.copy();env.pop('HARMONY_BUILD_PROCESS_GROUP',None)
args=['中文 空格.bcf','quotes\'";$literal']
direct=json.loads(subprocess.check_output([str(prefix/'bin/biber'),*args],env=env));assert direct['argv'][-2:]==args and direct['pid']==direct['pgid']
env['HARMONY_BUILD_PROCESS_GROUP']='not-a-group'
invalid=json.loads(subprocess.check_output([str(prefix/'bin/biber'),'invalid-marker.bcf'],env=env));assert invalid['pid']==invalid['pgid']
nested=json.loads(subprocess.check_output([str(prefix/'bin/latexmk'),'main.tex'],env=env))
assert nested['pid']==nested['pgid']==nested['child']['pgid'] and nested['pid']!=nested['child']['pid']
report={'passed':True,'scope':'native launcher logic on host Linux; device cancellation still required',
 'checks':['literal arguments preserved','direct Biber owns its process group','invalid inherited marker rejected','latexmk child Biber stays in parent build group']}
(root/'validation/biber/launcher-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
