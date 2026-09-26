from pathlib import Path
import json, shutil
r=Path(__file__).resolve().parents[1]
src=r/'texstudio-harmony/third_party/texstudio/src'
out=r/'validation/project-cli-1.0.25'
(out/'before').mkdir(parents=True,exist_ok=True)
for name in ['texstudio.cpp','texstudio.h','spellerutility.cpp']:
    dst=out/'before'/name
    if not dst.exists():shutil.copy2(src/name,dst)
p=src/'texstudio.cpp';s=p.read_text(encoding='utf-8')
start=s.index('void Texstudio::harmonyAutomationSession()')
end=s.index('void Texstudio::harmonyCleanRebuild()',start)
s=s[:start]+(r/'build-support/project-session-function.txt').read_text(encoding='utf-8')+s[end:]
if '#include "harmonyproject.h"' not in s:s='#include "harmonyproject.h"\n#include <QFileDialog>\n'+s
p.write_text(s,encoding='utf-8')
p=src/'texstudio.h';s=p.read_text(encoding='utf-8')
if 'QPointer<QDialog> harmonyProjectPanel' not in s:s=s.replace('    void harmonyAutomationSession();','    QPointer<QDialog> harmonyProjectPanel;\n    void harmonyAutomationSession();')
p.write_text(s,encoding='utf-8')
p=src/'spellerutility.cpp';s=p.read_text(encoding='utf-8')
if '#include "harmonyspell.h"' not in s:
    s='#include "harmonyspell.h"\n'+s
    s=s.replace('bool SpellerUtility::check(QString word)\n{','''bool SpellerUtility::check(QString word)
{
#ifdef Q_OS_OHOS
    const QStringList parts = harmonySpellParts(word);
    if (parts != QStringList{word}) {
        for (const QString &part : parts) if (!check(part)) return false;
        return true;
    }
#endif''')
p.write_text(s,encoding='utf-8')
p=r/'build-support/sync-baseline.py';s=p.read_text(encoding='utf-8')
if "'harmonyproject.h'" not in s:s=s.replace('report = []',"paths += ['third_party/texstudio/src/' + name for name in ('harmonyproject.h', 'harmonyspell.h', 'spellerutility.cpp')]\nreport = []")
p.write_text(s,encoding='utf-8')
p=r/'texstudio-harmony/release.json';d=json.loads(p.read_text());d['version']='1.0.25';d['versionCode']=1000025;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for source,target in [('build-interaction.sh','build-project-cli.sh'),('stage-interaction-app.sh','stage-project-cli-app.sh'),('assemble-interaction-package.py','assemble-project-cli-package.py'),('check-interaction-package.py','check-project-cli-package.py')]:
    text=(r/'build-support'/source).read_text(encoding='utf-8').replace('interaction-1.0.24','project-cli-1.0.25').replace('1.0.24','1.0.25').replace('1000024','1000025').replace('build-interaction.sh','build-project-cli.sh').replace('check-interaction-package.py','check-project-cli-package.py')
    (r/'build-support'/target).write_text(text,encoding='utf-8',newline='\n')
print('Prepared project CLI 1.0.25 source and build scripts')
