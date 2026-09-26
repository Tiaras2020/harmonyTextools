#ifndef HARMONY_CHINESE_DICT_H
#define HARMONY_CHINESE_DICT_H
#include <QtCore>
// Chinese has no word separators. Accept a run only if dictionary words cover it.
// This tests vocabulary membership, not whether a sentence makes semantic sense.
inline bool harmonyChineseKnown(const QString &text)
{
    static const QSet<QString> words = [] {
        QSet<QString> result; QFile f(":/dictionaries/zh_CN.dic");
        if (f.open(QIODevice::ReadOnly)) {
            f.readLine();
            while (!f.atEnd()) result.insert(QString::fromUtf8(f.readLine()).trimmed());
        }
        return result;
    }();
    if (words.isEmpty()) return true;
    auto matches = QRegularExpression(QStringLiteral("[\\x{3400}-\\x{9fff}]+")).globalMatch(text);
    while (matches.hasNext()) {
        const QString run = matches.next().captured();
        QVector<bool> reachable(run.size()+1, false); reachable[0] = true;
        for (int i=0; i<run.size(); ++i) if (reachable[i])
            for (int n=1; n<=32 && i+n<=run.size(); ++n)
                if (words.contains(run.mid(i,n))) reachable[i+n] = true;
        if (!reachable.last()) return false;
    }
    return true;
}
#endif
