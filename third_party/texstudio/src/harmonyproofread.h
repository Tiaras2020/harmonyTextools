#ifndef HARMONY_PROOFREAD_H
#define HARMONY_PROOFREAD_H
#include "harmonynetwork.h"
#include "harmonydialoglayout.h"
#include <QtWidgets>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QUrlQuery>
#include <QRegularExpression>

// Preserve UTF-16 positions/newlines while masking common LaTeX syntax.
// This is a conservative preview, not a full TeX expansion engine.
inline QString harmonyProofreadText(QString text)
{
    auto mask = [&text](const QString &pattern) {
        auto matches = QRegularExpression(pattern, QRegularExpression::DotMatchesEverythingOption).globalMatch(text);
        while (matches.hasNext()) {
            auto m = matches.next();
            for (int i = m.capturedStart(); i < m.capturedEnd(); ++i)
                if (text[i] != '\n' && text[i] != '\r') text[i] = ' ';
        }
    };
    mask(QStringLiteral(R"((?<!\\)%[^\n]*)"));
    mask(QStringLiteral(R"(\\begin\{(equation\*?|align\*?|gather\*?|verbatim|lstlisting|minted)\}.*?\\end\{\1\})"));
    mask(QStringLiteral(R"(\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$[^$]*?(?<!\\)\$)"));
    mask(QStringLiteral(R"(\\(?:input|include|includegraphics|label|ref|eqref|cite\w*|bibliography|bibliographystyle|documentclass|usepackage|begin|end)\*?(?:\[[^\]]*\])?\{[^{}]*\})"));
    mask(QStringLiteral(R"(\\[A-Za-z@]+\*?(?:\[[^\]]*\])?|\\[^A-Za-z])"));
    text.replace('{', ' '); text.replace('}', ' ');
    return text;
}

inline void harmonyShowProofread(QWidget *parent, const QString &selection, const QString &configuredUrl, const QString &settingsPath)
{
    auto *dlg = new QDialog(parent);
    dlg->setAttribute(Qt::WA_DeleteOnClose);
    dlg->setWindowTitle(QStringLiteral("中文校对（LanguageTool）"));
    auto *layout = new QVBoxLayout(dlg);
    auto *description = new QLabel(QStringLiteral("检查选中的文字，不修改源文件。已过滤常见命令、公式和注释；复杂宏请在发送前检查预览。\n点击“开始校对”会将预览文字发送到下方服务。中文规则检查不能代替完整的错别字词典。"), dlg);
    description->setWordWrap(true); layout->addWidget(description);
    auto *settings = new QSettings(settingsPath, QSettings::IniFormat, dlg);
    QString initialUrl = configuredUrl;
    if (initialUrl.isEmpty() || initialUrl == "http://localhost:8081/") initialUrl = QStringLiteral("https://api.languagetool.org/v2/check");
    auto *url = new QLineEdit(settings->value("serviceUrl", initialUrl).toString(), dlg);
    url->setPlaceholderText(QStringLiteral("LanguageTool 服务地址，可使用自建服务")); layout->addWidget(url);
    auto *preview = new QPlainTextEdit(harmonyProofreadText(selection), dlg);
    preview->setReadOnly(true); layout->addWidget(preview, 1);
    auto *results = new QPlainTextEdit(dlg); results->setReadOnly(true); layout->addWidget(results, 1);
    auto *buttons = new QDialogButtonBox(QDialogButtonBox::Close, dlg);
    buttons->button(QDialogButtonBox::Close)->setText(QStringLiteral("关闭"));
    auto *run = buttons->addButton(QStringLiteral("开始校对"), QDialogButtonBox::ActionRole);
    auto *stop = buttons->addButton(QStringLiteral("取消请求"), QDialogButtonBox::ActionRole); stop->setEnabled(false);
    layout->addWidget(buttons); QObject::connect(buttons, &QDialogButtonBox::rejected, dlg, &QDialog::close);
    auto *manager = new QNetworkAccessManager(dlg);
    QObject::connect(run, &QPushButton::clicked, dlg, [=] {
        QUrl endpoint(url->text().trimmed());
        if (!endpoint.path().endsWith("/v2/check")) endpoint.setPath(endpoint.path().replace(QRegularExpression("/$"), "") + "/v2/check");
        if (!harmonyValidServiceUrl(endpoint)) { results->setPlainText(QStringLiteral("请输入有效的 HTTP/HTTPS 服务地址。")); return; }
        settings->setValue("serviceUrl", endpoint.toString());
        if (preview->toPlainText().size() > 20000) { results->setPlainText(QStringLiteral("一次最多校对 20000 个字符，请缩小选区。")); return; }
        harmonyInitializeTls();
        QUrlQuery form; form.addQueryItem("language", "zh-CN"); form.addQueryItem("text", preview->toPlainText());
        QNetworkRequest request(endpoint); request.setHeader(QNetworkRequest::ContentTypeHeader, "application/x-www-form-urlencoded");
        auto *reply = manager->post(request, form.query(QUrl::FullyEncoded).replace("+", "%2B").toUtf8());
        run->setEnabled(false); stop->setEnabled(true); results->setPlainText(QStringLiteral("正在校对…"));
        auto *timeout = new QTimer(reply); timeout->setSingleShot(true);
        QObject::connect(timeout, &QTimer::timeout, reply, [reply] { reply->setProperty("timedOut", true); reply->abort(); }); timeout->start(30000);
        QObject::connect(stop, &QPushButton::clicked, reply, &QNetworkReply::abort);
        QObject::connect(reply, &QNetworkReply::finished, dlg, [=] {
            timeout->stop(); run->setEnabled(true); stop->setEnabled(false);
            if (reply->error() != QNetworkReply::NoError) {
                results->setPlainText(reply->property("timedOut").toBool() ? QStringLiteral("服务超时，请检查地址或稍后重试。") : QStringLiteral("校对未完成：") + reply->errorString());
            } else {
                QJsonParseError error; auto doc = QJsonDocument::fromJson(reply->readAll(), &error);
                if (error.error != QJsonParseError::NoError || !doc.object().value("matches").isArray()) results->setPlainText(QStringLiteral("服务返回的不是有效的 LanguageTool 检查结果。"));
                else {
                    QStringList lines;
                    for (auto value : doc.object()["matches"].toArray()) {
                        auto item = value.toObject(); int offset = item["offset"].toInt(-1), length = item["length"].toInt();
                        if (offset < 0 || offset + length > selection.size()) continue;
                        QStringList replacements;
                        for (auto replacement : item["replacements"].toArray()) replacements << replacement.toObject()["value"].toString();
                        lines << QStringLiteral("选区第 %1 行：%2\n原文：%3\n建议：%4\n").arg(selection.left(offset).count('\n') + 1).arg(item["message"].toString(), selection.mid(offset, length), replacements.mid(0, 5).join(QStringLiteral(" / ")));
                    }
                    results->setPlainText(lines.isEmpty() ? QStringLiteral("本次规则检查未发现问题；不代表文字完全无误。") : lines.join('\n'));
                }
            }
            reply->deleteLater();
        });
    });
    fitHarmonyDialog(dlg, 55, 28); dlg->show();
}
#endif
