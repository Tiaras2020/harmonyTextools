#ifndef Header_DblClick_MenuBar
#define Header_DblClick_MenuBar

#include <QMenuBar>

class DblClickMenuBar : public QMenuBar
{
	Q_OBJECT

public:
    explicit DblClickMenuBar(QWidget *parent = nullptr);

signals:
	void doubleClicked(); // emitted when double clicking empty part of menu bar
	
public slots:

protected:
	virtual void mouseDoubleClickEvent(QMouseEvent *);
#ifdef Q_OS_OHOS
    void resizeEvent(QResizeEvent *event) override;
    void actionEvent(QActionEvent *event) override;
    void spreadMenus();
    int menuPadding = -1;
#endif
};

#endif // DBLCLICKMENUBAR_H
