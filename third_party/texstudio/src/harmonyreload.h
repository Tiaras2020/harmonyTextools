#pragma once
#include <QFile>
#include <QTextCodec>
#include <QCryptographicHash>
namespace HarmonyReload {
inline QString revision(const QString &text) {
    return QString::fromLatin1(QCryptographicHash::hash(text.toUtf8(),QCryptographicHash::Sha256).toHex());
}
inline QString normalized(QString text) {
    return text.replace("\r\n","\n").replace('\r','\n');
}
inline QString read(const QString &path,QTextCodec *codec,QString &text) {
    QFile file(path);
    if(!file.open(QIODevice::ReadOnly))return "read_failed";
    const QByteArray data=file.read(4*1024*1024+1);
    if(data.size()>4*1024*1024 || !file.atEnd())return "file_too_large";
    if(file.error()!=QFile::NoError)return "read_failed";
    if(!codec)return "unknown_encoding";
    QTextCodec::ConverterState state;
    text=codec->toUnicode(data.constData(),data.size(),&state);
    if(state.invalidChars || state.remainingChars || text.contains(QChar(0)))return "invalid_encoding";
    return {};
}
}
