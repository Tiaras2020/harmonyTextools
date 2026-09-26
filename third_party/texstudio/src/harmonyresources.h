#ifndef HARMONY_RESOURCES_H
#define HARMONY_RESOURCES_H
#include <QString>
#include <QProcessEnvironment>
class QWidget;
namespace HarmonyResources {
struct Result { QString id; QString error; };
QString storageRoot();
QString sessionResource();
QString selectedResource(const QString &root);
QStringList installed(const QString &root);
Result importArchive(const QString &archive, const QString &root, const QString &compatibility);
QString activate(const QString &root, const QString &id, const QString &compatibility);
QString verify(const QString &root, const QString &id, const QString &compatibility);
QString exportArchive(const QString &root, const QString &id, const QString &archive, const QString &compatibility);
QString removeResource(const QString &root, const QString &id, const QString &currentSession);
bool userEnabled(const QString &root);
QString setUserEnabled(const QString &root, bool enabled);
QStringList userFiles(const QString &root);
QString userFileError(const QString &root, const QString &relative, const QString &bundledRoot);
QString saveUserFile(const QString &root, const QString &relative, const QByteArray &data, const QString &bundledRoot);
QString deleteUserFile(const QString &root, const QString &relative, const QString &bundledRoot);
QString refreshUserIndex(const QString &root);
QString exportUserArchive(const QString &root, const QString &archive, const QString &bundledRoot);
QString restoreUserArchive(const QString &root, const QString &archive, const QString &bundledRoot, bool merge = false);
QString createUserFolder(const QString &root, const QString &relative, const QString &bundledRoot);
QStringList userConflicts(const QString &root, const QString &relative, const QString &bundledRoot, const QString &id);
void showUserDialog(QWidget *parent);
void configure(QProcessEnvironment &env, const QString &bundledRoot, const QString &storage, const QString &id);
void showDialog(QWidget *parent);
}
#endif
