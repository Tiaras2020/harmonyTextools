#ifndef HARMONY_DIALOG_LAYOUT_H
#define HARMONY_DIALOG_LAYOUT_H
#include <QApplication>
#include <QDialog>
#include <QScreen>
#include <QWindow>
#include <QLayout>

// Use the current screen and font, rather than physical-pixel assumptions.
inline void fitHarmonyDialog(QDialog *dialog, int columns = 64, int rows = 30)
{
    dialog->setFont(QApplication::font());
    dialog->ensurePolished();
    const int em = dialog->fontMetrics().height();
    QScreen *screen = dialog->parentWidget() && dialog->parentWidget()->windowHandle()
        ? dialog->parentWidget()->windowHandle()->screen() : QGuiApplication::primaryScreen();
    const QSize available = screen ? screen->availableGeometry().size() : QSize(1280, 900);
    const QSize preferred(qMin(columns * em, available.width() * 9 / 10),
                          qMin(rows * em, available.height() * 8 / 10));
    dialog->resize(preferred.expandedTo(dialog->minimumSizeHint()));
}
#endif
