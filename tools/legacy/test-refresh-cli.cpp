#include "harmonyproject.h"
#include "qreliablefilewatch.h"
#include <QCoreApplication>
#include <QTemporaryDir>
#include <QSaveFile>
#include <QThread>
#include <cassert>
class Recipient:public QObject {
    Q_OBJECT
public:int changes=0;
public slots:void fileChanged(const QString &){++changes;}
};
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);QTemporaryDir tmp;
    const QString path=tmp.path()+"/main.tex";
    auto write=[&](const char *text){QFile f(path);assert(f.open(QIODevice::WriteOnly));f.write(text);};
    write("aaaa");QReliableFileWatch watcher;Recipient recipient;watcher.addWatch(path,&recipient);
    write("bbbb");watcher.refreshNow(path);assert(recipient.changes==1);
    watcher.refreshNow(path);assert(recipient.changes==1);
    {QSaveFile f(path);assert(f.open(QIODevice::WriteOnly));f.write("cccc");assert(f.commit());}
    watcher.refreshNow(path);assert(recipient.changes==2);
    write("dddd");
    QElapsedTimer elapsed;elapsed.start();while(elapsed.elapsed()<1600){app.processEvents();QThread::msleep(20);}
    assert(recipient.changes==3);
    QFile::remove(path);watcher.refreshNow(path);assert(recipient.changes==4);
    write("eeee");watcher.refreshNow(path);assert(recipient.changes==5);
    watcher.removeWatch(&recipient);
    HarmonyProject::Job j;j.id="test";j.master="main.tex";
    assert(j.status().value("buildSucceeded").isNull());
    j.state="failed";j.exitCode=12;assert(j.status().value("ok").toBool());assert(!j.status().value("buildSucceeded").toBool());
    j.log="Nothing to do\nErrors from previous invocation\n";
    auto d=HarmonyProject::diagnostics(j,tmp.path());assert(d["items"].toArray()[0].toObject()["code"]=="cached_previous_failure");
    j.log="Run number 1 of rule 'pdflatex'\nLaTeX Warning: Label(s) may have changed.\nRun number 2 of rule 'pdflatex'\n";
    j.finalLogAvailable=true;j.finalLog="Final converged log\n";j.state="succeeded";
    assert(HarmonyProject::diagnostics(j,tmp.path())["items"].toArray().isEmpty());
    j.finalLog="LaTeX Warning: Reference `missing' undefined.\n";
    assert(HarmonyProject::diagnostics(j,tmp.path())["items"].toArray().size()==1);
    qInfo()<<"PASS: rapid equal-size writes, atomic replacement, polling, deletion/recreation, terminal result, cached failure and final-pass diagnostics";
}
#include "test-refresh-cli.moc"
