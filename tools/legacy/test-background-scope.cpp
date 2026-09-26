#include "harmonyproject.h"
#include <QCoreApplication>
#include <cassert>
int main(int argc,char **argv) {
    QCoreApplication app(argc,argv);
    using HarmonyProject::documentPath;
    assert(documentPath("/project","/project/new/missing.tex")=="new/missing.tex");
    assert(documentPath("/project","/project/.hidden.tex")==".hidden.tex");
    assert(documentPath("/project","/project/../outside.tex").isEmpty());
    assert(documentPath("/project","/project-other/main.tex").isEmpty());
    assert(documentPath("/project","").isEmpty());
    assert(documentPath("/project","untitled").isEmpty());
    HarmonyProject::Job job;job.state="failed";
    job.blockers.append(QJsonObject{{"path","missing.tex"},{"conflict",true},{"exists",false}});
    assert(job.status()["blockers"].toArray()==job.blockers);
    qInfo()<<"PASS: project boundary, missing/hidden buffer visibility, untitled exclusion, queued blocker reporting";
}
