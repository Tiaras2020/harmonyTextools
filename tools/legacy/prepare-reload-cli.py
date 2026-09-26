from pathlib import Path
import json
r=Path.cwd(); src=r/'texstudio-harmony/third_party/texstudio/src'
p=src/'qcodeedit/lib/qeditor.h';s=p.read_text(encoding='utf-8').replace('        void refreshExternalChanges();','        void refreshExternalChanges();\n        bool reconcileExternalChanges();\n        QString reloadExternal(bool discardLocal, const QString &expectedRevision);');p.write_text(s,encoding='utf-8')
p=src/'qcodeedit/lib/qeditor.cpp';s=p.read_text(encoding='utf-8');s='#include "harmonyreload.h"\n'+s
s=s.replace('    if (!QFileInfo::exists(file) || isContentModified() || isInConflict()) {','    if (reconcileExternalChanges()) return;\n    if (!QFileInfo::exists(file) || isContentModified() || isInConflict()) {',1)
s=s.replace('void QEditor::refreshExternalChanges() { watcher()->refreshNow(fileName()); }', '''void QEditor::refreshExternalChanges() {
    watcher()->refreshNow(fileName());
    if(isInConflict())reconcileExternalChanges();
}
bool QEditor::reconcileExternalChanges() {
    if(!isInConflict()&&!isContentModified())return false;
    QString disk;
    if(!HarmonyReload::read(fileName(),m_doc->codec(),disk).isEmpty())return false;
    if(HarmonyReload::normalized(disk)!=HarmonyReload::normalized(m_doc->text()))return false;
    m_saveState=Undefined;
    m_doc->setClean(); // Preserve text, cursor and undo history; disk already agrees.
    emit fileReloaded();
    return true;
}
QString QEditor::reloadExternal(bool discardLocal,const QString &expectedRevision) {
    const QString before=HarmonyReload::revision(m_doc->text());
    if(discardLocal && expectedRevision.isEmpty())return "expected_revision_required";
    if(!expectedRevision.isEmpty() && expectedRevision!=before)return "revision_mismatch";
    QString disk;
    const QString error=HarmonyReload::read(fileName(),m_doc->codec(),disk);
    if(!error.isEmpty())return error; // Never clear a buffer on failed reads.
    const bool same=HarmonyReload::normalized(disk)==HarmonyReload::normalized(m_doc->text());
    if(!same && isContentModified() && !discardLocal)return "unsaved_edits";
    if(same) {
        m_saveState=Undefined;m_doc->setClean();emit fileReloaded();return {};
    }
    const int line=cursor().lineNumber(),column=cursor().columnNumber();
    emit fileAutoReloading(fileName());
    // Apply exactly the validated snapshot, without a second disk read.
    setText(disk,false);
    m_saveState=Undefined;m_doc->setClean();
    setCursor(QDocumentCursor(m_doc,qBound(0,line,m_doc->lineCount()-1),qMax(0,column)));
    emit fileReloaded();
    return {};
}''');p.write_text(s,encoding='utf-8')
p=r/'build-support/project-session-function.txt';s=p.read_text(encoding='utf-8');s=s.replace('"document.read","document.open"','"document.read","document.reload","document.open"',1)
pos=s.index('        // Refresh before exposing buffers')
s=s[:pos]+'''        if(cmd=="document.reload") {
            if(busy())return error("busy");
            const QString path=HarmonyProject::resolve(s->root,r.value("path").toString());
            if(path.isEmpty()||!HarmonyProject::textFile(path))return error("invalid_text_path");
            auto *v=getEditorViewFromFileName(path);
            if(!v)return error("document_not_open");
            if((r.contains("discardLocal")&&!r.value("discardLocal").isBool()) ||
               (r.contains("expectedRevision")&&!r.value("expectedRevision").isString()))return error("invalid_parameters");
            const bool dirty=v->editor->isContentModified();
            const QString previous=HarmonyProject::digest(v->document->text().toUtf8());
            const QString failure=v->editor->reloadExternal(r.value("discardLocal").toBool(),r.value("expectedRevision").toString());
            QJsonObject result{{"ok",failure.isEmpty()},{"path",rel(path)},
                {"modified",v->editor->isContentModified()},{"conflict",v->editor->isInConflict()},
                {"revision",HarmonyProject::digest(v->document->text().toUtf8())}};
            if(!failure.isEmpty()) {
                result.insert("error",failure);
                result.insert("recoveryHint",QStringLiteral("先用 document.read 查看当前缓冲区并保留需要的编辑；明确以磁盘为准时，使用 document.reload --discard-local --expected-revision REV。文件缺失或无法读取时先恢复磁盘文件。"));
            } else result.insert("discardedLocalChanges",dirty&&previous!=result.value("revision").toString());
            return result;
        }
'''+s[pos:]
s=s.replace('{"scope","authorized_project_buffers"},{"blockers",blocked}', '{"scope","authorized_project_buffers"},{"blockers",blocked},{"recoveryHint",QStringLiteral("先读取 blockers 中的文件并保留所需编辑。可在应用内保存/重载；明确以磁盘为准时调用 document.reload --discard-local --expected-revision REV，REV 来自 document.read。缺失文件须先恢复。不要自动丢弃编辑。")}')
p.write_text(s,encoding='utf-8')
p=src/'texstudio.cpp';t=p.read_text(encoding='utf-8');a=t.index('void Texstudio::harmonyAutomationSession()');b=t.index('void Texstudio::harmonyCleanRebuild()',a);p.write_text(t[:a]+s+t[b:],encoding='utf-8')
p=r/'tools/texstudioctl.py';s=p.read_text(encoding='utf-8').replace("    parser.add_argument('--job',", "    parser.add_argument('--discard-local', action='store_true', help='明确丢弃未保存缓冲区；需 --expected-revision')\n    parser.add_argument('--expected-revision', help='document.read 返回的缓冲区 revision')\n    parser.add_argument('--job',")
s=s.replace('    try:\n        session =', '''    if (args.discard_local or args.expected_revision is not None) and args.command != 'document.reload':parser.error('重载参数仅用于 document.reload')
    if args.discard_local and not args.expected_revision:parser.error('--discard-local 必须同时提供 --expected-revision')
    try:
        session =''')
s=s.replace('        result = request(session, args.command,', "        if args.command=='document.reload':\n            parameters['discardLocal']=args.discard_local\n            if args.expected_revision is not None:parameters['expectedRevision']=args.expected_revision\n        result = request(session, args.command,")
p.write_text(s,encoding='utf-8')
p=r/'tools/texstudio-cli-help.json';d=json.loads(p.read_text(encoding='utf-8'));d['appliesTo']='TeXstudio Harmony 1.0.29'
d['notes']+=['磁盘与缓冲区按当前编码解码、统一换行后内容一致时，刷新可自动解除冲突并标记已保存，保留撤销历史。','document.reload 默认保护未保存修改。明确采用磁盘内容时，先 document.read，再传 --discard-local --expected-revision REV；版本变化会拒绝。成功替换内容会清空旧撤销历史。不要自动丢弃用户编辑。']
d['commands']['document.reload']={'summary':'从磁盘重载已打开文本；默认不丢弃未保存编辑','parameters':{'--path':'必填，授权工程内已打开文本文件','--discard-local':'明确丢弃本地编辑，必须配合版本校验','--expected-revision':'document.read 返回的 revision；不匹配则拒绝'},'request':{'command':'document.reload','path':'main.tex'},'example':'python3 texstudioctl.py --session texstudio-session.json document.reload --path main.tex','limits':'4 MiB；按编辑器当前编码读取；忙碌、缺失、无效编码和旧版本均拒绝。强制示例：document.reload --path main.tex --discard-local --expected-revision REV'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'build-support/sync-baseline.py';s=p.read_text().replace('report = []',"paths += ['third_party/texstudio/src/harmonyreload.h']\nreport = []");p.write_text(s)
p=r/'texstudio-harmony/release.json';d=json.loads(p.read_text());d.update(version='1.0.29',versionCode=1000029);p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['build-background-cli.sh','stage-background-cli-app.sh','assemble-background-cli-package.py','check-background-cli-package.py','test-background-help.py']:
    t=(r/'build-support'/name).read_text(encoding='utf-8').replace('background-cli','reload-cli').replace('1.0.28','1.0.29').replace('1000028','1000029').replace('==19','==20').replace('19 help','20 help')
    (r/'build-support'/name.replace('background','reload')).write_text(t,encoding='utf-8',newline='\n')
