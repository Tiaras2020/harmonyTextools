#include "harmonyresources.h"
#include "harmonyRelease.h"
#include <QCryptographicHash>
#include <QDir>
#include <QDirIterator>
#include <QDateTime>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLockFile>
#include <QMap>
#include <QRegularExpression>
#include <QSaveFile>
#include <QSet>
#include <QStandardPaths>
#include <QStorageInfo>
#include <QTemporaryDir>
#include <QUuid>
#include <quazip.h>
#include <quazipfile.h>
#include <quazipnewinfo.h>

namespace HarmonyResources {
namespace {
const qint64 maxTotal = qint64(8) * 1024 * 1024 * 1024;
const qint64 maxFile = qint64(256) * 1024 * 1024;
bool validId(const QString &id) { return QRegularExpression("^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}$").match(id).hasMatch(); }
bool safePath(const QString &name) {
    if (name.isEmpty() || name.startsWith('/') || name.contains('\\') || name.contains(':') || name.contains(QChar(0))) return false;
    for (const QChar c : name) if (c.unicode() < 32) return false;
    const QStringList parts = name.split('/');
    for (const QString &p : parts) if (p.isEmpty() || p == "." || p == "..") return false;
    return true;
}
bool allowed(const QString &name, bool luaResources = false) {
    if (!safePath(name)) return false;
    const QString suffix = QFileInfo(name).suffix().toLower();
    // B1 is an additive resource profile. Executables, formats, core replacements
    // and Type1/map installers require the later full-resource profile.
    if (name.startsWith("texmf/tex/latex/") || name.startsWith("texmf/tex/generic/")
        || (luaResources && name.startsWith("texmf/tex/luatex/"))) {
        static const QSet<QString> extensions = {"sty", "cls", "tex", "def", "fd", "cfg", "clo", "ltx", "ldf"};
        const QString part = name.section('/', 3, 3).toLower();
        return (extensions.contains(suffix) || (luaResources && suffix == "lua"))
            && part != "base" && part != "latexconfig" && !part.startsWith("l3")
            && QFileInfo(name).fileName().toLower() != "language.dat.lua";
    }
    if (name.startsWith("texmf/bibtex/")) return suffix == "bib" || suffix == "bst";
    if (name.startsWith("texmf/fonts/opentype/")) return suffix == "otf";
    if (name.startsWith("texmf/fonts/truetype/")) return suffix == "ttf" || suffix == "ttc";
    if (name.startsWith("texmf/doc/")) return suffix == "txt" || suffix == "md" || suffix == "pdf";
    return false;
}
bool fullAllowed(const QString &name, bool reviewedAssets = false) {
    if (!safePath(name) || !name.startsWith("texmf/")) return false;
    const QString path = name.mid(6);
    if (path.startsWith("tex/latex/base/") || path.startsWith("tex/latex/latexconfig/")
        || path.startsWith("tex/latex/l3") || path.startsWith("fonts/conf/")) return false;
    bool prefix = false;
    for (const QString &p : {QString("tex/latex/"), QString("tex/generic/"), QString("tex/plain/"),
        QString("tex/xelatex/"), QString("tex/xetex/"), QString("bibtex/"), QString("makeindex/"), QString("fonts/")})
        if (path.startsWith(p)) prefix = true;
    if (!prefix) return false;
    if (path.startsWith("fonts/cmap/")) return true;
    const QString suffix = QFileInfo(path).suffix().toLower();
    if (reviewedAssets && ((path.startsWith("tex/latex/beamer/") && (suffix == "pdf" || suffix == "eps"))
        || (path.startsWith("tex/latex/translator/") && suffix == "dict")
        || (path.startsWith("tex/latex/newpx/") && suffix == "fontspec"))) return true;
    static const QSet<QString> extensions = {"sty", "cls", "tex", "def", "fd", "cfg", "clo", "ltx", "ldf", "cld",
        "bbx", "cbx", "lbx", "dbx", "bst", "bib", "ist", "xdy", "tfm", "vf", "pfb", "afm", "enc", "map",
        "otf", "ttf", "ttc", "pfm", "sfd", "dat", "tec", "pro", "cmap", "mkii", "txt"};
    return extensions.contains(QFileInfo(path).suffix().toLower());
}
bool writeAtomic(const QString &path, const QByteArray &data) {
    QSaveFile file(path);
    return file.open(QIODevice::WriteOnly) && file.write(data) == data.size() && file.commit();
}
QJsonObject readObject(const QString &path) {
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly) || f.size() > 64*1024*1024) return {};
    return QJsonDocument::fromJson(f.readAll()).object();
}
QString manifestError(const QJsonObject &m, const QString &compatibility) {
    const QString profile = m.value("profile").toString();
    const bool full = profile == "runtime-extension-v1" || profile == "runtime-extension-v2";
    if (m.value("schema").toInt() != 1 || (!full && profile != "additive-v1" && profile != "additive-lua-v1")) return "Unsupported resource package format";
    if (m.value("compatibilityId").toString() != compatibility) return "Resource package does not match this engine/kernel baseline";
    if (!validId(m.value("id").toString()) || !validId(m.value("version").toString())) return "Invalid resource id/version";
    const auto files = m.value("files").toObject();
    if (files.isEmpty() || files.size() > 200000) return "Invalid resource file count";
    qint64 total = 0;
    for (auto i = files.begin(); i != files.end(); ++i) {
        const auto f = i.value().toObject();
        const double size = f.value("size").toDouble(-1);
        if (!(full ? fullAllowed(i.key(), profile == "runtime-extension-v2") : allowed(i.key(), profile == "additive-lua-v1")) || size < 0 || size > maxFile || size != qint64(size)
            || !QRegularExpression("^[0-9a-f]{64}$").match(f.value("sha256").toString()).hasMatch()) return "Invalid or unsupported resource entry: " + i.key();
        total += qint64(size);
        if (total > maxTotal) return "Resource package exceeds 8 GiB limit";
    }
    return {};
}
QString makeIndex(const QString &tree) {
    QMap<QString, QStringList> dirs;
    dirs["."] = QStringList();
    QDirIterator it(tree, QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);
    while (it.hasNext()) {
        it.next();
        QString rel = QDir(tree).relativeFilePath(it.filePath());
        QString parent = QFileInfo(rel).path();
        dirs[parent].append(QFileInfo(rel).fileName());
        if (it.fileInfo().isDir()) dirs[rel];
    }
    QByteArray data = "% ls-R -- filename database for kpathsea; do not change this line.\n\n";
    for (auto i = dirs.begin(); i != dirs.end(); ++i) {
        i.value().sort();
        data += (i.key() == "." ? QString(".") : "./" + i.key()).toUtf8() + ":\n";
        for (const QString &file : i.value()) data += file.toUtf8() + '\n';
        data += '\n';
    }
    return writeAtomic(tree + "/ls-R", data) ? QString() : "Could not save ls-R";
}
}

QString storageRoot() {
    const QString base = QStandardPaths::writableLocation(QStandardPaths::AppLocalDataLocation);
    return base.isEmpty() ? QString() : base + "/tex-resources";
}

QString sessionResource() {
    // Pinned for this process. Import/rollback changes take effect after restart,
    // including all subprocesses in a multi-pass build.
    static const QString selected = []() {
        const QString root = storageRoot();
        if (root.isEmpty()) return QString();
        const QString id = readObject(root + "/active.json").value("id").toString();
        if (!validId(id)) return QString();
        const auto m = readObject(root + "/resources/" + id + "/manifest.json");
        return manifestError(m, HARMONY_TEX_COMPATIBILITY).isEmpty() ? id : QString();
    }();
    return selected;
}

QString selectedResource(const QString &root) {
    return readObject(root + "/active.json").value("id").toString();
}

QStringList installed(const QString &root) {
    QStringList result;
    for (const auto &name : QDir(root + "/resources").entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name))
        if (validId(name) && QFileInfo::exists(root + "/resources/" + name + "/manifest.json")) result.append(name);
    return result;
}

Result importArchive(const QString &archive, const QString &root, const QString &compatibility) {
    if (root.isEmpty() || !QDir().mkpath(root + "/resources")) return {{}, "Cannot create persistent resource directory"};
    QLockFile lock(root + "/import.lock");
    if (!lock.tryLock(0)) return {{}, "Another resource operation is in progress"};
    QuaZip zip(archive);
    zip.setFileNameCodec("UTF-8");
    if (!zip.open(QuaZip::mdUnzip)) return {{}, "Cannot open resource ZIP"};
    auto entries = zip.getFileInfoList64();
    if (zip.getZipError() != UNZ_OK || entries.size() > 220000) return {{}, "Invalid ZIP directory"};
    QSet<QString> names;
    qint64 total = 0;
    for (const auto &entry : entries) {
        QString name = entry.name;
        const bool dir = name.endsWith('/');
        if (dir) name.chop(1);
        const quint32 type = (entry.externalAttr >> 16) & 0170000;
        if (!safePath(name) || names.contains(entry.name) || entry.isEncrypted()
            || (type && type != 0100000 && type != 0040000) || (!dir && type == 0040000)
            || entry.uncompressedSize > quint64(maxFile)) return {{}, "Unsafe ZIP entry: " + entry.name};
        names.insert(entry.name);
        total += qint64(entry.uncompressedSize);
        if (total > maxTotal) return {{}, "Resource ZIP exceeds 8 GiB limit"};
    }
    if (!zip.setCurrentFile("manifest.json", QuaZip::csSensitive)) return {{}, "manifest.json is missing"};
    QuaZipFile manifestFile(&zip);
    if (!manifestFile.open(QIODevice::ReadOnly)) return {{}, "Cannot read manifest"};
    const QByteArray manifestBytes = manifestFile.read(64*1024*1024 + 1);
    manifestFile.close();
    if (manifestBytes.size() > 64*1024*1024 || manifestFile.getZipError() != UNZ_OK) return {{}, "Invalid manifest"};
    const auto manifest = QJsonDocument::fromJson(manifestBytes).object();
    QString error = manifestError(manifest, compatibility);
    if (!error.isEmpty()) return {{}, error};
    const auto files = manifest.value("files").toObject();
    int count = 0;
    for (const auto &entry : entries) {
        if (entry.name.endsWith('/') || entry.name == "manifest.json") continue;
        if (!files.contains(entry.name) || qint64(entry.uncompressedSize) != qint64(files.value(entry.name).toObject().value("size").toDouble())) return {{}, "ZIP and manifest disagree"};
        count++;
    }
    if (count != files.size()) return {{}, "Manifest references missing files"};
    QStorageInfo storage(root);
    const qint64 reserve = manifest.value("profile").toString() != "additive-v1" ? qint64(1024)*1024*1024 : 64*1024*1024;
    if (!storage.isValid() || !storage.isReady() || storage.bytesAvailable() < 0) return {{}, "Cannot determine available storage"};
    if (storage.bytesAvailable() < total + reserve) return {{}, "Insufficient free space"};
    const QString id = manifest.value("id").toString().left(35) + "-" + manifest.value("version").toString().left(35) + "-"
        + QString::fromLatin1(QCryptographicHash::hash(manifestBytes, QCryptographicHash::Sha256).toHex().left(16));
    if (QFileInfo::exists(root + "/resources/" + id)) return {{}, "This resource version is already installed"};
    QTemporaryDir stage(root + "/.import-XXXXXX");
    if (!stage.isValid()) return {{}, "Cannot create import staging directory"};
    for (auto i = files.begin(); i != files.end(); ++i) {
        if (!zip.setCurrentFile(i.key(), QuaZip::csSensitive)) return {{}, "Missing ZIP entry"};
        QuaZipFile input(&zip);
        const QString target = stage.path() + "/" + i.key();
        QDir().mkpath(QFileInfo(target).absolutePath());
        QFile output(target);
        if (!input.open(QIODevice::ReadOnly) || !output.open(QIODevice::WriteOnly)) return {{}, "Cannot extract resource: " + i.key()};
        QCryptographicHash hash(QCryptographicHash::Sha256);
        qint64 size = 0;
        const qint64 expected = qint64(i.value().toObject().value("size").toDouble());
        while (!input.atEnd()) {
            const QByteArray block = input.read(1024*1024);
            if (block.isEmpty()) return {{}, "ZIP read failure"};
            size += block.size();
            if (size > expected || output.write(block) != block.size()) return {{}, "Extraction size/write error"};
            hash.addData(block);
        }
        input.close(); output.close();
        if (input.getZipError() != UNZ_OK || size != expected || hash.result().toHex() != i.value().toObject().value("sha256").toString().toLatin1()) return {{}, "Resource checksum mismatch: " + i.key()};
    }
    error = makeIndex(stage.path() + "/texmf");
    if (!error.isEmpty()) return {{}, error};
    if (!writeAtomic(stage.path() + "/manifest.json", manifestBytes)) return {{}, "Could not save manifest"};
    if (!QDir().rename(stage.path(), root + "/resources/" + id)) return {{}, "Could not commit resource version"};
    stage.setAutoRemove(false);
    return {id, {}};
}

QString verify(const QString &root, const QString &id, const QString &compatibility) {
    if (!validId(id)) return "Invalid resource selection";
    const QString base = root + "/resources/" + id;
    if (QFileInfo(base).isSymLink()) return "Resource directory must not be a link";
    const auto manifest = readObject(base + "/manifest.json");
    QString error = manifestError(manifest, compatibility);
    if (!error.isEmpty()) return error;
    const auto files = manifest.value("files").toObject();
    for (auto i = files.begin(); i != files.end(); ++i) {
        QFile f(base + "/" + i.key());
        if (QFileInfo(f).isSymLink() || !f.open(QIODevice::ReadOnly) || f.size() != qint64(i.value().toObject().value("size").toDouble())) return "Missing/changed resource: " + i.key();
        QCryptographicHash hash(QCryptographicHash::Sha256);
        if (!hash.addData(&f) || hash.result().toHex() != i.value().toObject().value("sha256").toString().toLatin1()) return "Checksum mismatch: " + i.key();
    }
    return makeIndex(base + "/texmf");
}

QString activate(const QString &root, const QString &id, const QString &compatibility) {
    if (root.isEmpty() || !QDir().mkpath(root)) return "Cannot create resource directory";
    QLockFile lock(root + "/import.lock");
    if (!lock.tryLock(0)) return "Another resource operation is in progress";
    if (!id.isEmpty()) {
        const QString error = verify(root, id, compatibility);
        if (!error.isEmpty()) return error;
    }
    QJsonObject state; state.insert("id", id);
    return writeAtomic(root + "/active.json", QJsonDocument(state).toJson()) ? QString() : "Cannot save active resource selection";
}

QString exportArchive(const QString &root, const QString &id, const QString &archive, const QString &compatibility) {
    QLockFile lock(root + "/import.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个资源操作正在进行。");
    const QString error = verify(root, id, compatibility);
    if (!error.isEmpty()) return error;
    // Never allow an export destination to replace an installed resource or its state.
    const QString parent = QFileInfo(archive).absoluteDir().canonicalPath();
    const QString canonicalRoot = QDir(root).canonicalPath();
    if (parent.isEmpty() || parent == canonicalRoot || parent.startsWith(canonicalRoot + "/") || QFileInfo(archive).isSymLink())
        return QStringLiteral("请选择应用资源目录之外的导出位置。");
    const QString base = root + "/resources/" + id;
    const auto manifest = readObject(base + "/manifest.json");
    QStringList names = manifest.value("files").toObject().keys();
    names.prepend("manifest.json");
    QSaveFile output(archive);
    if (!output.open(QIODevice::WriteOnly)) return QStringLiteral("无法创建导出文件：") + output.errorString();
    QuaZip zip(&output);
    zip.setAutoClose(false);
    zip.setFileNameCodec("UTF-8");
    if (!zip.open(QuaZip::mdCreate)) return QStringLiteral("无法创建 ZIP。");
    for (const QString &name : names) {
        QFile input(base + "/" + name);
        QuaZipFile entry(&zip);
        QuaZipNewInfo info(name);
        info.externalAttr = 0100644u << 16;
        if (!input.open(QIODevice::ReadOnly) || !entry.open(QIODevice::WriteOnly, info))
            return QStringLiteral("无法导出文件：") + name;
        while (!input.atEnd()) {
            const QByteArray block = input.read(1024 * 1024);
            if (block.isEmpty() || entry.write(block) != block.size()) return QStringLiteral("导出读写失败：") + name;
        }
        entry.close();
        if (entry.getZipError() != UNZ_OK) return QStringLiteral("ZIP 写入失败：") + name;
    }
    zip.close();
    if (zip.getZipError() != UNZ_OK || !output.commit()) return QStringLiteral("导出文件保存失败。");
    return {};
}

QString removeResource(const QString &root, const QString &id, const QString &currentSession) {
    if (!validId(id)) return QStringLiteral("无效的资源版本。");
    QLockFile lock(root + "/import.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个资源操作正在进行。");
    if (id == currentSession) return QStringLiteral("当前会话正在使用此资源。请先恢复内置资源或启用其他版本，完全退出并重新打开应用后再删除。");
    if (id == selectedResource(root)) return QStringLiteral("此资源已安排在下次启动时启用。请先恢复内置资源或启用其他版本，再删除。");
    const QString parent = QDir(root + "/resources").canonicalPath();
    const QString target = root + "/resources/" + id;
    const QFileInfo info(target);
    if (parent.isEmpty() || info.isSymLink() || !info.isDir() || info.canonicalFilePath() != parent + "/" + id)
        return QStringLiteral("资源目录不存在或路径异常。");
    if (!QDir(target).removeRecursively()) return QStringLiteral("资源未能完全删除，请重试。");
    const QString cacheParent = QDir(root + "/var/" + HARMONY_TEX_COMPATIBILITY).canonicalPath();
    const QFileInfo cache(root + "/var/" + HARMONY_TEX_COMPATIBILITY + "/" + id);
    if (cache.exists()) {
        if (cacheParent.isEmpty() || cache.isSymLink() || cache.canonicalFilePath() != cacheParent + "/" + id
            || !QDir(cache.absoluteFilePath()).removeRecursively())
            return QStringLiteral("资源已删除，但该版本的缓存未能清理。");
    }
    return {};
}

bool userEnabled(const QString &root) {
    return readObject(root + "/user-state.json").value("enabled").toBool(true);
}

QString setUserEnabled(const QString &root, bool enabled) {
    if (!QDir().mkpath(root)) return QStringLiteral("无法建立用户资源目录。");
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    QJsonObject state; state.insert("enabled", enabled);
    return writeAtomic(root + "/user-state.json", QJsonDocument(state).toJson()) ? QString() : QStringLiteral("无法保存用户资源设置。");
}

QStringList userFiles(const QString &root) {
    QStringList files;
    const QString tree = root + "/texmf-home";
    if (QFileInfo(tree).isSymLink()) return files;
    QDirIterator it(tree, QDir::Files | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);
    while (it.hasNext()) {
        it.next();
        const QString relative = QDir(tree).relativeFilePath(it.filePath());
        if (!it.fileInfo().isSymLink() && allowed("texmf/" + relative, true)) files.append(relative);
    }
    files.sort();
    return files;
}

QString userFileError(const QString &root, const QString &relative, const QString &bundledRoot) {
    if (!allowed("texmf/" + relative, true)) return QStringLiteral("不支持的用户资源路径或类型：") + relative;
    const QString tree = root + "/texmf-home";
    QString path = tree;
    if (QFileInfo(path).isSymLink()) return QStringLiteral("用户资源目录不能是符号链接。");
    for (const QString &part : relative.split('/')) {
        path += "/" + part;
        if (QFileInfo(path).isSymLink()) return QStringLiteral("用户资源路径不能包含符号链接。");
    }
    // Block core files by basename too: putting latex.ltx in another directory
    // must not bypass the directory restrictions of the additive profile.
    const QString name = QFileInfo(relative).fileName();
    if (relative.startsWith("tex/")) {
        const QString latex = bundledRoot + "/texmf/tex/latex";
        if (!QDir(latex + "/base").exists()) return QStringLiteral("无法读取基础内核清单，不能验证此宏包。");
        for (const QString &part : QDir(latex).entryList(QDir::Dirs | QDir::NoDotAndDotDot)) {
            if (part != "base" && part != "latexconfig" && !part.startsWith("l3")) continue;
            QDirIterator it(latex + "/" + part, QStringList{name}, QDir::Files, QDirIterator::Subdirectories);
            if (it.hasNext()) return QStringLiteral("此文件属于受保护的内核/基础组件：") + name;
        }
        static const QSet<QString> core = {"plain.tex", "hyphen.tex", "language.dat", "language.def", "language.dat.lua", "texmf.cnf"};
        if (core.contains(name)) return QStringLiteral("此文件属于受保护的基础组件：") + name;
    }
    return {};
}

QString refreshUserIndex(const QString &root) {
    const QString tree = root + "/texmf-home";
    if (QFileInfo(tree).isSymLink() || !QDir().mkpath(tree)) return QStringLiteral("无法创建用户资源目录。");
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    const QString error = makeIndex(tree);
    if (!error.isEmpty()) return error;
    return writeAtomic(root + "/user-font-revision", QUuid::createUuid().toString(QUuid::WithoutBraces).toLatin1()) ? QString() : QStringLiteral("无法刷新字体缓存版本。");
}

QString saveUserFile(const QString &root, const QString &relative, const QByteArray &data, const QString &bundledRoot) {
    const QString error = userFileError(root, relative, bundledRoot);
    if (!error.isEmpty()) return error;
    if (data.size() > maxFile) return QStringLiteral("单个用户文件不能超过 256 MiB。");
    const QString target = root + "/texmf-home/" + relative;
    if (!QDir().mkpath(QFileInfo(target).absolutePath())) return QStringLiteral("无法建立用户文件目录。");
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    if (!writeAtomic(target, data)) return QStringLiteral("无法保存用户文件。");
    if (relative.startsWith("fonts/") && !writeAtomic(root + "/user-font-revision", QUuid::createUuid().toString(QUuid::WithoutBraces).toLatin1())) return QStringLiteral("文件已保存，但字体缓存版本未能刷新。");
    return makeIndex(root + "/texmf-home");
}

QString deleteUserFile(const QString &root, const QString &relative, const QString &bundledRoot) {
    const QString error = userFileError(root, relative, bundledRoot);
    if (!error.isEmpty()) return error;
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    if (!QFile::remove(root + "/texmf-home/" + relative)) return QStringLiteral("无法删除用户文件。");
    if (relative.startsWith("fonts/") && !writeAtomic(root + "/user-font-revision", QUuid::createUuid().toString(QUuid::WithoutBraces).toLatin1())) return QStringLiteral("文件已删除，但字体缓存版本未能刷新。");
    return makeIndex(root + "/texmf-home");
}

QStringList userConflicts(const QString &root, const QString &relative, const QString &bundledRoot, const QString &id) {
    QStringList found, trees{bundledRoot + "/texmf"};
    if (validId(id)) trees.append(root + "/resources/" + id + "/texmf");
    const QString kind = relative.section('/', 0, 0);
    for (const QString &tree : trees) {
        QDirIterator it(tree + "/" + kind, QStringList{QFileInfo(relative).fileName()}, QDir::Files, QDirIterator::Subdirectories);
        while (it.hasNext()) found.append(it.next());
    }
    for (const QString &file : userFiles(root))
        if (file != relative && QFileInfo(file).fileName() == QFileInfo(relative).fileName()) found.append(root + "/texmf-home/" + file);
    return found;
}

QString exportUserArchive(const QString &root, const QString &archive, const QString &bundledRoot) {
    if (!QDir().mkpath(root)) return QStringLiteral("无法建立用户目录。");
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    const QString parent = QFileInfo(archive).absoluteDir().canonicalPath();
    const QString canonicalRoot = QDir(root).canonicalPath();
    if (parent.isEmpty() || parent == canonicalRoot || parent.startsWith(canonicalRoot + "/")) return QStringLiteral("请选择用户资源目录之外的备份位置。");
    QTemporaryDir temp(root + "/.user-export-XXXXXX");
    if (!temp.isValid()) return QStringLiteral("无法建立备份暂存目录。");
    const QString id = "user-backup";
    const QString snapshot = temp.path() + "/resources/" + id;
    QJsonObject files;
    for (const QString &relative : userFiles(root)) {
        const QString error = userFileError(root, relative, bundledRoot);
        if (!error.isEmpty()) return error;
        QFile input(root + "/texmf-home/" + relative);
        if (!input.open(QIODevice::ReadOnly) || input.size() > maxFile) return QStringLiteral("无法读取备份文件：") + relative;
        const QString target = snapshot + "/texmf/" + relative;
        QDir().mkpath(QFileInfo(target).absolutePath());
        QFile output(target);
        if (!output.open(QIODevice::WriteOnly)) return QStringLiteral("无法写入备份暂存文件。");
        QCryptographicHash hash(QCryptographicHash::Sha256);
        qint64 size = 0;
        while (!input.atEnd()) {
            const QByteArray block = input.read(1024 * 1024);
            if (block.isEmpty() || output.write(block) != block.size()) return QStringLiteral("备份读写失败。");
            hash.addData(block); size += block.size();
        }
        QJsonObject entry; entry.insert("size", double(size)); entry.insert("sha256", QString::fromLatin1(hash.result().toHex()));
        files.insert("texmf/" + relative, entry);
    }
    if (files.isEmpty()) return QStringLiteral("用户资源为空，无需备份。");
    QJsonObject manifest;
    bool needsLuaProfile = false;
    for (auto it = files.begin(); it != files.end(); ++it)
        if (!allowed(it.key())) needsLuaProfile = true;
    manifest.insert("schema", 1); manifest.insert("profile", needsLuaProfile ? "additive-lua-v1" : "additive-v1");
    manifest.insert("id", id); manifest.insert("version", QDateTime::currentDateTimeUtc().toString("yyyyMMddHHmmsszzz"));
    manifest.insert("title", QStringLiteral("用户资源备份")); manifest.insert("compatibilityId", HARMONY_TEX_COMPATIBILITY);
    manifest.insert("files", files);
    if (!writeAtomic(snapshot + "/manifest.json", QJsonDocument(manifest).toJson())) return QStringLiteral("无法写入备份清单。");
    return exportArchive(temp.path(), id, archive, HARMONY_TEX_COMPATIBILITY);
}

QString createUserFolder(const QString &root, const QString &relative, const QString &bundledRoot) {
    QString suffix = "sty";
    if (relative.startsWith("fonts/opentype/")) suffix = "otf";
    else if (relative.startsWith("fonts/truetype/")) suffix = "ttf";
    else if (relative.startsWith("bibtex/")) suffix = "bib";
    else if (relative.startsWith("doc/")) suffix = "txt";
    const QString error = userFileError(root, relative + "/folder-validation." + suffix, bundledRoot);
    if (!error.isEmpty()) return error;
    if (!QDir().mkpath(root)) return QStringLiteral("无法创建用户目录。");
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    return QDir().mkpath(root + "/texmf-home/" + relative) ? QString() : QStringLiteral("无法创建文件夹。");
}

QString restoreUserArchive(const QString &root, const QString &archive, const QString &bundledRoot, bool merge) {
    if (!QDir().mkpath(root)) return QStringLiteral("无法建立用户目录。");
    QLockFile lock(root + "/user.lock");
    if (!lock.tryLock(0)) return QStringLiteral("另一个用户资源操作正在进行。");
    QTemporaryDir temp(root + "/.user-restore-XXXXXX");
    if (!temp.isValid()) return QStringLiteral("无法建立恢复暂存目录。");
    const Result imported = importArchive(archive, temp.path(), HARMONY_TEX_COMPATIBILITY);
    if (!imported.error.isEmpty()) return imported.error;
    const QString staged = temp.path() + "/resources/" + imported.id;
    const auto files = readObject(staged + "/manifest.json").value("files").toObject();
    for (auto i = files.begin(); i != files.end(); ++i) {
        const QString error = userFileError(root, i.key().mid(6), bundledRoot);
        if (!error.isEmpty()) return error;
    }
    const QString target = root + "/texmf-home";
    if (QFileInfo(target).isSymLink()) return QStringLiteral("用户目录不能是符号链接。");
    if (merge) {
        // Compose a complete replacement before touching the current tree. A
        // conflicting path rejects the entire import, even if bytes match.
        QDirIterator it(target, QDir::Files | QDir::Dirs | QDir::Hidden | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);
        qint64 total = 0;
        for (auto i = files.begin(); i != files.end(); ++i) total += qint64(i.value().toObject().value("size").toDouble());
        while (it.hasNext()) {
            it.next();
            const QString relative = QDir(target).relativeFilePath(it.filePath());
            if (it.fileInfo().isSymLink()) return QStringLiteral("原用户树含符号链接，未执行导入。");
            const QString destination = staged + "/texmf/" + relative;
            if (it.fileInfo().isDir()) {
                if (!QDir().mkpath(destination)) return QStringLiteral("无法暂存用户文件夹。");
                continue;
            }
            if (relative == "ls-R") continue;
            const QString error = userFileError(root, relative, bundledRoot);
            if (!error.isEmpty()) return error;
            if (QFileInfo::exists(destination)) return QStringLiteral("导入包与现有用户文件冲突，未修改任何文件：\n") + relative;
            total += it.fileInfo().size();
            if (it.fileInfo().size() > maxFile || total > maxTotal) return QStringLiteral("合并后的用户资源超过大小限制。");
            if (!QDir().mkpath(QFileInfo(destination).absolutePath()) || !QFile::copy(it.filePath(), destination))
                return QStringLiteral("无法暂存现有用户文件，未执行导入：") + relative;
        }
        const QString error = makeIndex(staged + "/texmf");
        if (!error.isEmpty()) return error;
    }
    if (!writeAtomic(root + "/user-font-revision", QUuid::createUuid().toString(QUuid::WithoutBraces).toLatin1())) return QStringLiteral("无法刷新字体缓存版本，未执行恢复。");
    const bool exists = QFileInfo::exists(target);
    const QString old = temp.path() + "/previous";
    if (exists && !QDir().rename(target, old)) return QStringLiteral("无法暂存原用户资源，未执行恢复。");
    if (!QDir().rename(staged + "/texmf", target)) {
        if (exists && !QDir().rename(old, target)) {
            temp.setAutoRemove(false);
            return QStringLiteral("恢复失败，原资源保留在：") + old;
        }
        return QStringLiteral("恢复失败，已保留原用户资源。");
    }
    return {};
}

void configure(QProcessEnvironment &env, const QString &bundledRoot, const QString &storage, const QString &id) {
    if (storage.isEmpty()) return;
    const QString base = bundledRoot + "/texmf";
    QStringList trees{base};
    if (validId(id)) trees.append(storage + "/resources/" + id + "/texmf");
    // Mutable user resources are read again for each compiler invocation.
    if (userEnabled(storage) && !QFileInfo(storage + "/texmf-home").isSymLink()) trees.prepend(storage + "/texmf-home");
    env.insert("TEXMF", "{" + trees.join(',') + "}");
    env.insert("TEXMFDBS", trees.join(':'));
    env.insert("TEXMFHOME", storage + "/texmf-home");
    env.insert("TEXMFVAR", storage + "/var/" + HARMONY_TEX_COMPATIBILITY + "/" + (id.isEmpty() ? "builtin" : id));
    QFile revisionFile(storage + "/user-font-revision");
    revisionFile.open(QIODevice::ReadOnly);
    QString revision = QString::fromLatin1(revisionFile.read(128)).trimmed();
    if (!validId(revision)) revision = "initial";
    env.insert("TEXMFVAR", env.value("TEXMFVAR") + (userEnabled(storage) ? "/user-" + revision : "/without-user"));
    // Kpathsea permits Lua cache writes below TEXMFVAR with openout_any=p.
    // Keep the cache tied to the active resource set and user font revision.
    env.insert("TEXMFCACHE", env.value("TEXMFVAR"));
    env.insert("TEXMFCONFIG", storage + "/config");
    for (const QString &key : {QString("TEXMFHOME"), QString("TEXMFVAR"), QString("TEXMFCONFIG")}) QDir().mkpath(env.value(key));
    auto paths = [&](const QString &suffix) { QStringList list{"."}; for (const QString &tree : trees) list.append(tree + suffix); return list.join(':'); };
    const QString tex = paths("/tex/{plain,generic,latex,xelatex,xetex,luatex}//");
    env.insert("TEXINPUTS", tex);
    for (const QString &engine : {QString("pdftex"), QString("pdflatex"), QString("tex"), QString("xetex"), QString("xelatex"), QString("luahbtex"), QString("lualatex")}) env.insert("TEXINPUTS." + engine, tex);
    env.insert("LUAINPUTS", paths("/{tex,scripts}//"));
    env.insert("BIBINPUTS", paths("/bibtex/bib//"));
    env.insert("BSTINPUTS", paths("/bibtex/{bst,csf}//"));
    env.insert("OPENTYPEFONTS", paths("/fonts/opentype//"));
    env.insert("TRUETYPEFONTS", paths("/fonts/truetype//"));
    env.insert("TFMFONTS", paths("/fonts/tfm//"));
    env.insert("VFFONTS", paths("/fonts/vf//"));
    env.insert("T1FONTS", paths("/fonts/type1//"));
    env.insert("AFMFONTS", paths("/fonts/afm//"));
    env.insert("ENCFONTS", paths("/fonts/enc//"));
    env.insert("SFDFONTS", paths("/fonts/sfd//"));
    env.insert("CMAPFONTS", paths("/fonts/cmap//"));
    // Driver configuration can contain external conversion commands; keep it bundled.
    env.insert("DVIPDFMXINPUTS", base + "/dvipdfmx//");
    env.insert("XDVIPDFMXINPUTS", base + "/dvipdfmx//");
    env.insert("INDEXSTYLE", paths("/makeindex//"));
    QStringList mapTrees{base};
    const QString activeProfile = validId(id) ? readObject(storage + "/resources/" + id + "/manifest.json").value("profile").toString() : QString();
    if (validId(id) && (activeProfile == "runtime-extension-v1" || activeProfile == "runtime-extension-v2"))
        mapTrees.prepend(storage + "/resources/" + id + "/texmf");
    QStringList maps;
    for (const QString &tree : mapTrees) maps.append(tree + "/fonts/map//");
    env.insert("TEXFONTMAPS", maps.join(':'));
    // Imported data cannot replace the executable/config/format search paths.
    env.insert("TEXFORMATS", base + "/web2c/{$engine,}");
    const QString cache = env.value("TEXMFVAR") + "/fontconfig";
    if (!QDir().mkpath(cache)) return;
    QString xml = "<?xml version=\"1.0\"?>\n<fontconfig>\n";
    for (const QString &tree : trees) for (const QString &kind : {QString("opentype"), QString("truetype")}) xml += "<dir>" + (tree + "/fonts/" + kind).toHtmlEscaped() + "</dir>\n";
    xml += "<dir>/system/fonts</dir>\n<cachedir>" + cache.toHtmlEscaped() + "</cachedir>\n</fontconfig>\n";
    const QString config = cache + "/fonts.conf";
    if (writeAtomic(config, xml.toUtf8())) env.insert("FONTCONFIG_FILE", config);
}
}
