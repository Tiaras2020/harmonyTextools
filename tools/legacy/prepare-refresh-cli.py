"""Apply the reviewed 1.0.26 delta; do not replay after subsequent development."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
p=r/'build-support/project-session-function.txt'
s=p.read_text(encoding='utf-8')
s=s.replace('"master.set","build","job.status"','"master.set","project.refresh","build","build.clean","job.status"')
s=s.replace('{"writes",false}', '{"okMeaning","request_succeeded_not_build_succeeded"},{"externalRefresh","content-hash polling and preflight"},{"writes",false}')
needle='        if(cmd=="documents.list") {'
s=s.replace(needle,'''        // Refresh before exposing buffers or selecting a build. Never save here.
        if(QStringList{"project.refresh","documents.list","document.read","document.open","master.set","build","build.clean"}.contains(cmd)) {
            const auto views=editors->editors();
            for(LatexEditorView *v:views) {
                const QString relative=rel(v->document->getFileName());
                if(relative!=".."&&!relative.startsWith("../")&&!QDir::isAbsolutePath(relative))v->editor->refreshExternalChanges();
            }
        }
        if(cmd=="documents.list"||cmd=="project.refresh") {''')
start=s.index('            if(cmd=="diagnostics") {')
end=s.index('            const QString pdf=',start)
s=s[:start]+'''            if(cmd=="diagnostics")return HarmonyProject::diagnostics(j,s->root);
'''+s[end:]
s=s.replace('if(cmd!="build")','if(cmd!="build"&&cmd!="build.clean")')
s=s.replace('j.started=QDateTime::currentDateTimeUtc();','j.started=QDateTime::currentDateTimeUtc();j.cleanRebuild=cmd=="build.clean";')
needle='        s->jobs.insert(j.id,j);'
s=s.replace(needle,'''        if(j.cleanRebuild) {
            const QString cache=QFileInfo(path).absolutePath()+'/'+QFileInfo(path).completeBaseName()+".fdb_latexmk";
            if(QFileInfo(cache).exists()||QFileInfo(cache).isSymLink()) {
                const QString safe=HarmonyProject::resolve(s->root,rel(cache));
                if(safe.isEmpty())return error("unsafe_cache_path");
                if(!QFile::remove(safe))return error("cache_remove_failed");
            }
        }
'''+needle)
s=s.replace('auto &job=s->jobs[s->currentJob];\n            if(job.cancelled)', '''auto &job=s->jobs[s->currentJob];
            bool edits=false;
            for(LatexEditorView *v:editors->editors()) {
                v->editor->refreshExternalChanges();
                edits=edits||v->editor->isContentModified()||v->editor->isInConflict();
            }
            if(edits){job.state="failed";job.exitCode=-1;job.append("Unsaved edits or external conflict before build\\n");}
            else if(job.cancelled)''')
s=s.replace('[-file-line-error]").arg(flag)', '[-file-line-error]%2").arg(flag,job.cleanRebuild?"[-g]":"")')
s=s.replace('            job.finished=QDateTime::currentDateTimeUtc();', '''            // Capture now, so later jobs cannot overwrite this task's diagnostics.
            const QString logPath=QFileInfo(path).absolutePath()+'/'+QFileInfo(path).completeBaseName()+".log";
            const QString safeLog=HarmonyProject::resolve(s->root,QDir(s->root).relativeFilePath(logPath));
            if(!safeLog.isEmpty()&&job.log.contains("Transcript written on ")) {
                QFile file(safeLog);
                if(file.size()<=2*1024*1024&&file.open(QIODevice::ReadOnly)) {
                    job.finalLog=QString::fromUtf8(file.readAll());job.finalLogAvailable=true;
                }
            }
            job.finished=QDateTime::currentDateTimeUtc();''')
s=s.replace('return {{"ok",true},{"job",j.id},{"state","queued"}};', 'return j.status();')
p.write_text(s,encoding='utf-8')
p=r/'texstudio-harmony/third_party/texstudio/src/texstudio.cpp';t=p.read_text(encoding='utf-8')
a=t.index('void Texstudio::harmonyAutomationSession()');b=t.index('void Texstudio::harmonyCleanRebuild()',a)
p.write_text(t[:a]+s+t[b:],encoding='utf-8')
p=r/'build-support/sync-baseline.py';t=p.read_text(encoding='utf-8')
t=t.replace('report = []',"paths += ['third_party/texstudio/src/qcodeedit/lib/' + name for name in ('qeditor.cpp','qeditor.h','qreliablefilewatch.cpp','qreliablefilewatch.h')]\nreport = []")
p.write_text(t,encoding='utf-8')
p=r/'texstudio-harmony/release.json';d=json.loads(p.read_text());d.update(version='1.0.26',versionCode=1000026);p.write_text(json.dumps(d,indent=2)+'\n')
for a,b in [('build-project-cli.sh','build-refresh-cli.sh'),('stage-project-cli-app.sh','stage-refresh-cli-app.sh'),('assemble-project-cli-package.py','assemble-refresh-cli-package.py'),('check-project-cli-package.py','check-refresh-cli-package.py')]:
    t=(r/'build-support'/a).read_text().replace('project-cli-1.0.25','refresh-cli-1.0.26').replace('1.0.25','1.0.26').replace('1000025','1000026').replace('build-project-cli.sh','build-refresh-cli.sh').replace('check-project-cli-package.py','check-refresh-cli-package.py')
    (r/'build-support'/b).write_text(t,encoding='utf-8',newline='\n')
print('Prepared 1.0.26')
