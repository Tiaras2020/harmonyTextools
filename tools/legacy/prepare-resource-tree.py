from pathlib import Path
r = Path(__file__).resolve().parents[1]
p = r/'texstudio-harmony/third_party/texstudio/src/harmonyuserresourcesdialog.cpp'
t = p.read_text(encoding='utf-8')
t = '#include "harmonydialoglayout.h"\n#include <QTreeWidget>\n#include <QDirIterator>\n#include <QMenu>\n#include <QToolButton>\n#include <QSet>\n#include <QHeaderView>\n' + t
t = t.replace('dialog.setMinimumSize(1000, 850);', '')
t = t.replace('description.setMinimumHeight(110);', 'description.setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);')
t = t.replace('QListWidget list; list.setMinimumHeight(180); layout.addWidget(&list);', '''QTreeWidget list; list.setHeaderLabels({QStringLiteral("文件 / 文件夹")});
    list.setSelectionMode(QAbstractItemView::ExtendedSelection);
    list.setMinimumHeight(180); list.setUniformRowHeights(true);
    list.header()->setSectionResizeMode(QHeaderView::ResizeToContents);
    layout.addWidget(&list, 1);
    auto selectedPath = [&]() { return list.currentItem() ? list.currentItem()->data(0, Qt::UserRole).toString() : QString(); };
    auto selectedDirectory = [&]() {
        if (!list.currentItem()) return QStringLiteral("tex/latex/user");
        return list.currentItem()->data(0, Qt::UserRole + 1).toBool()
            ? selectedPath() : QFileInfo(selectedPath()).path();
    };''')
start=t.index('    auto refresh = [&]() {')
end=t.index('    auto report = ',start)
t=t[:start]+'''    auto refresh = [&]() {
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
        if (item->data(0, Qt::UserRole + 1).toBool()) { details.setPlainText(file + QStringLiteral("\\n文件夹；可以新建子文件夹或选择其中的文件。")); return; }
        const auto conflicts = userConflicts(root, file, base, sessionResource());
        details.setPlainText(file + "\\n" + (conflicts.isEmpty() ? QStringLiteral("未发现其他资源层的同名文件。") : QStringLiteral("存在同名文件；启用时用户版本优先。\\n") + conflicts.join('\\n')));
    });
''' + t[end:]
t=t.replace('layout.addWidget(&actions);', 'actions.hide();')
t=t.replace('layout.addWidget(&backups);', '''backups.hide();
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
        const QString name = QInputDialog::getText(&dialog, QStringLiteral("新建文件夹"), QStringLiteral("相对路径："), QLineEdit::Normal, selectedDirectory() + "/my-resources");
        if (!name.isEmpty()) report(createUserFolder(root, name, base));
    });
    QObject::connect(importZip, &QPushButton::clicked, &dialog, [&]() {
        const QString path = FileDialog::getOpenFileName(&dialog, QStringLiteral("导入用户资源包（保留现有资源）"), QString(), QStringLiteral("TeX 资源包 (*.zip)"));
        if (!path.isEmpty()) run([=]() { return restoreUserArchive(root, path, base, true); });
    });''')
t=t.replace('"tex/latex/user/mypackage.sty");', 'selectedDirectory() + "/mypackage.sty");')
t=t.replace('if (list.currentItem()) edit(list.currentItem()->text(), true);', 'if (list.currentItem() && !list.currentItem()->data(0, Qt::UserRole + 1).toBool()) edit(selectedPath(), true);')
start=t.index('    QObject::connect(remove,')
end=t.index('    QObject::connect(backup,',start)
t=t[:start]+'''    QObject::connect(remove, &QPushButton::clicked, &dialog, [&]() {
        QStringList paths;
        for (auto *item : list.selectedItems()) paths.append(item->data(0, Qt::UserRole).toString());
        QSet<QString> files;
        for (const QString &file : userFiles(root)) for (const QString &path : paths)
            if (file == path || file.startsWith(path + "/")) files.insert(file);
        if (paths.isEmpty()) return;
        if (QMessageBox::question(&dialog, QStringLiteral("删除用户资源"), QStringLiteral("删除所选范围内的 %1 个文件及空文件夹？\\n源工程文件不会被修改。").arg(files.size()), QMessageBox::Yes | QMessageBox::No, QMessageBox::No) != QMessageBox::Yes) return;
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
''' +t[end:]
t=t.replace('refresh(); dialog.exec();','refresh(); fitHarmonyDialog(&dialog, 66, 34); dialog.exec();')
t='#include <QStyle>\n#include <QMap>\n#include <algorithm>\n'+t
p.write_text(t,encoding='utf-8',newline='\n')
print('Resource tree, multi-selection, folders, merge import and action menu prepared')
