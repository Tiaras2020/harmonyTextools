#include "dblclickmenubar.h"

#include "QMouseEvent"
#include <QAction>
#include <QTimer>

DblClickMenuBar::DblClickMenuBar(QWidget *parent) :
	QMenuBar(parent)
{
}

#ifdef Q_OS_OHOS
void DblClickMenuBar::spreadMenus()
{
    int textWidth = 0, count = 0;
    for (QAction *action : actions()) {
        if (!action->isVisible() || action->isSeparator()) continue;
        QString label = action->text();
        label.remove('&');
        textWidth += fontMetrics().horizontalAdvance(label);
        ++count;
    }
    if (!count) return;
    // Leave room for the frame; narrow windows retain QMenuBar's overflow handling.
    const int padding = qMax(6, (width() - textWidth - count * 12 - 24) / (2 * count));
    if (padding == menuPadding) return;
    menuPadding = padding;
    setStyleSheet(QStringLiteral(
        "QMenuBar { background: #ffffff; color: #202124; border-bottom: 1px solid #dedede; }"
        "QMenuBar::item { padding: 2px %1px; background: transparent; }"
        "QMenuBar::item:selected { background: #e8f1fb; color: #202124; }"
        "QMenuBar::item:pressed { background: #d9e9fa; }").arg(padding));
}

void DblClickMenuBar::resizeEvent(QResizeEvent *event)
{
    QMenuBar::resizeEvent(event);
    QTimer::singleShot(0, this, [this] { spreadMenus(); });
}

void DblClickMenuBar::actionEvent(QActionEvent *event)
{
    QMenuBar::actionEvent(event);
    QTimer::singleShot(0, this, [this] { spreadMenus(); });
}
#endif

void DblClickMenuBar::mouseDoubleClickEvent(QMouseEvent *event)
{
	if (!actionAt(event->pos())) {
		emit doubleClicked();
		return;
	}
	QMenuBar::mouseDoubleClickEvent(event);
}
