#ifndef HARMONY_CLIPBOARD_H
#define HARMONY_CLIPBOARD_H
#include <QtWidgets>
#include <functional>
#include "harmonylightpalette.h"
#ifdef Q_OS_OHOS
#include <QtOhosExtras/qohosappcontext.h>
#endif
// Read only on an explicit Paste action. Never log or persist clipboard contents.
inline void harmonyPaste(QWidget *owner, std::function<void(const QString &)> insert)
{
    QPointer<QWidget> safeOwner(owner);
    const QPalette applicationPalette=QApplication::palette();
    QList<QPair<QPointer<QWidget>,QPalette>> palettes;
    palettes.append(qMakePair(QPointer<QWidget>(owner),owner->palette()));
    for(auto *w:QApplication::allWidgets())palettes.append(qMakePair(QPointer<QWidget>(w),w->palette()));
    auto restore=[safeOwner,applicationPalette,palettes]{
        if(!safeOwner)return;QApplication::setPalette(applicationPalette);
        for(const auto &entry:palettes)if(entry.first){entry.first->setPalette(entry.second);entry.first->update();}
        harmonyRestoreLightPalette();
    };
    auto stabilize=[safeOwner,restore]{if(!safeOwner)return;restore();for(int delay:{0,250,1000})QTimer::singleShot(delay,safeOwner,restore);};
    auto read = [owner, safeOwner, insert, stabilize] {
        if(!safeOwner)return;
        const QString text = QApplication::clipboard()->text();
        if (text.isEmpty()) QMessageBox::information(owner, QStringLiteral("粘贴"), QStringLiteral("没有读到剪贴板文字。请重新复制文字；若曾拒绝访问，请在系统应用权限中允许读取剪贴板。"));
        else insert(text);
        stabilize();
    };
#ifdef Q_OS_OHOS
    using namespace QtOhosExtras;
    auto *context = QOhosAppContext::instance();
    auto permission = AppPermissions::Permission::ReadPasteboard;
    if (context && !context->isPermissionGranted(permission)) {
        auto *request = new QObject(owner);
        QObject::connect(context, &QOhosAppContext::permissionRequestResponseReceived, request,
            [=](AppPermissions::Permission p, bool granted) {
                if (p != permission) return;
                request->deleteLater();
                stabilize();
                if (granted) QTimer::singleShot(200,owner,read);
                else QMessageBox::information(owner, QStringLiteral("粘贴"), QStringLiteral("剪贴板权限未获准。请在系统设置中允许 TeXstudio 读取剪贴板，再点击粘贴。"));
            });
        context->requestPermissionFromUserIfNeeded(permission);
        return;
    }
#endif
    read();
}
#endif
