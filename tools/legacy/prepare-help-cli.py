from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
p=r/'build-support/project-session-function.txt';s=p.read_text(encoding='utf-8')
s=s.replace('{"token",s->server.token}}).toJson()', '{"token",s->server.token},{"appVersion",HARMONY_TEX_VERSION},{"projectRoot",s->root},{"help",harmonyCliHelp()}}).toJson()')
s=s.replace('        if(cmd=="capabilities")', '        if(cmd=="help")return {{"ok",true},{"help",harmonyCliHelp()}};\n        if(cmd=="capabilities")')
s=s.replace('{"commands",QJsonArray{"capabilities"', '{"commands",QJsonArray{"help","capabilities"')
p.write_text(s,encoding='utf-8')
p=r/'texstudio-harmony/third_party/texstudio/src/texstudio.cpp';t=p.read_text(encoding='utf-8')
a=t.index('void Texstudio::harmonyAutomationSession()');b=t.index('void Texstudio::harmonyCleanRebuild()',a)
t=t[:a]+s+t[b:]
if '#include "harmonyclihelp.h"' not in t:t='#include "harmonyclihelp.h"\n'+t
p.write_text(t,encoding='utf-8')
p=r/'build-support/sync-baseline.py';t=p.read_text(encoding='utf-8');t=t.replace('report = []',"paths += ['third_party/texstudio/src/harmonyclihelp.h']\nreport = []");p.write_text(t,encoding='utf-8')
p=r/'texstudio-harmony/release.json';d=json.loads(p.read_text());d.update(version='1.0.27',versionCode=1000027);p.write_text(json.dumps(d,indent=2)+'\n')
for a,b in [('build-refresh-cli.sh','build-help-cli.sh'),('stage-refresh-cli-app.sh','stage-help-cli-app.sh'),('assemble-refresh-cli-package.py','assemble-help-cli-package.py'),('check-refresh-cli-package.py','check-help-cli-package.py')]:
    t=(r/'build-support'/a).read_text().replace('refresh-cli-1.0.26','help-cli-1.0.27').replace('1.0.26','1.0.27').replace('1000026','1000027').replace('build-refresh-cli.sh','build-help-cli.sh').replace('check-refresh-cli-package.py','check-help-cli-package.py')
    (r/'build-support'/b).write_text(t,encoding='utf-8',newline='\n')
print('Prepared CLI help 1.0.27')
