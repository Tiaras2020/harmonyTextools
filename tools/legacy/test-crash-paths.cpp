#include "harmonyproject.h"
#include <QCoreApplication>
#include <QTemporaryDir>
#include <cassert>
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);QTemporaryDir tmp,outside;
    const QString root=QFileInfo(tmp.path()).canonicalFilePath();QString error;
    auto resolve=[&](const QString &path){return HarmonyProject::resolve(root,path,false,&error);};
    assert(resolve("missing.tex").isEmpty()&&error=="file_missing");
    for(const QString &path:{"../outside.tex","/etc/passwd","missing/../outside.tex",".hidden.tex","a//b.tex","a\\b.tex"})
        assert(resolve(path).isEmpty()&&error=="invalid_text_path");
    assert(QFile::link(outside.path()+"/missing.tex",root+"/link.tex"));
    assert(resolve("link.tex").isEmpty()&&error=="invalid_text_path");
    assert(QFile::link(outside.path(),root+"/directory"));
    assert(resolve("directory/missing.tex").isEmpty()&&error=="invalid_text_path");
    QFile f(root+"/main.tex");assert(f.open(QIODevice::WriteOnly));f.write("original");f.close();
    assert(!resolve("main.tex").isEmpty()&&error.isEmpty());
    assert(resolve("main.tex/child.tex").isEmpty()&&error=="invalid_text_path");
    f.remove();assert(resolve("main.tex").isEmpty()&&error=="file_missing");
    qInfo()<<"PASS: missing versus illegal paths; traversal, dangling/parent symlinks, non-directory parent, delete and restore boundary";
}
