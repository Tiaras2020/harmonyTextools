#include "harmonyaitools.h"
#include "harmonychinesedict.h"
#include <cassert>
#include <iostream>
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);QTemporaryDir dir,outside;assert(dir.isValid());
    HarmonyAiTools t;t.root=dir.path();
    assert(t.run("create_file",{{"path","a.tex"},{"text","中文, \"quoted\": \\LaTeX\n"}})["error"]=="read_only_mode");
    t.editable=true;
    assert(t.run("create_file",{{"path","a.tex"},{"text","中文, \"quoted\": \\LaTeX\n"}})["saved"].toBool());
    assert(t.run("create_file",{{"path","a.tex"},{"text","overwrite"}})["error"]=="already_exists");
    for(QString p:{"../outside.tex","/etc/passwd",".env","a/../../b.tex","x\\a.tex","a.pdf"})assert(t.resolve(p).isEmpty());
    assert(QFile::link(outside.path(),dir.path()+"/link"));assert(t.resolve("link/b.tex").isEmpty());
    auto first=t.read("a.tex");
    assert(QDir(dir.path()).mkdir("directory.tex"));
    assert(t.read("directory.tex")["error"]=="not_a_regular_file");
    assert(t.run("replace_text",{{"path","a.tex"},{"revision","stale"},{"old_text","中文"},{"new_text","内容"}})["error"]=="revision_mismatch_read_again");
    assert(t.run("replace_text",{{"path","a.tex"},{"revision",first["revision"]},{"old_text","中文"},{"new_text","内容"}})["saved"].toBool());
    assert(t.read("a.tex")["text"].toString().startsWith(QStringLiteral("内容")));
    assert(t.run("replace_text",{{"path","a.tex"},{"revision",first["revision"]},{"old_text","内容"},{"new_text","旧版"}}).contains("error"));
    QString buffer="unsaved text";bool changed=false;
    t.buffer=[&](QString){return QJsonObject{{"open",true},{"text",buffer},{"modified",true}};};
    t.editBuffer=[&](QString,QString revision,QString text){assert(revision==HarmonyAiTools::revision(buffer));buffer=text;changed=true;return QJsonObject{{"saved",false},{"undoAvailable",true}};};
    auto b=t.read("a.tex");auto edited=t.run("replace_text",{{"path","a.tex"},{"revision",b["revision"]},{"old_text","unsaved"},{"new_text","edited"}});
    assert(changed && !edited["saved"].toBool() && buffer=="edited text");
    t.buffer={};t.editBuffer={};
    QFile log(dir.path()+"/main.log");assert(log.open(QIODevice::WriteOnly));log.write("final log warning");log.close();
    assert(t.run("read_log",{{"path","main.log"}})["text"]=="final log warning");
    assert(t.run("read_log",{{"path","../main.log"}})["error"]=="invalid_log_path");
    assert(t.run("read_log",{{"path","a.tex"}})["error"]=="invalid_log_path");
    assert(t.run("delete_file",{{"path","a.tex"}})["error"]=="deletion_disabled");t.deletable=true;
    assert(t.run("delete_file",{{"path","a.tex"},{"revision","stale"}})["error"]=="revision_mismatch_read_again");
    t.buffer=[](QString){return QJsonObject{{"open",true}};};
    assert(t.run("delete_file",{{"path","a.tex"}})["error"]=="close_document_before_deleting");t.buffer={};
    auto latest=t.read("a.tex");auto deleted=t.run("delete_file",{{"path","a.tex"},{"revision",latest["revision"]}});
    assert(deleted["recoverable"].toBool() && !QFileInfo::exists(dir.path()+"/a.tex"));
    QFile recover(dir.path()+"/"+deleted["movedTo"].toString());assert(recover.open(QIODevice::ReadOnly));assert(QString::fromUtf8(recover.readAll())==latest["text"].toString());
    assert(t.resolve(deleted["movedTo"].toString()).isEmpty());
    assert(HarmonyAiTools::schema(false,false).size()==3 && HarmonyAiTools::schema(true,true).size()==6);
    assert(harmonyChineseKnown(QStringLiteral("这是一个中文测试数学概率空间")));
    assert(!harmonyChineseKnown(QStringLiteral("鿿鿿")));
    std::cout<<"PASS: project path boundaries, symlink rejection, read-only, create-no-overwrite, revision conflicts, UTF-8 edits, editor buffer routing, bounded log path, deletion opt-in/open-file/revision guards, recoverable trash, capability schema, Chinese word coverage\n";
}
