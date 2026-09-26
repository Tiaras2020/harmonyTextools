#include "harmonyproofread.h"
#include <cassert>
#include <iostream>
int main() {
    const QByteArray chinese = QStringLiteral("data: {\"choices\":[{\"delta\":{\"content\":\"中文 data: 正文\"}}]}\r\n\r\ndata: [DONE]\n\n").toUtf8();
    for (int split=0; split <= chinese.size(); ++split) {
        HarmonySseBuffer parser;
        auto events=parser.feed(chinese.left(split)); events.append(parser.feed(chinese.mid(split)));
        assert(events.size()==2 && events[1]=="[DONE]" && !parser.incomplete());
        auto data=QJsonDocument::fromJson(events[0]);
        assert(data.object()["choices"].toArray()[0].toObject()["delta"].toObject()["content"].toString()==QStringLiteral("中文 data: 正文"));
    }
    HarmonySseBuffer parser; QList<QByteArray> events;
    for (auto c:chinese) events.append(parser.feed(QByteArray(1,c)));
    assert(events.size()==2);
    assert(parser.feed(": keepalive\n\ndata: unfinished").isEmpty() && parser.incomplete());
    parser.clear(); assert(!parser.incomplete());
    auto multiline=parser.feed("data: {\n" "data: \"ok\":true}\n\n");
    assert(multiline.size()==1 && QJsonDocument::fromJson(multiline[0]).object()["ok"].toBool());
    assert(harmonyValidServiceUrl(QUrl("https://api.deepseek.com/chat/completions")));
    assert(harmonyValidServiceUrl(QUrl("http://127.0.0.1:18831/chat/completions")));
    assert(!harmonyValidServiceUrl(QUrl("file:///etc/passwd")));
    assert(!harmonyValidServiceUrl(QUrl("https://user:secret@example.com")));
    const QString raw=QStringLiteral("中文\\textbf{正文} $x+y$ \\(a+b\\) %注释\n\\cite{key}\\input{secret}\\begin{equation}x=y\\end{equation}你好");
    auto clean=harmonyProofreadText(raw);
    assert(clean.size()==raw.size() && clean.count('\n')==1);
    assert(clean.contains(QStringLiteral("正文")) && clean.endsWith(QStringLiteral("你好")));
    for(auto word: {"x+y","a+b","key","secret","equation","x=y"}) assert(!clean.contains(word));
    assert(!clean.contains(QStringLiteral("注释")));
    std::cout << "PASS: all SSE split positions, bytewise UTF-8, CRLF, multiline, truncation/reset, URL policy and LaTeX masking\n";
}
