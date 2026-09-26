#ifndef HARMONY_FLOATING_PANEL_H
#define HARMONY_FLOATING_PANEL_H
#include <QtWidgets>
class HarmonyFloatingPanel : public QDialog {
    QPointer<QWidget> panel, original;
    int index=-1;
    bool restored=false;
    void restore() {
        if(restored || !panel || !original)return;restored=true;
        panel->setParent(original);
        if(auto *stack=qobject_cast<QStackedWidget*>(original.data())){stack->insertWidget(qMax(0,index),panel);stack->setCurrentWidget(panel);}
        else if(auto *dock=qobject_cast<QDockWidget*>(original.data()))dock->setWidget(panel);
        else if(original->layout())original->layout()->addWidget(panel);
        panel->show();original->show();
    }
protected:
    void closeEvent(QCloseEvent *event) override {restore();QDialog::closeEvent(event);}
    void reject() override {restore();QDialog::reject();deleteLater();}
public:
    HarmonyFloatingPanel(QWidget *content,QString title,bool onTop):QDialog(content->window()),panel(content),original(content->parentWidget()) {
        setAttribute(Qt::WA_DeleteOnClose);setWindowTitle(title);
        if(onTop)setWindowFlag(Qt::WindowStaysOnTopHint,true);
        if(auto *stack=qobject_cast<QStackedWidget*>(original.data())){index=stack->indexOf(content);stack->removeWidget(content);}
        auto *layout=new QVBoxLayout(this);layout->setContentsMargins(4,4,4,4);layout->addWidget(content);content->show();
        QRect area=parentWidget()->geometry();resize(onTop?QSize(qMax(600,area.width()/3),area.height()*4/5):QSize(area.width()*9/10,area.height()*4/5));
        move(area.center()-QPoint(width()/2,height()/2));show();
    }
    ~HarmonyFloatingPanel() override {restore();}
};
#endif
