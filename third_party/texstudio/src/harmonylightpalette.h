#ifndef HARMONY_LIGHT_PALETTE_H
#define HARMONY_LIGHT_PALETTE_H
#include <QtWidgets>
inline void harmonyRestoreLightPalette() {
#ifdef Q_OS_OHOS
    QVariant saved=qApp->property("harmonyLightPalette");if(!saved.isValid())return;
    const QPalette palette=qvariant_cast<QPalette>(saved);
    QApplication::setPalette(palette);
    // QPA can replace per-class palettes after QApplication::paletteChanged.
    // Apply after the theme event has finished, including inactive windows.
    for(auto *widget:QApplication::allWidgets()) {widget->setPalette(palette);widget->update();}
#endif
}
class HarmonyLightPaletteGuard : public QObject {
    bool queued=false, restoring=false;
protected:
    bool eventFilter(QObject *,QEvent *event) override {
        if(!restoring && !queued && (event->type()==QEvent::Show || event->type()==QEvent::PaletteChange || event->type()==QEvent::ApplicationPaletteChange || event->type()==QEvent::ThemeChange || event->type()==QEvent::ApplicationActivate)) {
            queued=true;QTimer::singleShot(0,this,[this]{queued=false;restoring=true;harmonyRestoreLightPalette();restoring=false;});
        }
        return false;
    }
public:
    explicit HarmonyLightPaletteGuard(QObject *parent):QObject(parent){qApp->installEventFilter(this);}
};
#endif
