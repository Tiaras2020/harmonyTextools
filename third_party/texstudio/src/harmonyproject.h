#ifndef HARMONY_PROJECT_H
#define HARMONY_PROJECT_H
#include <QDialog>
#include <QDir>
#include <QFileInfo>
#include <QFile>
#include <QCryptographicHash>
#include <QJsonArray>
#include <QJsonObject>
#include <QMap>
#include <QDateTime>
#include <QPointer>
#include <QProcess>
#include <QRegularExpression>
#include "harmonyautomation.h"

namespace HarmonyProject {
inline bool textFile(const QString &path) {
    return QStringList{"tex","sty","cls","bib","bst","lua","txt","md","csv","tsv","json","log","aux","toc","out","bbl","blg","fls","fdb_latexmk"}.contains(QFileInfo(path).suffix().toLower());
}
// Reject symlinks at every level, not just a final path whose canonical name escapes.
inline QString resolve(const QString &root, const QString &relative, bool directory = false, QString *failure = nullptr) {
    if (failure) *failure = "invalid_text_path";
    if (relative.isEmpty() || QDir::isAbsolutePath(relative) || relative.contains('\\') || relative.contains(QChar(0))) return {};
    // Validate the entire lexical path before reporting anything about disk
    // existence (including missing/../outside.tex and dangling symlinks).
    if (relative != ".") for (const QString &part : relative.split('/'))
        if (part.isEmpty() || part == "." || part == ".." || part.startsWith('.')) return {};
    if (QFileInfo(root).canonicalFilePath() != root || !QFileInfo(root).isDir()) return {};
    QString path = root;
    if (relative != ".") for (const QString &part : relative.split('/')) {
        if (QFileInfo(path).exists() && !QFileInfo(path).isDir()) return {};
        path += '/' + part;
        if (QFileInfo(path).isSymLink()) return {};
    }
    const QFileInfo info(path);
    if (!info.exists()) {
        if (failure) *failure = "file_missing";
        return {};
    }
    const QString canonical = info.canonicalFilePath();
    if (canonical != root && !canonical.startsWith(root + '/')) return {};
    if (canonical.isEmpty() || (directory ? !info.isDir() : !info.isFile())) return {};
    if (failure) failure->clear();
    return canonical;
}
// Buffer membership must not depend on whether its disk file still exists.
// This is only for listing/preflight, never for authorizing disk reads or writes.
inline QString documentPath(const QString &root, const QString &filename) {
    if (filename.isEmpty() || !QDir::isAbsolutePath(filename)) return {};
    const QString path=QDir(root).relativeFilePath(QDir::cleanPath(filename));
    if(path==".." || path.startsWith("../") || QDir::isAbsolutePath(path)) return {};
    return path;
}
inline QString digest(const QByteArray &data) { return QString::fromLatin1(QCryptographicHash::hash(data, QCryptographicHash::Sha256).toHex()); }
inline QString fileDigest(const QString &path, qint64 limit = 128*1024*1024) {
    QFile file(path);
    if (file.size() > limit || !file.open(QIODevice::ReadOnly)) return {};
    QCryptographicHash hash(QCryptographicHash::Sha256);
    if (!hash.addData(&file)) return {};
    return QString::fromLatin1(hash.result().toHex());
}
struct Job {
    QString id, master, engine, state = "queued", log, pdfBefore, pdfAfter, finalLog;
    QJsonArray blockers;
    bool finalLogAvailable = false, cleanRebuild = false;
    qint64 logStart = 0;
    int exitCode = 0;
    bool cancelled = false;
    QDateTime started, finished;
    void append(const QString &text) {
        log += text;
        if (log.size() > 262144) { logStart += log.size()-262144; log = log.right(262144); }
    }
    QJsonObject status() const {
        const bool terminal=state=="succeeded"||state=="failed"||state=="cancelled";
        return {{"ok",true},{"buildSucceeded",terminal?QJsonValue(state=="succeeded"):QJsonValue(QJsonValue::Null)},
                {"blockers",blockers},{"recoveryHint",blockers.isEmpty()?QJsonValue(QJsonValue::Null):QJsonValue(QStringLiteral("先用 document.read 检查阻塞文件并保留所需编辑；明确以磁盘为准时调用 document.reload --discard-local --expected-revision REV。"))},{"terminal",terminal},{"cleanRebuild",cleanRebuild},{"job",id},{"master",master},{"engine",engine},{"state",state},{"exitCode",terminal?QJsonValue(exitCode):QJsonValue(QJsonValue::Null)},
                {"started",started.toString(Qt::ISODateWithMs)},{"finished",finished.toString(Qt::ISODateWithMs)}};
    }
};
inline QJsonObject diagnostics(const Job &job,const QString &root) {
    QJsonArray items;
    const bool cached=job.state=="failed"&&job.log.contains("Nothing to do")&&!job.log.contains("Run number ");
    const QString source=job.finalLogAvailable?"final_engine_log":"build_output";
    // Never collect warnings from all TeX rounds. If no final log was captured,
    // retain only the last latexmk rule's output as a labelled fallback.
    QString text=job.finalLogAvailable?job.finalLog:job.log;
    if(!job.finalLogAvailable) {
        const int last=text.lastIndexOf("Run number ");
        if(last>=0)text=text.mid(last);
    }
    QRegularExpression pattern("^(.+\\.(?:tex|sty|cls|bib)):(\\d+):\\s*(.*)$");
    if(cached)items.append(QJsonObject{{"code","cached_previous_failure"},{"source","latexmk"},
        {"message",QStringLiteral("上次构建失败且输入未变化，latexmk 未重新编译。请修改相关文件，或使用 build.clean 清理失败缓存并重试。")},{"recoveryCommand","build.clean"}});
    for(const QString &raw:text.split('\n')) {
        const QString line=raw.trimmed();const auto match=pattern.match(line);
        QJsonObject item{{"source",source},{"message",line}};
        if(match.hasMatch()) {
            const QString candidate=QDir::isAbsolutePath(match.captured(1))?QDir(root).relativeFilePath(match.captured(1)):QDir::cleanPath(QFileInfo(job.master).path()+'/'+match.captured(1));
            const QString safe=resolve(root,candidate);
            if(!safe.isEmpty()){item.insert("path",QDir(root).relativeFilePath(safe));item.insert("line",match.captured(2).toInt());}
            item.insert("message",match.captured(3));
        } else if(!line.startsWith('!')&&!line.contains("Warning:")&&!line.startsWith("Overfull ")&&!line.startsWith("Underfull "))continue;
        items.append(item);if(items.size()>=200)break;
    }
    if(job.state=="failed"&&items.isEmpty())items.append(QJsonObject{{"code","build_failed"},{"source","build_output"},
        {"message",QStringLiteral("构建失败，未解析到文件行号；请读取 job.logs 查看完整输出。")}});
    return {{"ok",true},{"job",job.id},{"items",items},{"partial",true},{"source",source},
        {"buildSucceeded",job.status().value("buildSucceeded")},{"note","Final engine log when available; full multi-pass output remains in job.logs"}};
}
class Session : public QDialog {
public:
    HarmonyAutomation server;
    QString root, master, currentJob;
    QMap<QString, Job> jobs;
    QStringList order;
    bool connected = false;
    bool running = false;
    QPointer<QProcess> activeProcess;
    explicit Session(QWidget *parent) : QDialog(parent), server(this) { setAttribute(Qt::WA_DeleteOnClose); setModal(false); }
    void reject() override { if (!running) QDialog::reject(); }
};
}
#endif
