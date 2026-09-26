"""Apply scoped UI fixes; retain all replaced files before editing."""
from pathlib import Path
import json, shutil
r = Path(__file__).resolve().parents[1]
s = r/'texstudio-harmony/third_party/texstudio/src'
backup = r/'validation/interaction-1.0.24/before'
def edit(name, transform):
    p = s/name
    dest = backup/name
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    p.write_text(transform(p.read_text(encoding='utf-8')), encoding='utf-8', newline='\n')
def layout_config(t):
    t = '#include "harmonydialoglayout.h"\n' + t
    marker = 'void ConfigDialog::showAndLimitSize() {\n'
    t = t.replace(marker, marker + '''#ifdef Q_OS_OHOS
    setFont(QApplication::font());
    const int em = fontMetrics().height();
    // A useful navigation width, independent of a previously saved splitter.
    ui.contentsWidget->setIconSize(QSize(em, em));
    ui.contentsWidget->setMinimumWidth(10 * em);
    ui.contentsWidget->setTextElideMode(Qt::ElideNone);
    ui.contentsWidget->setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    ui.mainSplitter->setSizes({10 * em, 60 * em});
    ui.shortcutTree->header()->setSectionResizeMode(QHeaderView::ResizeToContents);
    ui.shortcutTree->header()->setStretchLastSection(false);
    for (auto *label : findChildren<QLabel *>()) {
        label->setWordWrap(true);
        label->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);
    }
    for (auto *area : findChildren<QScrollArea *>()) {
        area->setWidgetResizable(true);
        if (area->widget() && area->widget()->layout())
            area->widget()->layout()->setAlignment(Qt::AlignTop);
    }
    fitHarmonyDialog(this, 82, 38);
#endif
''')
    return t
edit('configdialog.cpp', layout_config)
def style(t):
    # Let Fusion measure and paint label/shortcut columns together. QSS item
    # padding bypassed its native shortcut spacing for some translated labels.
    t = '\n'.join(line for line in t.split('\n') if not ('"QMenu' in line and  'QString' not in line))
    return t
edit('configmanager.cpp', style)
def tab(t):
    t = '#include "harmonydialoglayout.h"\n#include <QHeaderView>\n' + t
    t = t.replace('UtilsUi::resizeInFontHeight(this, 53, 44);', '''#ifdef Q_OS_OHOS
    fitHarmonyDialog(this, 56, 30);
    const int em = fontMetrics().height();
    ui.tableWidget->setMinimumHeight(7 * em);
    ui.tableWidget->setMaximumHeight(16 * em);
    ui.tableWidget->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    ui.tableWidget->verticalHeader()->setDefaultSectionSize(2 * em);
    ui.tableWidget->setAlternatingRowColors(true);
    ui.tableWidget->setToolTip(QStringLiteral("双击单元格输入内容；在下方设置行列和边框。"));
    ui.gridLayout->setRowStretch(0, 1);
#else
    UtilsUi::resizeInFontHeight(this, 53, 44);
#endif''')
    return t
edit('tabdialog.cpp', tab)
def cli(t):
    t = '#include "harmonydialoglayout.h"\n' + t
    t = t.replace('description.setWordWrap(true); layout.addWidget(&description);', 'description.setWordWrap(true); description.setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum); layout.addWidget(&description);')
    t = t.replace('dialog.resize(900, 400); dialog.exec();', 'layout.addStretch(); fitHarmonyDialog(&dialog, 62, 22); dialog.exec();')
    return t
edit('texstudio.cpp', cli)
def resources(t):
    t = '#include "harmonydialoglayout.h"\n#include <QMenu>\n#include <QToolButton>\n' + t
    t = t.replace('dialog.resize(720, 460);', '')
    t = t.replace('description.setWordWrap(true);', 'description.setWordWrap(true); description.setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);')
    t = t.replace('layout.addWidget(&buttons);', 'buttons.hide();')
    for name in ('exportButton','deleteButton'):
        t = t.replace('management.addButton(QStringLiteral("'+ ('导出所选资源…' if name=='exportButton' else '删除所选资源…') +'"), QDialogButtonBox::ActionRole)', 'buttons.addButton(QStringLiteral("'+ ('导出所选资源…' if name=='exportButton' else '删除所选资源…') +'"), QDialogButtonBox::ActionRole)')
    marker='layout.addWidget(&management);'
    t = t.replace(marker, '''QMenu operations(&dialog);
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
    layout.addWidget(&management);''')
    t = t.replace('dialog.exec();', 'fitHarmonyDialog(&dialog, 65, 28); dialog.exec();')
    return t
edit('harmonyresourcesdialog.cpp', resources)
release = r/'texstudio-harmony/release.json'
d=json.loads(release.read_text()); assert d['version']=='1.0.23'
d.update(version='1.0.24',versionCode=1000024)
release.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for old,new in [('build-lua-cli.sh','build-interaction.sh'),('stage-lua-cli-app.sh','stage-interaction-app.sh'),('assemble-lua-cli-package.py','assemble-interaction-package.py'),('check-lua-cli-package.py','check-interaction-package.py')]:
    t=(r/'build-support'/old).read_text()
    t=t.replace('lua-cli-1.0.23','interaction-1.0.24').replace('1.0.23','1.0.24').replace('1000023','1000024').replace('build-lua-cli.sh','build-interaction.sh').replace('check-lua-cli-package.py','check-interaction-package.py')
    (r/'build-support'/new).write_text(t,encoding='utf-8',newline='\n')
print('Prepared 1.0.24 dialog changes')
