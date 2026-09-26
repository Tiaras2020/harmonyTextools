#include "tested-workbench.h"
#include "harmonyfloatingpanel.h"
#include <cassert>
#include <iostream>
int main(int argc,char **argv){
 QApplication app(argc,argv);QTemporaryDir dir;ConfigManager config;config.configBaseDir=dir.path();
 HarmonyAiWorkbench w(&config);w.resize(600,600);w.show();app.processEvents();
 w.input->setPlainText("no project");w.submit();assert(w.messages.isEmpty());
 w.setRoot(dir.path());w.input->setPlainText("shortcut test");
 QKeyEvent override(QEvent::ShortcutOverride,Qt::Key_Return,Qt::ControlModifier);QApplication::sendEvent(w.input,&override);assert(override.isAccepted());
 QKeyEvent key(QEvent::KeyPress,Qt::Key_Return,Qt::ControlModifier);QApplication::sendEvent(w.input,&key);assert(w.messages.size()==1 && w.input->toPlainText().isEmpty());
 for(int i=0;i<20;++i)w.messages.append(QJsonObject{{"role","user"},{"content",QString("Message %1\n").arg(i)+QString(300,'x')}});
 w.render();app.processEvents();auto *scroll=w.chat->verticalScrollBar();scroll->setValue(scroll->maximum()/2);int old=scroll->value();w.streamText="stream fragment";w.render();assert(scroll->value()==old);
 w.toBottom();w.streamText+=QString(500,'y');w.render();assert(scroll->value()==scroll->maximum());
 w.navigateMessage(-1);assert(w.messageIndex==w.messages.size()-1);w.navigateMessage(-1);assert(w.messageIndex==w.messages.size()-2);
 w.edit->setChecked(true);w.deletion->setChecked(true);w.shell->setChecked(true);w.setRoot(dir.path());assert(!w.tools.editable && !w.tools.deletable && !w.shell->isChecked());
 assert(w.extendedTool("shell_start",{{"command","echo test"}})["error"]=="shell_disabled");
 w.shell->setChecked(true);auto job=w.extendedTool("shell_start",{{"command","printf shell_ok"}});assert(job.contains("jobId"));
 QElapsedTimer timer;timer.start();while(w.process->state()!=QProcess::NotRunning && timer.elapsed()<5000){app.processEvents();QThread::msleep(10);}app.processEvents();
 auto result=w.extendedTool("shell_status",{{"jobId",job["jobId"]}});assert(result["exitCode"]==0 && result["output"]=="shell_ok");
 QMainWindow main;auto *stack=new QStackedWidget;main.setCentralWidget(stack);auto *panel=new QWidget;stack->addWidget(panel);main.resize(1000,700);main.show();
 QPointer<HarmonyFloatingPanel> floating=new HarmonyFloatingPanel(panel,"test",true);app.processEvents();assert(panel->isVisible());assert(floating->windowFlags().testFlag(Qt::WindowStaysOnTopHint));floating->close();app.processEvents();assert(panel->parentWidget()==stack && stack->currentWidget()==panel);
 std::cout<<"PASS: project required, Ctrl+Enter, scroll preservation and follow tail, message navigation, permission reset, shell opt-in/output, floating restore\n";
}
