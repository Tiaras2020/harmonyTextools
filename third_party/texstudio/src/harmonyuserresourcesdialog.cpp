#include <QStyle>
#include <QMap>
#include <algorithm>
#include "harmonydialoglayout.h"
#include <QTreeWidget>
#include <QTreeWidgetItemIterator>
#include <QDirIterator>
#include <QMenu>
#include <QToolButton>
#include <QSet>
#include <QHeaderView>
#include "harmonyresources.h"
#include "filedialog.h"
#include "utilsSystem.h"
#include <QCheckBox>
#include <QDialog>
#include <QDialogButtonBox>
#include <QFile>
#include <QFileInfo>
#include <QFutureWatcher>
#include <QInputDialog>
#include <QLabel>
#include <QListWidget>
#include <QMessageBox>
#include <QPlainTextEdit>
#include <QProgressDialog>
#include <QPushButton>
#include <QVBoxLayout>
#include <QtConcurrent>
#include <functional>

namespace {
QString resourcePathInput(QWidget *parent, const QString &title, const QString &label,
                          QLineEdit::EchoMode echo, const QString &initial)
{
    QInputDialog input(parent);
    input.setWindowTitle(title); input.setLabelText(label);
    input.setTextEchoMode(echo); input.setTextValue(initial);
    input.setOkButtonText(QStringLiteral("确定")); input.setCancelButtonText(QStringLiteral("取消"));
    fitHarmonyDialog(&input, 48, 8);
    return input.exec() == QDialog::Accepted ? input.textValue() : QString();
}
}

void HarmonyResources::showUserDialog(QWidget *parent)
{
    const QString root = storageRoot();
#ifdef Q_OS_OHOS
    const QString base = ohosBundledTexRoot();
#else
    const QString base = qEnvironmentVariable("TEXMFROOT");
#endif
    QDialog dialog(parent);
    dialog.setWindowTitle(QStringLiteral("可编辑用户资源"));
    
    QVBoxLayout layout(&dialog);
    QLabel description(QStringLiteral("保存和启停从下一次编译生效。项目文件优先，其次是用户资源。\n支持 Lua 宏包源码；请选择可信文件，保留宏包目录结构。\n内核和基础组件禁止替换。HiShell 需导出、解压并设置搜索路径。"));
    description.setWordWrap(true); description.setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum); layout.addWidget(&description);
    QCheckBox enabled(QStringLiteral("启用用户资源"));
    enabled.setChecked(userEnabled(root)); layout.addWidget(&enabled);
    QTreeWidget list; list.setHeaderLabels({QStringLiteral("文件 / 文件夹")});
    list.setSelectionMode(QAbstractItemView::ExtendedSelection);
    list.setMinimumHeight(180); list.setUniformRowHeights(true);
    list.header()->setSectionResizeMode(QHeaderView::ResizeToContents);
    layout.addWidget(&list, 1);
    auto selectedPath = [&]() { return list.currentItem() ? list.currentItem()->data(0, Qt::UserRole).toString() : QString(); };
    auto selectedDirectory = [&]() {
        if (!list.currentItem()) return QStringLiteral("tex/latex/user");
        return list.currentItem()->data(0, Qt::UserRole + 1).toBool()
            ? selectedPath() : QFileInfo(selectedPath()).path();
    };
    QPlainTextEdit details; details.setReadOnly(true); details.setMinimumHeight(100); details.setMaximumHeight(120);
    layout.addWidget(&details);
    auto refresh = [&]() {
        const QString previous = selectedPath();
        QSet<QString> expanded;
        for (QTreeWidgetItemIterator it(&list); *it; ++it)
            if ((*it)->isExpanded()) expanded.insert((*it)->data(0, Qt::UserRole).toString());
        list.clear();
        QMap<QString, QTreeWidgetItem *> folders;
        auto addPath = [&](const QString &path, bool directory) {
            QString cumulative;
            QTreeWidgetItem *parentItem = nullptr;
            const auto parts = path.split('/');
            for (int i = 0; i < parts.size(); ++i) {
                cumulative += (cumulative.isEmpty() ? "" : "/") + parts[i];
                const bool isDirectory = i < parts.size() - 1 || directory;
                auto *item = folders.value(cumulative, nullptr);
                if (!item) {
                    item = parentItem ? new QTreeWidgetItem(parentItem) : new QTreeWidgetItem(&list);
                    item->setText(0, parts[i]); item->setToolTip(0, cumulative);
                    item->setData(0, Qt::UserRole, cumulative);
                    item->setData(0, Qt::UserRole + 1, isDirectory);
                    item->setIcon(0, dialog.style()->standardIcon(isDirectory ? QStyle::SP_DirIcon : QStyle::SP_FileIcon));
                    folders.insert(cumulative, item);
                    item->setExpanded(expanded.contains(cumulative) || i < 2);
                }
                if (cumulative == previous) list.setCurrentItem(item);
                parentItem = item;
            }
        };
        QDirIterator dirs(root + "/texmf-home", QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);
        while (dirs.hasNext()) {
            dirs.next();
            if (!dirs.fileInfo().isSymLink()) addPath(QDir(root + "/texmf-home").relativeFilePath(dirs.filePath()), true);
        }
        const auto files = userFiles(root);
        for (const QString &file : files) addPath(file, false);
        details.setPlainText(QStringLiteral("%1 个资源文件。Shift 连选，Ctrl 多选；文件夹操作会包含其中的文件。ZIP 导入保留包内目录，不覆盖已有文件。").arg(files.size()));
    };
    QObject::connect(&list, &QTreeWidget::currentItemChanged, &dialog, [&](QTreeWidgetItem *item, QTreeWidgetItem *) {
        if (!item) return;
        const QString file = item->data(0, Qt::UserRole).toString();
        if (item->data(0, Qt::UserRole + 1).toBool()) { details.setPlainText(file + QStringLiteral("\n文件夹；可以新建子文件夹或选择其中的文件。")); return; }
        const auto conflicts = userConflicts(root, file, base, sessionResource());
        details.setPlainText(file + "\n" + (conflicts.isEmpty() ? QStringLiteral("未发现其他资源层的同名文件。") : QStringLiteral("存在同名文件；启用时用户版本优先。\n") + conflicts.join('\n')));
    });
    auto report = [&](const QString &error) {
        if (!error.isEmpty()) QMessageBox::warning(&dialog, QStringLiteral("用户资源操作未完成"), error);
        refresh();
    };
    auto run = [&](const std::function<QString()> &operation) {
        QProgressDialog progress(QStringLiteral("正在处理用户资源…"), QString(), 0, 0, &dialog);
        progress.setCancelButton(nullptr); progress.setWindowModality(Qt::WindowModal);
        QFutureWatcher<QString> watcher;
        QObject::connect(&watcher, &QFutureWatcher<QString>::finished, &progress, &QProgressDialog::accept);
        watcher.setFuture(QtConcurrent::run(operation)); progress.exec(); watcher.waitForFinished();
        report(watcher.result());
    };
    QObject::connect(&enabled, &QCheckBox::toggled, &dialog, [&](bool value) {
        const QString error = setUserEnabled(root, value);
        if (!error.isEmpty()) { enabled.blockSignals(true); enabled.setChecked(userEnabled(root)); enabled.blockSignals(false); report(error); }
    });
    auto edit = [&](const QString &relative, bool existing) {
        const QString error = userFileError(root, relative, base);
        if (!error.isEmpty()) { report(error); return; }
        const QString suffix = QFileInfo(relative).suffix().toLower();
        if (QStringList{"otf", "ttf", "ttc", "pdf"}.contains(suffix)) { report(QStringLiteral("此文件是二进制资源，可通过导入同名文件替换。")); return; }
        QByteArray data;
        if (existing) {
            QFile f(root + "/texmf-home/" + relative);
            if (!f.open(QIODevice::ReadOnly) || f.size() > 2*1024*1024) { report(QStringLiteral("无法打开文本文件，或文件超过 2 MiB 编辑上限。")); return; }
            data = f.readAll();
            if (QString::fromUtf8(data).toUtf8() != data) { report(QStringLiteral("内置编辑器只编辑 UTF-8 文本，请转换编码后重新导入。")); return; }
        }
        QDialog editor(&dialog); editor.setWindowTitle(relative); editor.resize(850, 600);
        QVBoxLayout editorLayout(&editor);
        QPlainTextEdit text; text.setMinimumSize(720, 360); text.setPlainText(QString::fromUtf8(data)); editorLayout.addWidget(&text);
        QDialogButtonBox controls(QDialogButtonBox::Save | QDialogButtonBox::Cancel);
        controls.button(QDialogButtonBox::Save)->setText(QStringLiteral("保存"));
        controls.button(QDialogButtonBox::Cancel)->setText(QStringLiteral("取消"));
        editorLayout.addWidget(&controls);
        QObject::connect(&controls, &QDialogButtonBox::rejected, &editor, &QDialog::reject);
        QObject::connect(&controls, &QDialogButtonBox::accepted, &editor, [&]() {
            const QString error = saveUserFile(root, relative, text.toPlainText().toUtf8(), base);
            if (error.isEmpty()) editor.accept();
            else QMessageBox::warning(&editor, QStringLiteral("保存未完成"), error);
        });
        editor.exec(); refresh();
    };
    QDialogButtonBox actions;
    auto *add = actions.addButton(QStringLiteral("新建文本…"), QDialogButtonBox::ActionRole);
    auto *import = actions.addButton(QStringLiteral("添加文件…"), QDialogButtonBox::ActionRole);
    auto *modify = actions.addButton(QStringLiteral("编辑…"), QDialogButtonBox::ActionRole);
    auto *remove = actions.addButton(QStringLiteral("删除…"), QDialogButtonBox::ActionRole);
    actions.hide();
    QDialogButtonBox backups;
    auto *backup = backups.addButton(QStringLiteral("导出备份…"), QDialogButtonBox::ActionRole);
    auto *restore = backups.addButton(QStringLiteral("从 ZIP 恢复…"), QDialogButtonBox::ActionRole);
    auto *index = backups.addButton(QStringLiteral("刷新索引和字体缓存"), QDialogButtonBox::ActionRole);
    auto *close = backups.addButton(QDialogButtonBox::Close); close->setText(QStringLiteral("关闭"));
    backups.hide();
    auto *folder = actions.addButton(QStringLiteral("新建文件夹…"), QDialogButtonBox::ActionRole);
    auto *importZip = actions.addButton(QStringLiteral("导入 ZIP（保留现有资源）…"), QDialogButtonBox::ActionRole);
    QMenu operations(&dialog);
    for (auto *button : {importZip, import, add, folder, modify, remove, backup, restore, index}) {
        auto *action = operations.addAction(button->text());
        QObject::connect(action, &QAction::triggered, button, &QPushButton::click);
    }
    QToolButton menuButton; menuButton.setText(QStringLiteral("资源操作"));
    menuButton.setMenu(&operations); menuButton.setPopupMode(QToolButton::InstantPopup);
    QHBoxLayout footer; footer.addWidget(&menuButton); footer.addStretch();
    QPushButton visibleClose(QStringLiteral("关闭")); footer.addWidget(&visibleClose); layout.addLayout(&footer);
    QObject::connect(&visibleClose, &QPushButton::clicked, &dialog, &QDialog::accept);
    list.setContextMenuPolicy(Qt::CustomContextMenu);
    QObject::connect(&list, &QTreeWidget::customContextMenuRequested, &dialog,
        [&](const QPoint &point) { operations.exec(list.viewport()->mapToGlobal(point)); });
    QObject::connect(folder, &QPushButton::clicked, &dialog, [&]() {
        const QString name = resourcePathInput(&dialog, QStringLiteral("新建文件夹"), QStringLiteral("相对路径："), QLineEdit::Normal, selectedDirectory() + "/my-resources");
        if (!name.isEmpty()) report(createUserFolder(root, name, base));
    });
    QObject::connect(importZip, &QPushButton::clicked, &dialog, [&]() {
        const QString path = FileDialog::getOpenFileName(&dialog, QStringLiteral("导入用户资源包（保留现有资源）"), QString(), QStringLiteral("TeX 资源包 (*.zip)"));
        if (!path.isEmpty()) run([=]() { return restoreUserArchive(root, path, base, true); });
    });
    QObject::connect(close, &QPushButton::clicked, &dialog, &QDialog::accept);
    QObject::connect(add, &QPushButton::clicked, &dialog, [&]() {
        const QString name = resourcePathInput(&dialog, QStringLiteral("新建用户资源"), QStringLiteral("相对路径（例如 tex/latex/user/mypackage.sty）："), QLineEdit::Normal, selectedDirectory() + "/mypackage.sty");
        if (name.isEmpty()) return;
        edit(name, QFileInfo::exists(root + "/texmf-home/" + name));
    });
    QObject::connect(modify, &QPushButton::clicked, &dialog, [&]() { if (list.currentItem() && !list.currentItem()->data(0, Qt::UserRole + 1).toBool()) edit(selectedPath(), true); });
    QObject::connect(import, &QPushButton::clicked, &dialog, [&]() {
        const QString path = FileDialog::getOpenFileName(&dialog, QStringLiteral("添加用户资源文件"), QString(), QStringLiteral("资源文件 (*.sty *.cls *.tex *.lua *.def *.fd *.cfg *.clo *.ltx *.ldf *.bib *.bst *.otf *.ttf *.ttc *.txt *.md *.pdf)"));
        if (path.isEmpty()) return;
        const QString ext = QFileInfo(path).suffix().toLower();
        QString directory = "tex/latex/user/";
        if (ext == "lua") directory = "tex/luatex/user/";
        else if (ext == "otf") directory = "fonts/opentype/user/";
        else if (ext == "ttf" || ext == "ttc") directory = "fonts/truetype/user/";
        else if (ext == "bib" || ext == "bst") directory = "bibtex/" + ext + "/user/";
        else if (ext == "txt" || ext == "md" || ext == "pdf") directory = "doc/user/";
        const QString relative = resourcePathInput(&dialog, QStringLiteral("资源保存位置"), QStringLiteral("用户资源树中的相对路径："), QLineEdit::Normal, directory + QFileInfo(path).fileName());
        if (relative.isEmpty()) return;
        const QString error = userFileError(root, relative, base);
        if (!error.isEmpty()) { report(error); return; }
        if (QFileInfo::exists(root + "/texmf-home/" + relative) && QMessageBox::question(&dialog, QStringLiteral("替换文件"), QStringLiteral("替换已有用户文件？\n") + relative, QMessageBox::Yes | QMessageBox::No, QMessageBox::No) != QMessageBox::Yes) return;
        run([=]() {
            QFile input(path);
            if (!input.open(QIODevice::ReadOnly) || input.size() > 256*1024*1024) return QStringLiteral("无法读取文件，或文件超过 256 MiB。");
            const QByteArray data = input.readAll();
            if (input.error() != QFile::NoError) return QStringLiteral("文件读取失败。");
            return saveUserFile(root, relative, data, base);
        });
    });
    QObject::connect(remove, &QPushButton::clicked, &dialog, [&]() {
        QStringList paths;
        for (auto *item : list.selectedItems()) paths.append(item->data(0, Qt::UserRole).toString());
        QSet<QString> files;
        for (const QString &file : userFiles(root)) for (const QString &path : paths)
            if (file == path || file.startsWith(path + "/")) files.insert(file);
        if (paths.isEmpty()) return;
        if (QMessageBox::question(&dialog, QStringLiteral("删除用户资源"), QStringLiteral("删除所选范围内的 %1 个文件及空文件夹？\n源工程文件不会被修改。").arg(files.size()), QMessageBox::Yes | QMessageBox::No, QMessageBox::No) != QMessageBox::Yes) return;
        for (const QString &file : files) {
            const QString error = deleteUserFile(root, file, base);
            if (!error.isEmpty()) { report(error); return; }
        }
        // Remove only empty selected directories and their empty descendants.
        QStringList dirs;
        QDirIterator it(root + "/texmf-home", QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);
        while (it.hasNext()) {
            it.next(); const QString rel = QDir(root + "/texmf-home").relativeFilePath(it.filePath());
            if (it.fileInfo().isSymLink()) continue;
            for (const QString &path : paths) if (rel == path || rel.startsWith(path + "/")) { dirs.append(rel); break; }
        }
        std::sort(dirs.begin(), dirs.end(), [](const QString &a, const QString &b) { return a.size() > b.size(); });
        for (const QString &dir : dirs) QDir().rmdir(root + "/texmf-home/" + dir);
        refresh();
    });
    QObject::connect(backup, &QPushButton::clicked, &dialog, [&]() {
        const QString path = FileDialog::getSaveFileName(&dialog, QStringLiteral("导出用户资源备份"), "texstudio-user-resources.zip", QStringLiteral("TeX 资源包 (*.zip)"));
        if (!path.isEmpty()) run([=]() { return exportUserArchive(root, path, base); });
    });
    QObject::connect(restore, &QPushButton::clicked, &dialog, [&]() {
        const QString path = FileDialog::getOpenFileName(&dialog, QStringLiteral("恢复用户资源"), QString(), QStringLiteral("TeX 资源包 (*.zip)"));
        if (path.isEmpty()) return;
        if (QMessageBox::question(&dialog, QStringLiteral("替换全部用户资源"), QStringLiteral("恢复将替换当前全部用户文件。请先导出备份。\n只接受本应用兼容的资源 ZIP；原 ZIP 无需一直保留。"), QMessageBox::Yes | QMessageBox::No, QMessageBox::No) != QMessageBox::Yes) return;
        run([=]() { return restoreUserArchive(root, path, base); });
    });
    QObject::connect(index, &QPushButton::clicked, &dialog, [&]() { run([=]() { return refreshUserIndex(root); }); });
    refresh(); fitHarmonyDialog(&dialog, 66, 34); dialog.exec();
}
