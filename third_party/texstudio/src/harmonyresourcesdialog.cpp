#include "harmonydialoglayout.h"
#include <QMenu>
#include <QToolButton>
#include "harmonyresources.h"
#include "harmonyRelease.h"
#include "filedialog.h"
#include <QDialog>
#include <QDialogButtonBox>
#include <QFile>
#include <QFutureWatcher>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QListWidget>
#include <QMessageBox>
#include <QProgressDialog>
#include <QPushButton>
#include <QVBoxLayout>
#include <QtConcurrent>
#include <functional>

void HarmonyResources::showDialog(QWidget *parent)
{
    const QString root = storageRoot();
    const QString current = sessionResource();
    if (root.isEmpty()) { QMessageBox::warning(parent, QStringLiteral("离线资源"), QStringLiteral("无法取得应用持久化目录。")); return; }
    QDialog dialog(parent);
    dialog.setWindowTitle(QStringLiteral("离线资源管理"));
    
    QVBoxLayout layout(&dialog);
    QLabel description(QStringLiteral("导入后资源已解压保存，原 ZIP 可移走或删除；可导出 ZIP 备份。\n启用和回退在完全退出并重新打开应用后生效；恢复内置资源不会删除已导入的资源。"));
    description.setWordWrap(true); description.setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum); layout.addWidget(&description);
    QLabel session(current.isEmpty() ? QStringLiteral("当前会话：内置资源") : QStringLiteral("当前会话：已启用扩展资源"));
    layout.addWidget(&session);
    QListWidget list; layout.addWidget(&list);
    auto refresh = [&]() {
        const QString previous = list.currentItem() ? list.currentItem()->data(Qt::UserRole).toString() : QString();
        const QString selected = selectedResource(root);
        list.clear();
        for (const QString &id : installed(root)) {
            QFile f(root + "/resources/" + id + "/manifest.json"); f.open(QIODevice::ReadOnly);
            const auto m = QJsonDocument::fromJson(f.readAll()).object();
            const QString title = m.value("title").toString(m.value("id").toString());
            QString status;
            if (id == current) status += QStringLiteral("  [当前使用]");
            if (id == selected) status += QStringLiteral("  [下次启动使用]");
            auto *item = new QListWidgetItem(title + "  " + m.value("version").toString() + QStringLiteral("  · %1 个文件").arg(m.value("files").toObject().size()) + status, &list);
            item->setData(Qt::UserRole, id);
            if (id == previous) list.setCurrentItem(item);
        }
        if (!list.currentItem() && list.count()) list.setCurrentRow(0);
    };
    refresh();
    QDialogButtonBox buttons;
    auto *importButton = buttons.addButton(QStringLiteral("导入资源包…"), QDialogButtonBox::ActionRole);
    auto *activateButton = buttons.addButton(QStringLiteral("启用所选版本"), QDialogButtonBox::ActionRole);
    auto *verifyButton = buttons.addButton(QStringLiteral("校验与刷新索引"), QDialogButtonBox::ActionRole);
    auto *resetButton = buttons.addButton(QStringLiteral("恢复内置资源"), QDialogButtonBox::ActionRole);
    buttons.hide();
    QDialogButtonBox management;
    auto *userButton = management.addButton(QStringLiteral("用户资源…"), QDialogButtonBox::ActionRole);
    QObject::connect(userButton, &QPushButton::clicked, &dialog, [&]() { showUserDialog(&dialog); });
    auto *exportButton = buttons.addButton(QStringLiteral("导出所选资源…"), QDialogButtonBox::ActionRole);
    auto *deleteButton = buttons.addButton(QStringLiteral("删除所选资源…"), QDialogButtonBox::ActionRole);
    auto *closeButton = management.addButton(QDialogButtonBox::Close);
    closeButton->setText(QStringLiteral("关闭"));
    QMenu operations(&dialog);
    for (auto *button : {importButton, activateButton, verifyButton, resetButton, exportButton, deleteButton}) {
        auto *action = operations.addAction(button->text());
        QObject::connect(action, &QAction::triggered, button, &QPushButton::click);
    }
    QToolButton menuButton; menuButton.setText(QStringLiteral("资源操作"));
    menuButton.setMenu(&operations); menuButton.setPopupMode(QToolButton::InstantPopup);
    layout.addWidget(&menuButton, 0, Qt::AlignLeft);
    list.setContextMenuPolicy(Qt::CustomContextMenu);
    QObject::connect(&list, &QListWidget::customContextMenuRequested, &dialog,
        [&](const QPoint &point) { operations.exec(list.viewport()->mapToGlobal(point)); });
    layout.addWidget(&management);
    QObject::connect(closeButton, &QPushButton::clicked, &dialog, &QDialog::accept);
    auto run = [&](const std::function<Result()> &operation, const QString &success) {
        QProgressDialog progress(QStringLiteral("正在校验和准备资源，请稍候…"), QString(), 0, 0, &dialog);
        progress.setCancelButton(nullptr); progress.setWindowModality(Qt::WindowModal);
        QFutureWatcher<Result> watcher;
        QObject::connect(&watcher, &QFutureWatcher<Result>::finished, &progress, &QProgressDialog::accept);
        watcher.setFuture(QtConcurrent::run(operation));
        progress.exec(); watcher.waitForFinished();
        const Result result = watcher.result();
        if (!result.error.isEmpty()) QMessageBox::warning(&dialog, QStringLiteral("资源操作未完成"), result.error);
        else QMessageBox::information(&dialog, QStringLiteral("离线资源"), success);
        refresh();
    };
    QObject::connect(importButton, &QPushButton::clicked, &dialog, [&]() {
        const QString path = FileDialog::getOpenFileName(&dialog, QStringLiteral("选择离线资源包"), QString(), QStringLiteral("TeX 资源包 (*.zip)"));
        if (path.isEmpty()) return;
        run([=]() {
            Result result = importArchive(path, root, HARMONY_TEX_COMPATIBILITY);
            if (result.error.isEmpty()) result.error = activate(root, result.id, HARMONY_TEX_COMPATIBILITY);
            return result;
        }, QStringLiteral("资源已解压保存，原 ZIP 无需保留。请完全退出并重新打开 TeXstudio 后使用。"));
    });
    QObject::connect(activateButton, &QPushButton::clicked, &dialog, [&]() {
        if (!list.currentItem()) return;
        const QString id = list.currentItem()->data(Qt::UserRole).toString();
        run([=]() { return Result{id, activate(root, id, HARMONY_TEX_COMPATIBILITY)}; }, QStringLiteral("已安排启用。请完全退出并重新打开应用。"));
    });
    QObject::connect(verifyButton, &QPushButton::clicked, &dialog, [&]() {
        if (!list.currentItem()) return;
        const QString id = list.currentItem()->data(Qt::UserRole).toString();
        run([=]() { return Result{id, verify(root, id, HARMONY_TEX_COMPATIBILITY)}; }, QStringLiteral("文件校验通过，宏包索引已刷新。"));
    });
    QObject::connect(resetButton, &QPushButton::clicked, &dialog, [&]() {
        run([=]() { return Result{QString(), activate(root, QString(), HARMONY_TEX_COMPATIBILITY)}; }, QStringLiteral("已安排恢复内置资源，已导入的资源仍保留。请完全退出并重新打开应用。"));
    });
    QObject::connect(exportButton, &QPushButton::clicked, &dialog, [&]() {
        if (!list.currentItem()) return;
        const QString id = list.currentItem()->data(Qt::UserRole).toString();
        const QString path = FileDialog::getSaveFileName(&dialog, QStringLiteral("导出离线资源包"), id + ".zip", QStringLiteral("TeX 资源包 (*.zip)"));
        if (path.isEmpty()) return;
        run([=]() { return Result{id, exportArchive(root, id, path, HARMONY_TEX_COMPATIBILITY)}; }, QStringLiteral("资源包已导出，可用于备份或在兼容版本中重新导入。"));
    });
    QObject::connect(deleteButton, &QPushButton::clicked, &dialog, [&]() {
        if (!list.currentItem()) return;
        const QString id = list.currentItem()->data(Qt::UserRole).toString();
        if (id == current || id == selectedResource(root)) {
            QMessageBox::information(&dialog, QStringLiteral("资源仍在使用"), QStringLiteral("请先恢复内置资源或启用其他版本，再完全退出并重新打开应用后删除。"));
            return;
        }
        if (QMessageBox::question(&dialog, QStringLiteral("删除资源"), QStringLiteral("删除所选资源及其缓存？如需备份，请先导出。\n") + list.currentItem()->text(), QMessageBox::Yes | QMessageBox::No, QMessageBox::No) != QMessageBox::Yes) return;
        run([=]() { return Result{id, removeResource(root, id, current)}; }, QStringLiteral("所选资源及其缓存已删除。"));
    });
    fitHarmonyDialog(&dialog, 65, 28); dialog.exec();
}
