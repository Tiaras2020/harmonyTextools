from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
assert json.loads((r/'texstudio-harmony/release.json').read_text())['version']=='1.0.27', 'One-time migration from 1.0.27 only'
src=r/'texstudio-harmony/third_party/texstudio/src'
p=src/'harmonyproject.h';t=p.read_text(encoding='utf-8')
t=t.replace('inline QString digest(','''// Buffer membership must not depend on whether its disk file still exists.
// This is only for listing/preflight, never for authorizing disk reads or writes.
inline QString documentPath(const QString &root, const QString &filename) {
    if (filename.isEmpty() || !QDir::isAbsolutePath(filename)) return {};
    const QString path=QDir(root).relativeFilePath(QDir::cleanPath(filename));
    if(path==".." || path.startsWith("../") || QDir::isAbsolutePath(path)) return {};
    return path;
}
inline QString digest(''')
t=t.replace('bool finalLogAvailable = false', 'QJsonArray blockers;\n    bool finalLogAvailable = false')
t=t.replace('{"terminal",terminal}', '{"blockers",blockers},{"terminal",terminal}')
t=t.replace('bool running = false;', 'bool connected = false;\n    bool running = false;')
p.write_text(t,encoding='utf-8')
p=r/'build-support/project-session-function.txt';s=p.read_text(encoding='utf-8')
s=s.replace('关闭面板即断开会话。','连接成功后自动收起到左侧 CLI；关闭会话才撤销授权。')
s=s.replace('    s->server.dispatch=', '''    auto projectDocuments=[this,s](bool refresh)->QJsonArray {
        QJsonArray entries;
        for(LatexEditorView *v:editors->editors()) {
            const QString path=HarmonyProject::documentPath(s->root,v->document->getFileName());
            if(path.isEmpty())continue;
            if(refresh)v->editor->refreshExternalChanges();
            entries.append(QJsonObject{{"path",path},{"modified",v->editor->isContentModified()},
                {"conflict",v->editor->isInConflict()},{"exists",QFileInfo(v->document->getFileName()).exists()},{"master",path==s->master}});
        }
        return entries;
    };
    auto blockers=[projectDocuments]()->QJsonArray {
        QJsonArray result;
        for(const QJsonValue &v:projectDocuments(true)) {
            const auto entry=v.toObject();
            if(entry.value("modified").toBool()||entry.value("conflict").toBool())result.append(entry);
        }
        return result;
    };
    connect(s,&QObject::destroyed,this,[this](){if(harmonyCliStatus)harmonyCliStatus->setText(QStringLiteral("未连接"));});
    s->server.dispatch=''')
s=s.replace('[this,s,status,closeButton,exportButton](const QJsonObject &r)', '[this,s,status,closeButton,exportButton,projectDocuments,blockers](const QJsonObject &r)')
s=s.replace('        auto error=[]', '''        QScopedValueRollback<bool> background(harmonyBackgroundOperation,true);
        if(!s->connected) {
            s->connected=true;
            harmonyCliStatus->setText(QStringLiteral("已连接\\n工程：%1").arg(s->root));
            QTimer::singleShot(0,s,[s](){s->hide();});
        }
        auto error=[]''')
s=s.replace('{"writes",false}', '{"preflightScope","authorized_project_buffers"},{"foregroundActivation",false},{"writes",false}')
a=s.index('            const auto views=editors->editors();');b=s.index('        if(cmd=="document.read"',a)
s=s[:a]+'''            projectDocuments(true);
        }
        if(cmd=="documents.list"||cmd=="project.refresh")return {{"ok",true},{"documents",projectDocuments(false)}};
'''+s[b:]
s=s.replace('        for(LatexEditorView *v:editors->editors())if(v->editor->isContentModified()||v->editor->isInConflict())return error("unsaved_edits");', '''        const QJsonArray blocked=blockers();
        if(!blocked.isEmpty())return {{"ok",false},{"error","unsaved_edits"},{"scope","authorized_project_buffers"},{"blockers",blocked}};''')
s=s.replace('[this,s,status,closeButton,exportButton,pdf,path]()', '[this,s,status,closeButton,exportButton,pdf,path,blockers]()')
a=s.index('            bool edits=false;');b=s.index('            else if(job.cancelled)',a)
s=s[:a]+'''            QScopedValueRollback<bool> background(harmonyBackgroundOperation,true);
            job.blockers=blockers();
            if(!job.blockers.isEmpty()){job.state="failed";job.exitCode=-1;job.append("Unsaved edits or external conflict in authorized project before build\\n");}
'''+s[b:]
s=s.replace('job.state="running";status->setText', 'job.state="running";harmonyCliStatus->setText(QStringLiteral("正在构建：")+job.master);status->setText')
s=s.replace('s->running=false;closeButton', 'harmonyCliStatus->setText(QStringLiteral("已连接 · %1\\n%2").arg(job.state,job.master));\n            s->running=false;closeButton')
p.write_text(s,encoding='utf-8')
p=src/'texstudio.h';t=p.read_text(encoding='utf-8').replace('    QPointer<QDialog> harmonyProjectPanel;', '''    QPointer<QDialog> harmonyProjectPanel;
    bool harmonyBackgroundOperation=false;
    QDockWidget *harmonyCliDock=nullptr;
    QLabel *harmonyCliStatus=nullptr;''');p.write_text(t,encoding='utf-8')
p=src/'texstudio.cpp';t=p.read_text(encoding='utf-8')
a=t.index('void Texstudio::harmonyAutomationSession()');b=t.index('void Texstudio::harmonyCleanRebuild()',a);t=t[:a]+s+t[b:]
t='#include <QScopedValueRollback>\n'+t
t=t.replace('    m_firstDockWidget->raise(); // make sure on first run', '''#ifdef Q_OS_OHOS
    if(!harmonyCliDock) {
        auto *panel=new QWidget(this);
        auto *layout=new QVBoxLayout(panel);
        harmonyCliStatus=new QLabel(QStringLiteral("未连接"),panel);
        harmonyCliStatus->setWordWrap(true);
        layout->addWidget(harmonyCliStatus);
        auto *open=new QPushButton(QStringLiteral("打开 CLI 会话…"),panel);
        layout->addWidget(open);layout->addStretch();
        connect(open,&QPushButton::clicked,this,&Texstudio::harmonyAutomationSession);
        harmonyCliDock=addDock("harmonyCli",getRealIconFile("logpanel"),QStringLiteral("CLI 自动化"),panel);
    }
#endif
    m_firstDockWidget->raise(); // make sure on first run''')
t=t.replace('        editors->insertEditor(edit, index);\n        edit->editor->setFocus();', '''        editors->insertEditor(edit, index, !harmonyBackgroundOperation);
        if(harmonyBackgroundOperation)editors->setCurrentEditor(edit,false);
        else edit->editor->setFocus();''')
a=t.index('LatexEditorView *Texstudio::load(');b=t.index('\nvoid Texstudio::',a);load=t[a:b]
load=load.replace('    raise();','    if(!harmonyBackgroundOperation)raise();')
load=load.replace('editors->addEditor(existingView);','editors->insertEditor(existingView,-1,!harmonyBackgroundOperation);\n            if(harmonyBackgroundOperation)editors->setCurrentEditor(existingView,false);')
load=load.replace('existingView->editor->setFocus();','if(!harmonyBackgroundOperation)existingView->editor->setFocus();')
load=load.replace('editors->setCurrentEditor(existingView);','editors->setCurrentEditor(existingView,!harmonyBackgroundOperation);')
load=load.replace('if (windowState() == Qt::WindowMinimized || !isVisible() || !QApplication::activeWindow())', 'if (!harmonyBackgroundOperation && (windowState() == Qt::WindowMinimized || !isVisible() || !QApplication::activeWindow()))')
t=t[:a]+load+t[b:]
# Noninteractive CLI failures are returned through job logs, never modal warnings.
a=t.index('void Texstudio::endRunningSubCommand');b=t.index('\nvoid Texstudio::',a+10);part=t[a:b]
part=part.replace('if (', 'if (!harmonyBackgroundOperation && ',1);t=t[:a]+part+t[b:]
p.write_text(t,encoding='utf-8')
p=r/'texstudio-harmony/release.json';d=json.loads(p.read_text());d.update(version='1.0.28',versionCode=1000028);p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['build-help-cli.sh','stage-help-cli-app.sh','assemble-help-cli-package.py','check-help-cli-package.py']:
    t=(r/'build-support'/name).read_text().replace('help-cli','background-cli').replace('1.0.27','1.0.28').replace('1000027','1000028')
    (r/'build-support'/name.replace('help-cli','background-cli')).write_text(t,encoding='utf-8',newline='\n')
print('Prepared 1.0.28 source')
