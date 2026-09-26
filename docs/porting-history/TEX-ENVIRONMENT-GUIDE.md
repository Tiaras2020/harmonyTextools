> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 从本项目理解 TeX 环境

TeXstudio 是编辑器，TeX Live 是包含引擎、宏包、字体和工具的发行版，LaTeX 是建立在 TeX 排版系统之上的文档命令体系。本项目将编辑器和经过兼容性筛选的运行环境一起带到鸿蒙；它们协作，但不是同一个程序。

## 六个组成部分

| 部分 | 输入与职责 | 本项目中的例子 |
|---|---|---|
| 编辑器 | 编辑文本、选择主文件、发起构建、展示日志与 PDF | TeXstudio、内置 PDF 预览 |
| 构建调度 | 判断需要哪些程序、是否重编译、是否再跑一轮 | latexmk |
| 排版引擎 | 解释底层指令，计算字形、断行、分页和输出 | pdfTeX、XeTeX、LuaHBTeX |
| 格式、文档类与宏包 | 定义 `\section`、数学、中文、幻灯片等高层行为 | LaTeX 格式、article.cls、ctex、beamer |
| 字体和数据 | 提供字形轮廓、字体度量、映射、断词等 | OTF/TTF/TTC、TFM、字体映射 |
| 辅助工具 | 参考文献、索引、输出转换等 | BibTeX、Biber、xdvipdfmx |

`pdflatex`、`xelatex`、`lualatex` 通常代表“某种引擎加载相应 LaTeX 格式”的入口。`.fmt` 是事先处理好的一部分宏定义和引擎状态，启动时载入，省去每次重新初始化；它和引擎版本、内核版本有匹配关系。

## 一段源码如何变成 PDF

```tex
\documentclass{article}
\usepackage{amsmath}
\begin{document}
\section{Example}
\[ a^2+b^2=c^2 \]
\end{document}
```

1. 编辑器将源码保存成 `.tex`，识别主文档，并准备本次构建的资源路径和工作目录。
2. latexmk 启动所选引擎。引擎加载 LaTeX 格式，查找 `article.cls` 和 `amsmath.sty`，执行它们的定义。
3. 宏把文档命令逐步转换为排版操作；引擎结合字体，把文字和数学组织成盒子、间距、行和页面。LuaTeX 还可以通过 Lua 回调参与这些步骤。
4. 引擎写出排版结果和 `.aux`、`.log` 等中间文件。pdfLaTeX/LuaLaTeX 通常直接写 PDF；XeLaTeX 通常先写 XDV，再用 xdvipdfmx 生成 PDF。
5. 目录、交叉引用和参考文献可能需要重复编译。latexmk 观察依赖变化，按需要调用 BibTeX/Biber，并再次运行引擎。
6. 编辑器打开 PDF。启用 SyncTeX 时，另一个映射文件记录源码位置和 PDF 位置，供正反向跳转使用。

因此，“按钮显示完成”“进程退出码为零”“PDF 存在”“PDF 来自本次构建”“页面内容正确”是不同的证据。我们的 CLI 需要逐步把这些状态区分开，而不是只判断文件是否存在。

## 用户资源到底改了什么

用户资源是一棵可写的 TEXMF 文件树。它给文件搜索系统增加一组候选文件，并不重新编译排版引擎。本项目的主要查找顺序是：项目目录 → 启用的用户树 → 内置发行资源 → 当前附加资源。

| 文件类型 | 能改变的效果 |
|---|---|
| `.sty` | 新命令、章节格式、颜色、表格、特殊排版逻辑 |
| `.cls` | 整体文档结构、版心、默认字体和标题体系 |
| `.lua` | Lua 引擎下的字符处理、字体处理、节点和排版回调等 |
| `.otf/.ttf/.ttc` | 字形、字体选择及可覆盖的文字范围 |
| `.bst` | BibTeX 的文献输出规则 |
| `.bib` | 文献数据本身；一般随项目保存更直观 |

普通宏包可以自己修改。建议依次采用：宏包的现有选项 → 自己写一个小宏包调用或调整已有命令 → 必要时放修改后的宏包副本。以不同名字发布自己的宏包最清楚；同名覆盖适合明确知道版本依赖的情况。停用或移除用户副本后，搜索会回退到其他资源层。分发修改版时还应遵守该包的许可要求。

例如新建 `tex/latex/user/mylook.sty`：

```tex
\ProvidesPackage{mylook}
\RequirePackage{xcolor}
\newcommand{\ProjectWord}[1]{\textcolor{blue}{\textbf{#1}}}
```

正文加入 `\usepackage{mylook}`，然后使用 `\ProjectWord{Important}`。修改用户宏包中的 `blue` 为 `red` 后重新编译，可以直接观察资源层修改如何改变结果。

应用保护 LaTeX 内核、l3 等基础组件，也拒绝原生程序和格式文件。这是本项目的产品策略，不代表 TeX 从原理上不能修改内核。内核、引擎和格式的升级应该走发行构建和整套回归，不能当成普通宏包替换。

## 为什么 Lua 曾经不能导入

早期导入器仅接收传统宏包和字体，扩展名白名单没有 `.lua`，也没有开放 `tex/luatex/`。引擎移植成功以后，这条早期规则仍然存在。此前 luatex-cn 放在工程目录中可以编译，与“导入窗口拒绝 ZIP”并不矛盾：前者经过引擎加载路径，后者先经过我们写的导入器。

1.0.23 的实现为 Lua 源码引入 `additive-lua-v1` 资源包格式，保留子目录，沿用大小、路径和摘要校验。纯 Lua 源码可以执行不等于所有 Lua 包都兼容：某些包还需要 `.so` 原生模块、外部程序、字体或特定引擎版本，这些必须分别移植或验证。Lua 和 TeX 源码都可能执行有副作用的操作，导入文件应来自可信来源。

ZIP 是传输容器。导入后的解压文件才是实际资源，删除原 ZIP 不影响已安装文件。用户层处于应用私有目录，HiShell 不会自动共享；导出解压后的副本需要自己的 `TEXINPUTS`、`LUAINPUTS` 等配置。

## 用这个项目学习开发

可以按一次完整功能的路径读代码：

1. `harmonyuserresourcesdialog.cpp`：用户选择文件、输入相对路径、接收错误提示。
2. `harmonyresources.cpp`：检查路径和类型、验证摘要、暂存解压、替换资源树、构造编译环境。
3. `texstudio.cpp` 与 `buildmanager.cpp`：菜单和 CLI 如何共同进入构建流程，如何接收进程结束和日志。
4. `harmonyautomation.h` 与 `tools/texstudioctl.py`：两个进程如何用小型 JSON 协议通信，怎样处理令牌、错误输入和超时。
5. `build-support/test-lua-user-resources.py`：测试不只验证“能导入”，也验证失败不会破坏旧文件，停用后搜索路径会回退。

这次改动最有价值的经验是：文件被接收、文件能被搜索到、引擎能加载它、排版正确，是四个独立环节。定位故障时，先判断问题处在哪一环，再修改对应代码。
