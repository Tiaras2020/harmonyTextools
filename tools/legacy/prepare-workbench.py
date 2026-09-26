from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1];s=r/'texstudio-harmony/third_party/texstudio';src=s/'src'
def edit(path,old,new):
    p=Path(path);t=p.read_text(encoding='utf-8');assert old in t,str(path)+': missing anchor';p.write_text(t.replace(old,new,1),encoding='utf-8')
raw=(r/'validation/workbench-1.0.32/jieba-dict.txt').read_text(encoding='utf-8')
words=sorted({line.split()[0] for line in raw.splitlines() if line and all('\u3400'<=c<='\u9fff' for c in line.split()[0])})
d=s/'utilities/dictionaries';(d/'zh_CN.dic').write_text(str(len(words))+'\n'+'\n'.join(words)+'\n',encoding='utf-8');(d/'zh_CN.aff').write_text('SET UTF-8\nLANG zh_CN\n',encoding='utf-8')
(d/'README-zh_CN.md').write_text(f'''# 简体中文词表\n\n来自 https://github.com/fxsjy/jieba 的 jieba/dict.txt，保留纯汉字条目，共 {len(words)} 条。MIT 许可见 LICENSE-jieba.txt。\n原始词表 SHA256：{hashlib.sha256(raw.encode()).hexdigest()}\n\n设置选择 zh_CN 后按词表覆盖连续汉字，不把整个中文句子交给英文 Hunspell。词表只判断词汇成员，不判断搭配、语义或同音错字；生僻词可加入个人忽略列表。在线中文校对是独立功能，不随词典切换自动发送文本。\n''',encoding='utf-8')
edit(s/'texstudio.qrc','<qresource prefix="/">','<qresource prefix="/">\n'+''.join(f'        <file alias="dictionaries/{n}">utilities/dictionaries/{n}</file>\n' for n in ['zh_CN.aff','zh_CN.dic','LICENSE-jieba.txt','README-zh_CN.md']))
edit(src/'configmanager.cpp','"en_US.aff", "en_US.dic", "README_others.txt"','"en_US.aff", "en_US.dic", "README_others.txt", "zh_CN.aff", "zh_CN.dic", "LICENSE-jieba.txt", "README-zh_CN.md"')
edit(src/'spellerutility.cpp','#include "spellerutility.h"','#include "spellerutility.h"\n#include "harmonychinesedict.h"')
edit(src/'spellerutility.cpp','bool SpellerUtility::check(QString word)\n{','bool SpellerUtility::check(QString word)\n{\n    if(mName=="zh_CN") return ignoredWords.contains(word) || harmonyChineseKnown(word);')
edit(src/'spellerutility.cpp','QStringList SpellerUtility::suggest(QString word)\n{','QStringList SpellerUtility::suggest(QString word)\n{\n    if(mName=="zh_CN") return {};')
edit(src/'spellerutility.cpp','QString SpellerManager::prettyName(const QString &name)\n{','QString SpellerManager::prettyName(const QString &name)\n{\n    if(name=="zh_CN") return QStringLiteral("zh_CN - 简体中文（本地词表）");')
edit(src/'configdialog.cpp','#include "configdialog.h"','#include "configdialog.h"\n#include "harmonyclipboard.h"')
edit(src/'configdialog.cpp','    // ai chat\n','''    // Explicit paste requests clipboard permission before reading (OHOS).
    ui.leAIAPIKey->setEchoMode(QLineEdit::Password);
    auto *pasteKey = new QPushButton(QStringLiteral("粘贴密钥"),ui.leAIAPIKey->parentWidget());
    if(auto *grid=qobject_cast<QGridLayout *>(ui.leAIAPIKey->parentWidget()->layout())) grid->addWidget(pasteKey,1,4);
    connect(pasteKey,&QPushButton::clicked,this,[this]{harmonyPaste(this,[this](QString text){ui.leAIAPIKey->setText(text.trimmed());});});
    auto *pasteShortcut=new QShortcut(QKeySequence::Paste,ui.leAIAPIKey);
    pasteShortcut->setContext(Qt::WidgetShortcut);
    connect(pasteShortcut,&QShortcut::activated,pasteKey,&QPushButton::click);
    // ai chat
''')
edit(src/'texstudio.h','    AIChatAssistant *aiChatDlg = nullptr;','    AIChatAssistant *aiChatDlg = nullptr;\n    QDockWidget *harmonyAiDock = nullptr;\n    class HarmonyAiWorkbench *harmonyAiPanel = nullptr;\n    class HarmonyProofPanel *harmonyProofPanel = nullptr;')
edit(src/'texstudio.cpp','#include "harmonyproofread.h"','#include "harmonyproofread.h"\n#include "harmonyproofpanel.h"\n#include "harmonyaiworkbench.h"')
edit(src/'texstudio.cpp','    m_firstDockWidget->raise(); // make sure','''    if(!findChild<QDockWidget *>("harmonyProofread",Qt::FindDirectChildrenOnly)) {
        auto *panel=new QWidget(this);auto *layout=new QVBoxLayout(panel);
        auto *run=new QPushButton(QStringLiteral("开始中文校对"),panel);layout->addWidget(run);
        auto *hint=new QLabel(QStringLiteral("有选区时检查选区，否则检查当前文件全文。点击开始会将过滤后的正文发给配置的 LanguageTool 服务；结果显示在底部“中文校对”。本地中文词典可在设置中独立切换。"),panel);
        hint->setWordWrap(true);layout->addWidget(hint);layout->addStretch();
        connect(run,&QPushButton::clicked,this,&Texstudio::harmonyChineseProofread);
        addDock("harmonyProofread",getRealIconFile("spellcheck"),QStringLiteral("中文校对"),panel);
    }
    if(!harmonyAiPanel) {
        harmonyAiPanel=new HarmonyAiWorkbench(&configManager,this);
        harmonyAiPanel->tools.buffer=[this](const QString &path) -> QJsonObject {
            for(auto *v:editors->editors()) if(v && v->editor && QFileInfo(v->editor->fileName()).absoluteFilePath()==path)
                return {{"open",true},{"text",v->editor->text()},{"modified",v->editor->isContentModified()}};
            return {{"open",false}};
        };
        harmonyAiPanel->tools.editBuffer=[this](const QString &path,const QString &revision,const QString &text) -> QJsonObject {
            for(auto *v:editors->editors()) if(v && v->editor && QFileInfo(v->editor->fileName()).absoluteFilePath()==path) {
                auto *ed=v->editor;
                if(HarmonyAiTools::revision(ed->text())!=revision)return HarmonyAiTools::error("revision_mismatch_read_again");
                QDocumentCursor cursor(ed->document());cursor.movePosition(1,QDocumentCursor::Start);cursor.movePosition(1,QDocumentCursor::End,QDocumentCursor::KeepAnchor);cursor.replaceSelectedText(text);
                return {{"revision",HarmonyAiTools::revision(ed->text())},{"saved",false},{"undoAvailable",true}};
            }
            return HarmonyAiTools::error("editor_closed_read_again");
        };
        harmonyAiPanel->context=[this]() -> QString {
            auto *ed=currentEditor();if(!ed)return {};
            QString rel=QDir(harmonyAiPanel->tools.root).relativeFilePath(ed->fileName());
            if(harmonyAiPanel->tools.resolve(rel).isEmpty())return QStringLiteral("Current file is outside this conversation project.");
            return QStringLiteral("File: ")+rel+QStringLiteral("\\nSelection:\\n")+ed->cursor().selectedText().left(4000)+QStringLiteral("\\nText:\\n")+ed->text().left(12000);
        };
        harmonyAiDock=addDock("harmonyAi",getRealIconFile("help"),QStringLiteral("AI 助手"),harmonyAiPanel);
    }
    m_firstDockWidget->raise(); // make sure''')
start=(src/'texstudio.cpp').read_text(encoding='utf-8')
a=start.index('void Texstudio::harmonyChineseProofread()');b=start.index('\nvoid Texstudio::quickTabbing()',a)
start=start[:a]+'''void Texstudio::harmonyChineseProofread()
{
    auto *ed=currentEditor();if(!ed || !outputView)return;
    if(!harmonyProofPanel) {
        harmonyProofPanel=new HarmonyProofPanel(configManager.configBaseDir+"/harmony-proofread.ini",outputView);
        harmonyProofPanel->jump=[this](QString path,int line){
            for(auto *v:editors->editors()) if(v && v->editor && v->editor->fileName()==path){editors->setCurrentEditor(v);v->editor->setCursorPosition(line,0);return;}
        };
        outputView->appendPage(new TitledPanelPage(harmonyProofPanel,"harmonyProofreadResults",QStringLiteral("中文校对")));
    }
    auto cursor=ed->cursor();bool selected=cursor.hasSelection();
    outputView->showPage("harmonyProofreadResults");
    harmonyProofPanel->start(selected?cursor.selectedText():ed->text(),ed->fileName(),selected?cursor.startLineNumber():0);
}

void Texstudio::aiChat(const QString queryText)
{
    if(!harmonyAiPanel)return;
    if(harmonyAiPanel->tools.root.isEmpty() && currentEditor() && !currentEditor()->fileName().isEmpty())
        harmonyAiPanel->setRoot(QFileInfo(currentEditor()->fileName()).absolutePath());
    harmonyAiDock->show();harmonyAiDock->raise();
    if(!queryText.isEmpty()) harmonyAiPanel->setPrompt(queryText);
}
''' + start[b:]
(src/'texstudio.cpp').write_text(start,encoding='utf-8')
edit(src/'texstudio.cpp','中文校对（选中文字）…','中文校对（选区或全文）')
p=r/'texstudio-harmony/release.json';data=json.loads(p.read_text());data.update(version='1.0.32',versionCode=1000032);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'build-support/sync-baseline.py';text=p.read_text();mark='stamp = datetime.datetime.now';i=text.index(mark);text=text[:i]+"paths += ['third_party/texstudio/src/' + name for name in ('harmonyclipboard.h','harmonychinesedict.h','harmonyaitools.h','harmonyaiworkbench.h','harmonyproofpanel.h','spellerutility.cpp','configmanager.cpp','texstudio.h')]\npaths += ['third_party/texstudio/utilities/dictionaries/' + name for name in ('zh_CN.aff','zh_CN.dic','LICENSE-jieba.txt','README-zh_CN.md')]\n"+text[i:];p.write_text(text)
print('Workbench sources and Chinese dictionary prepared',len(words))
