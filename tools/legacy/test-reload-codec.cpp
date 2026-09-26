#include "harmonyreload.h"
#include <QCoreApplication>
#include <QDebug>
#include <QTemporaryDir>
#include <cassert>
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);QTemporaryDir tmp;
    QString p=tmp.path()+"/test.tex",text;
    auto write=[&](const QByteArray &bytes){QFile f(p);assert(f.open(QIODevice::WriteOnly));assert(f.write(bytes)==bytes.size());};
    auto *utf8=QTextCodec::codecForName("UTF-8");
    write(QByteArray::fromHex("efbbbf")+QStringLiteral("中文\r\nkeep spaces  \r").toUtf8());
    assert(HarmonyReload::read(p,utf8,text).isEmpty());
    assert(HarmonyReload::normalized(text)==QStringLiteral("中文\nkeep spaces  \n"));
    assert(HarmonyReload::normalized("text ")!=HarmonyReload::normalized("text"));
    write(QByteArray::fromHex("e4b8"));assert(HarmonyReload::read(p,utf8,text)=="invalid_encoding");
    write(QByteArray("a\0b",3));assert(HarmonyReload::read(p,utf8,text)=="invalid_encoding");
    auto *utf16=QTextCodec::codecForName("UTF-16LE");write(utf16->fromUnicode(QStringLiteral("中文")));
    assert(HarmonyReload::read(p,utf16,text).isEmpty()&&text==QStringLiteral("中文"));
    write(QByteArray(4*1024*1024+1,'x'));assert(HarmonyReload::read(p,utf8,text)=="file_too_large");
    QFile::remove(p);assert(HarmonyReload::read(p,utf8,text)=="read_failed");
    assert(HarmonyReload::revision("old")!=HarmonyReload::revision("new"));
    qInfo()<<"PASS: BOM, UTF-8/UTF-16, line endings, significant whitespace, partial encoding, NUL, size bound, missing file, revision change";
}
