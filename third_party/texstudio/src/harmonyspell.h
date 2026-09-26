#ifndef HARMONY_SPELL_H
#define HARMONY_SPELL_H
#include <QStringList>
#include <QChar>

// Han is not an English spelling error. Retain alphabetic runs for Hunspell,
// including English embedded in Chinese without spaces. This is not Chinese proofreading.
inline QStringList harmonySpellParts(const QString &word) {
    bool han = false;
    for (uint c : word.toUcs4()) if (QChar::script(c) == QChar::Script_Han) { han = true; break; }
    if (!han) return {word};
    QStringList result;
    QString run;
    for (uint c : word.toUcs4()) {
        if (QChar::script(c) != QChar::Script_Han && (QChar::isLetter(c) || QChar::isMark(c) || c == '\'')) run += QString::fromUcs4(&c,1);
        else if (!run.isEmpty()) { result << run; run.clear(); }
    }
    if (!run.isEmpty()) result << run;
    return result;
}
#endif
