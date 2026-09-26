> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 可编辑用户资源与 HiShell

## 1.0.24 管理界面更新

资源按文件夹树显示，Shift 连续多选、Ctrl 分散多选；操作按钮和右键菜单提供新建文件夹、添加/新建文件、删除、备份等入口。新建文件夹须符合 tex、fonts、bibtex、doc 等允许路径；尚不支持重命名、移动或拖放。

“导入 ZIP（保留现有资源）”验证协议清单后合并，保留标准目录结构；已有同路径文件时拒绝整包，避免静默覆盖。“从 ZIP 恢复”仍替换整个用户层，操作前先备份。ZIP 导入不是任意源码仓库解压，需按既有资源包协议打包。导入完成无需保留原 ZIP；想回退或转移时应另留备份。

用户层功能自 1.0.11 提供。1.0.23 扩展了 Lua 源码导入，运行包复用 1.0.21；最新实现与验证边界见 `LUA-RESOURCES-CLI-1.0.23.md`，环境组成见 `TEX-ENVIRONMENT-GUIDE.md`。完整兼容发行资源预装在公共 HNP，HiShell 可直接使用。本文的导出同步步骤针对用户自行编辑的私有资源；历史双版本验证见 `FULL-RESOURCES.md`。

## 在 TeXstudio 中使用

打开「选项 → 离线资源管理 → 用户资源」。

- 「添加文件」加入宏包、类文件、Lua 源码、BibTeX 数据/样式、OTF/TTF/TTC 字体等；可以修改保存的相对路径。Lua 包必须保留子目录，原生 `.so` 模块不在支持范围。
- 「新建文本」「编辑」直接修改 UTF-8 文本。编辑器上限 2 MiB，单个导入文件上限 256 MiB。
- 「删除」只删除选中的用户文件。「启用用户资源」可停用整个用户层，文件仍保留。
- 「导出备份」生成带校验清单的 ZIP。「从 ZIP 恢复」校验兼容性和文件后替换全部用户资源；需要保留当前内容时先导出。恢复接受本应用兼容的 additive-v1 和 additive-lua-v1 资源包，不接受任意 CTAN ZIP。含 Lua 的新备份不能给旧版应用恢复。
- 保存、删除、启停从下一次编译生效，无需重启。字体变更使用新的缓存目录，也可手动刷新索引和字体缓存。

搜索顺序为：项目当前目录 → 用户资源 → 内置资源 → 当前启用的附加资源。内置和附加资源之间保留 B1 的基础资源优先策略。同名文件在列表下方显示来源；同一用户树内不宜放多个同名宏包。用户层不能替换 LaTeX base、latexconfig、l3 等受保护基础组件，也不能导入原生程序、格式或 texmf.cnf。

建议路径：

| 文件 | 用户树中的位置 |
| --- | --- |
| 自定义 `.sty` / `.cls` | `tex/latex/user/` |
| Lua 宏包及其 `.lua` 子模块 | `tex/luatex/包名/`，保留原包内部目录 |
| `.bib` / `.bst` | `bibtex/bib/user/` / `bibtex/bst/user/` |
| `.otf` | `fonts/opentype/user/` |
| `.ttf` / `.ttc` | `fonts/truetype/user/` |

文件保存在应用持久目录的 `tex-resources/texmf-home`，不修改发行资源及其校验清单。导入/恢复完成后，编译不再依赖原 ZIP。卸载或清除应用数据前应向公共目录导出备份。

## 在 HiShell 中使用

真机 HiShell 能直接找到 `/data/service/hnp/bin/pdftex`、`xelatex`、`kpsewhich`，并读取公共 HNP 的内置资源。应用私有的附加包和用户层不会自动加入 HiShell 搜索路径。

操作流程：

1. 在用户资源窗口导出 `texstudio-user-resources.zip`，保存到「下载」。
2. 在 HiShell 中访问下载目录；系统询问时允许终端访问该目录。
3. 解压到一个新的目录，避免把已删除的旧文件残留在原解压目录中。
4. 为当前终端设置搜索路径，然后编译自己的文档。

```sh
cd /storage/Users/currentUser/Download
unzip texstudio-user-resources.zip -d texstudio-user-20260916
export TEXSTUDIO_USER_TREE="$PWD/texstudio-user-20260916/texmf"
export TEXINPUTS=".:$TEXSTUDIO_USER_TREE/tex//:"
export LUAINPUTS=".:$TEXSTUDIO_USER_TREE/{tex,scripts}//:"
export BIBINPUTS=".:$TEXSTUDIO_USER_TREE/bibtex/bib//:"
export BSTINPUTS=".:$TEXSTUDIO_USER_TREE/bibtex/bst//:"
export OPENTYPEFONTS=".:$TEXSTUDIO_USER_TREE/fonts/opentype//:"
export TRUETYPEFONTS=".:$TEXSTUDIO_USER_TREE/fonts/truetype//:"

kpsewhich mypackage.sty
cd /你的项目目录
pdftex -progname=pdflatex -interaction=nonstopmode main.tex
# 或
xelatex -interaction=nonstopmode main.tex
```

末尾的冒号保留内置默认搜索路径，前面的 `.` 保留项目文件优先。不要将 TEXINPUTS 只设成用户目录而丢失默认值。上述变量只影响当前终端及其子进程，不会改写终端启动配置。

这是一份导出快照，不是实时共用目录。应用内再次修改后，重新导出、解压到新目录并更新变量。原 ZIP 可移走；终端要保留解压目录。停用应用用户层不会停用已经导出的终端副本。

实测使用本机已有 `unzip`（来自 Harmonybrew）；应用本身不安装该工具。字体按文件路径使用更明确，例如 `fontspec` 的 `Path` 指向导出的字体目录；按字体家族名搜索还涉及 HiShell 自己的 Fontconfig 配置，本轮没有把这一项列为真机通过。BibTeX 搜索变量提供了接入方式，完整文献流程仍在后续验收范围。

## 验证记录

宿主：17 项资源导入回归、9 项管理回归、10 项用户层回归，覆盖实际 pdfTeX 编译、下一次编译读取编辑、启停回退、备份恢复、非法路径/内核保护、失败恢复保留原文件、字体添加/停用/删除。

真机记录和最终状态见 `validation/resources/device-result-1.0.11.json`。HiShell 使用应用导出的备份，pdfTeX 和 XeLaTeX 均输出 `User edit works.`；记录为 `hishell-result-1.0.10.txt` 和两个 `hishell-*-1.0.10.pdf`。

以上验证记录属于历史 B2.1 阶段。后续完整版、Perl/latexmk、Biber、LuaHBTeX 的交付状态见 `START-HERE.md`；1.0.23 的 Lua 用户资源和 CLI 有单独验证记录，不能把旧记录当成新版全量验收。
