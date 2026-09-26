#ifndef HARMONY_AI_TOOLS_H
#define HARMONY_AI_TOOLS_H
#include <QtCore>
#include <functional>
class HarmonyAiTools {
public:
    QString root;
    bool editable = false, deletable = false;
    // Open editor contents and modifications stay in the application's undo history.
    std::function<QJsonObject(const QString &)> buffer;
    std::function<QJsonObject(const QString &, const QString &, const QString &)> editBuffer;
    static QString revision(const QString &s) { return QString::fromLatin1(QCryptographicHash::hash(s.toUtf8(), QCryptographicHash::Sha256).toHex()); }
    static QJsonObject error(const QString &s) { return {{"error",s}}; }
    QString resolve(const QString &relative, bool artifact=false) const {
        if (root.isEmpty() || relative.isEmpty() || QDir::isAbsolutePath(relative) || relative.contains('\\')) return {};
        QStringList parts=relative.split('/');
        for (const auto &part:parts) if(part.isEmpty() || part==".." || part.startsWith('.')) return {};
        const QString suffix=QFileInfo(relative).suffix().toLower();
        if (!(artifact?QStringList{"log","pdf"}:QStringList{"tex","bib","sty","cls","txt","md","csv","tsv"}).contains(suffix)) return {};
        QString base=QFileInfo(root).canonicalFilePath(); if(base.isEmpty()) return {};
        QString p=base;
        for(const auto &part:parts) { p+='/'+part; if(QFileInfo(p).isSymLink()) return {}; }
        QString parent=QFileInfo(p).dir().canonicalPath();
        if(parent!=base && !parent.startsWith(base+'/')) return {};
        return QDir::cleanPath(p);
    }
    QJsonObject read(const QString &relative) const {
        QString path=resolve(relative); if(path.isEmpty()) return error("invalid_text_path");
        if(buffer) { auto b=buffer(path); if(b.value("open").toBool()) { if(b["text"].toString().size()>128*1024)return error("file_too_large"); b["path"]=relative; b["revision"]=revision(b["text"].toString()); return b; } }
        QFile f(path); if(!f.exists()) return error("file_missing");
        if(!QFileInfo(path).isFile()) return error("not_a_regular_file");
        if(f.size()>256*1024 || !f.open(QIODevice::ReadOnly)) return error("unreadable_or_too_large");
        QByteArray bytes=f.readAll(); QString text=QString::fromUtf8(bytes);
        if(bytes.contains('\0') || text.toUtf8()!=bytes) return error("utf8_text_required");
        return {{"path",relative},{"text",text},{"revision",revision(text)},{"open",false}};
    }
    QJsonObject run(const QString &name,const QJsonObject &a) {
        QString relative=a["path"].toString();
        if(name=="list_files") {
            QJsonArray files; if(root.isEmpty()) return error("no_project");
            QDirIterator it(root,QDir::Files|QDir::NoSymLinks,QDirIterator::Subdirectories);
            int visited=0;
            while(it.hasNext() && files.size()<300 && ++visited<10000) { auto p=it.next(); auto rel=QDir(root).relativeFilePath(p); if(!resolve(rel).isEmpty()) files.append(rel); }
            return {{"files",files},{"limit",300}};
        }
        if(name=="read_file") return read(relative);
        if(name=="read_log") {
            QString path=resolve(relative,true);if(path.isEmpty() || !path.endsWith(".log",Qt::CaseInsensitive))return error("invalid_log_path");
            QFile f(path);if(!f.exists())return error("file_missing");if(!QFileInfo(path).isFile() || !f.open(QIODevice::ReadOnly))return error("unreadable_log");
            qint64 bytes=f.size();if(bytes>96000)f.seek(bytes-96000);
            return {{"path",relative},{"text",QString::fromUtf8(f.readAll())},{"truncated",bytes>96000},{"modifiedAt",QFileInfo(path).lastModified().toUTC().toString(Qt::ISODate)},{"source","on_disk_log_may_be_stale"}};
        }
        if(name=="delete_file") {
            if(!deletable)return error("deletion_disabled");
            QString path=resolve(relative);if(path.isEmpty())return error("invalid_text_path");
            if(buffer && buffer(path)["open"].toBool())return error("close_document_before_deleting");
            auto original=read(relative);if(original.contains("error"))return original;
            if(a["revision"]!=original["revision"])return error("revision_mismatch_read_again");
            QString trash=root+"/.texstudio-ai-trash";
            if(QFileInfo(trash).isSymLink() || !QDir().mkpath(trash))return error("trash_unavailable");
            QString saved=QUuid::createUuid().toString(QUuid::WithoutBraces)+"-"+QFileInfo(path).fileName();
            if(!QFile::rename(path,trash+"/"+saved))return error("delete_failed");
            return {{"path",relative},{"movedTo",QStringLiteral(".texstudio-ai-trash/")+saved},{"recoverable",true}};
        }
        if(name!="replace_text" && name!="create_file") return error("unknown_tool");
        if(!editable) return error("read_only_mode");
        auto path=resolve(relative); if(path.isEmpty()) return error("invalid_text_path");
        QString text;
        if(name=="create_file") {
            if(QFileInfo::exists(path) || (buffer && buffer(path)["open"].toBool())) return error("already_exists");
            text=a["text"].toString();
        } else {
            auto original=read(relative); if(original.contains("error")) return original;
            if(original["conflict"].toBool()) return error("external_conflict_reload_or_resolve_first");
            text=original["text"].toString();
            if(a["revision"].toString()!=revision(text)) return error("revision_mismatch_read_again");
            QString before=a["old_text"].toString();
            if(before.isEmpty() || text.count(before)!=1) return error("old_text_must_match_exactly_once");
            text.replace(text.indexOf(before),before.size(),a["new_text"].toString());
            if(text.toUtf8().size()>256*1024) return error("file_too_large");
            if(original["open"].toBool() && editBuffer) return editBuffer(path,original["revision"].toString(),text);
            // Recheck immediately before atomic commit; all application calls run on UI thread.
            if(read(relative)["revision"]!=original["revision"]) return error("revision_mismatch_read_again");
        }
        QByteArray bytes=text.toUtf8(); if(bytes.size()>256*1024) return error("file_too_large");
        if(name=="create_file") {
            QFile f(path); if(!f.open(QIODevice::WriteOnly|QIODevice::NewOnly)) return error("create_failed");
            if(f.write(bytes)!=bytes.size()) return error("write_failed"); f.close();
        } else {
            QSaveFile f(path); if(!f.open(QIODevice::WriteOnly) || f.write(bytes)!=bytes.size() || !f.commit()) return error("write_failed");
        }
        return {{"path",relative},{"revision",revision(text)},{"saved",true}};
    }
    static QJsonArray schema(bool editable=true,bool deletable=false) {
        QJsonArray result;
        auto add=[&](QString name,QString description,QStringList keys) {
            QJsonObject properties; QJsonArray required;
            for(auto key:keys) { properties[key]=QJsonObject{{"type","string"}}; required.append(key); }
            result.append(QJsonObject{{"type","function"},{"function",QJsonObject{{"name",name},{"description",description},{"parameters",QJsonObject{{"type","object"},{"properties",properties},{"required",required},{"additionalProperties",false}}}}}});
        };
        add("list_files","List allowed project text files (bounded).",{});
        add("read_file","Read UTF-8 project file or current editor buffer and revision.",{"path"});
        if(editable)add("replace_text","Replace one exact occurrence, using revision from read_file. Open files change in editor undo history and remain unsaved; other files are saved atomically.",{"path","revision","old_text","new_text"});
        if(editable)add("create_file","Create a new UTF-8 project file; never overwrite. Parent directory must exist.",{"path","text"});
        add("read_log","Read last 96 KB of a project .log file with timestamp; not proof of latest build success.",{"path"});
        if(deletable)add("delete_file","Move an unopened UTF-8 project text file to .texstudio-ai-trash. Requires current revision; refuses open editor files.",{"path","revision"});
        return result;
    }
};
#endif
