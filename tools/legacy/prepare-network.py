"""Apply reviewed 1.0.31 integration edits; fails when source anchors drift."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]; src=r/'texstudio-harmony/third_party/texstudio/src'
def edit(p, old, new):
    t=p.read_text(encoding='utf-8'); assert old in t, (p,old[:60]); p.write_text(t.replace(old,new),encoding='utf-8')
edit(src/'aichatassistant.h','#include "chatdelegate.h"','#include "chatdelegate.h"\n#include "harmonynetwork.h"')
edit(src/'aichatassistant.h','    QString m_response;','    HarmonySseBuffer m_sse;\n    bool m_streamDone = false;\n    QString m_response;')
edit(src/'aichatassistant.cpp','    config=dynamic_cast<ConfigManager *>(ConfigManagerInterface::getInstance());','    harmonyInitializeTls();\n    config=dynamic_cast<ConfigManager *>(ConfigManagerInterface::getInstance());')
edit(src/'aichatassistant.cpp','new QNetworkAccessManager();','new QNetworkAccessManager(this);')
edit(src/'aichatassistant.cpp','        ja_messages.removeLast();','        // Keep the submitted question and any partial response after cancellation.')
edit(src/'aichatassistant.cpp','    m_response.clear();','    m_response.clear();\n    m_sse.clear();\n    m_streamDone = false;')
edit(src/'aichatassistant.cpp','        case 5: url="https://openrouter.ai/api/v1/chat/completions";','        case 6: url="https://api.deepseek.com/chat/completions";\n            break;\n        case 5: url="https://openrouter.ai/api/v1/chat/completions";')
edit(src/'aichatassistant.cpp','    QJsonObject dd;','    if (!harmonyValidServiceUrl(QUrl(url))) {\n        QMessageBox::warning(this, tr("AI Chat"), QStringLiteral("请输入有效的 HTTP/HTTPS 接口地址。")); return;\n    }\n    QJsonObject dd;')
edit(src/'aichatassistant.cpp','    dd["model"]=config->ai_preferredModel;','    dd["model"]=config->ai_preferredModel;\n    if (config->ai_provider == 6) {\n        if (config->ai_preferredModel.isEmpty()) dd["model"] = "deepseek-flash";\n        dd["thinking"] = QJsonObject{{"type", "disabled"}};\n    }')
edit(src/'aichatassistant.cpp','connect(networkManager, &QNetworkAccessManager::finished, this, &AIChatAssistant::onRequestCompleted);','connect(networkManager, &QNetworkAccessManager::finished, this, &AIChatAssistant::onRequestCompleted, Qt::UniqueConnection);\n    QTimer::singleShot(180000, m_reply, [reply = m_reply] {\n        if (reply->isRunning()) { reply->setProperty("timedOut", true); reply->abort(); }\n    });')
edit(src/'aichatassistant.cpp','''     QByteArray data=m_reply->readAll();
     QString allData(data);
     if(allData.startsWith("data: ")){
         updateStreamedConversation(allData);
     }''','''     if (!m_reply->header(QNetworkRequest::ContentTypeHeader).toString().contains("text/event-stream")) return;
     for (const auto &event : m_sse.feed(m_reply->readAll())) {
         if (event.trimmed() == "[DONE]") { m_streamDone = true; continue; }
         updateStreamedConversation(QStringLiteral("data: ") + QString::fromUtf8(event));
     }''')
edit(src/'aichatassistant.cpp','addMessage(QString("Error: "+m_reply->errorString()),Sender::Error);','addMessage(m_reply->property("timedOut").toBool() ? QStringLiteral("请求超时，请重试。") : (code == QNetworkReply::OperationCanceledError ? QStringLiteral("请求已取消。") : QString("Error: "+m_reply->errorString())),Sender::Error);')
edit(src/'aichatassistant.cpp','    if (!nreply || nreply->error() != QNetworkReply::NoError) return;','''    if (!nreply || nreply != m_reply || nreply->error() != QNetworkReply::NoError) return;
    const bool streaming = nreply->header(QNetworkRequest::ContentTypeHeader).toString().contains("text/event-stream");
    if (streaming) slotUpdateResults();''')
edit(src/'aichatassistant.cpp','    if(allData.isEmpty()) return; // work-around, seems to happen with mistral during multiple tool calls','''    if (streaming) {
        if (m_response.isEmpty()) addMessage(QStringLiteral("服务未返回正文。请检查模型和服务设置。"), Sender::Error);
        else if (m_sse.incomplete() || !m_streamDone) addMessage(QStringLiteral("响应流未完整结束，请核对结果或重试。"), Sender::Error);
        nreply->deleteLater(); m_reply = nullptr;
        m_actSend->setToolTip(tr("Send Query to AI provider")); m_actSend->setIcon(getRealIcon("document-send"));
        if (config->ai_recordConversation) writeToFile(m_conversationFileName, makeJsonDoc());
        return;
    }''')
edit(src/'aichatassistant.cpp','''        QJsonObject obj=doc.object();
        QJsonArray arr=obj["choices"].toArray();''','''        QJsonObject obj=doc.object();
        if (!obj.contains("choices") && obj["type"].toString() != "message")
            addMessage(QStringLiteral("服务返回的内容不是有效的聊天结果。"), Sender::Error);
        QJsonArray arr=obj["choices"].toArray();''')
# The stream updater must replace the previous assistant message, not duplicate it.
edit(src/'aichatassistant.cpp','''    }else{
        // Keep the submitted question and any partial response after cancellation.
    }
    ja_message["role"]="assistant";''','''    }else{
        ja_messages.removeLast();
    }
    ja_message["role"]="assistant";''')
edit(src/'configdialog.cpp','\tui.setupUi(this);','\tui.setupUi(this);\n    ui.cbAIProvider->addItem(QStringLiteral("DeepSeek V4.1-Flash"));')
edit(src/'configdialog.cpp','#include "configdialog.h"','#include "configdialog.h"\n#include "harmonynetwork.h"')
edit(src/'configdialog.cpp','void ConfigDialog::retrieveModels()\n{','void ConfigDialog::retrieveModels()\n{\n    harmonyInitializeTls();')
edit(src/'configdialog.cpp','    case 5:\n        url="https://openrouter.ai/v1/models";','    case 6:\n        url="https://api.deepseek.com/models";\n        break;\n    case 5:\n        url="https://openrouter.ai/v1/models";')
edit(src/'configdialog.cpp','''    default:
        ui.cbAIPreferredModel->clear();''','''    case 6:
        ui.cbAIPreferredModel->clear();
        ui.cbAIPreferredModel->addItem("deepseek-flash");
        modelLineEdit->setPlaceholderText("deepseek-flash");
        break;
    default:
        ui.cbAIPreferredModel->clear();''')
edit(src/'texstudio.h','    void harmonyCleanRebuild();','    void harmonyCleanRebuild();\n    void harmonyChineseProofread();')
edit(src/'texstudio.cpp','#include "texstudio.h"','#include "texstudio.h"\n#include "harmonyproofread.h"\n#ifdef Q_OS_OHOS\n#include <QtOhosExtras/qohosuiabilitycontext.h>\n#endif')
edit(src/'texstudio.cpp','    newManagedAction(menu, "aichat", tr("AI &Chat..."), SLOT(aiChat()));','    newManagedAction(menu, "aichat", tr("AI &Chat..."), SLOT(aiChat()));\n    newManagedAction(menu, "chineseproofread", QStringLiteral("中文校对（选中文字）…"), SLOT(harmonyChineseProofread()));')
edit(src/'texstudio.cpp','void Texstudio::aiChat(const QString queryText)','''void Texstudio::harmonyChineseProofread()
{
    if (!currentEditorView()) return;
    QString text = currentEditorView()->editor->cursor().selectedText();
    if (text.trimmed().isEmpty()) { QMessageBox::information(this, QStringLiteral("中文校对"), QStringLiteral("请先选中要校对的文字。")); return; }
    harmonyShowProofread(this, text, configManager.grammarCheckerConfig->languageToolURL);
}

void Texstudio::aiChat(const QString queryText)''')
edit(src/'texstudio.cpp','void Texstudio::openExternalTerminal(void)\n{','''void Texstudio::openExternalTerminal(void)
{
#ifdef Q_OS_OHOS
    QString dir = getCurrentFileName().isEmpty() ? getUserDocumentFolder() : QFileInfo(getCurrentFileName()).absolutePath();
    QString quoted = dir; quoted.replace("'", "'\\\"'\\\"'");
    QMessageBox box(QMessageBox::Information, QStringLiteral("外部终端"),
        QStringLiteral("打开 HiShell。可复制进入当前工程目录的命令，在终端粘贴执行。\\n目录：") + dir, QMessageBox::Cancel, this);
    auto *open = box.addButton(QStringLiteral("打开 HiShell"), QMessageBox::ActionRole);
    auto *copy = box.addButton(QStringLiteral("复制 cd 命令并打开"), QMessageBox::ActionRole);
    box.exec();
    if (box.clickedButton() != open && box.clickedButton() != copy) return;
    if (box.clickedButton() == copy) QApplication::clipboard()->setText("cd -- '" + quoted + "'");
    QtOhosExtras::QOhosWant want; want.bundleName = "com.huawei.hmos.hishell"; want.abilityName = "EntryAbility";
    const auto status = QtOhosExtras::startAbility(want);
    if (!status || !status->success()) QMessageBox::warning(this, QStringLiteral("外部终端"), QStringLiteral("无法打开 HiShell，请确认终端已安装且当前允许打开。"));
    return;
#endif''')
cm=r/'texstudio-harmony/third_party/texstudio/CMakeLists.txt'
edit(cm,'# Build texstudio application','# Build texstudio application\nif(OHOS)\n    find_package(Qt5OhosExtras REQUIRED)\n    list(APPEND ADDITIONAL_LIBRARIES Qt5::OhosExtras)\nendif()')
# Link explicitly: upstream does not consume ADDITIONAL_LIBRARIES consistently.
edit(cm,'target_link_libraries(texstudio PRIVATE','if(OHOS)\n    target_link_libraries(texstudio PRIVATE Qt5::OhosExtras)\nendif()\ntarget_link_libraries(texstudio PRIVATE')
edit(r/'texstudio-harmony/third_party/texstudio/texstudio.qrc','    <qresource prefix="/">','    <qresource prefix="/">\n        <file alias="certificates/cacert.pem">utilities/certificates/cacert.pem</file>')
p=r/'texstudio-harmony/release.json'; data=json.loads(p.read_text()); data['version']='1.0.31'; data['versionCode']=1000031; p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
edit(r/'build-support/sync-baseline.py','report = []','''paths += ['third_party/texstudio/src/' + name for name in ('harmonynetwork.h', 'harmonyproofread.h', 'aichatassistant.h')]
paths += ['third_party/texstudio/CMakeLists.txt', 'third_party/texstudio/utilities/certificates/cacert.pem']
report = []''')
print('Prepared network, proofreading, terminal and release integration')
