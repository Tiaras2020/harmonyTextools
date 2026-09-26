> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# luatex-cn 鸿蒙兼容性试用

测试日期：2026-09-25。使用 [open-guji/luatex-cn](https://github.com/open-guji/luatex-cn) **v0.4.1**，固定提交 `3b9297f012d71aa148783695bf7942a37a3c281b`。上游 `tex/` 文件未经修改；测试工程只指定本机字体、补充横排入口的本地搜索路径，并增加样例。

## 结论与范围

**可以在当前鸿蒙 LuaHBTeX/LuaLaTeX 移植环境中试用。** 已在真机 TeXstudio 1.0.20 应用和 HiShell 实测，并在 1.0.21 应用补测最终 Noto 字体的古籍整幅页，编译和预览通过；无需为这些样例增加原生二进制或启用 shell-escape。

| 用例 | HiShell 结果 | 应用结果 |
|---|---|---|
| `01-horizontal.tex`：台湾标点风格、简繁中文与英文混排 | 1 页，Noto CJK 版无缺字日志 | 初次 Fandol 版编译预览成功，但有字体缺字；不是完整视觉通过 |
| `02-guji.tex`：四库全书版式、句读、双行夹注、版心 | 2 张半页，Noto CJK 版无缺字日志 | Fandol 版编译和预览成功 |
| `03-modern-vertical.tex`：现代中文竖排 | 1 页，Noto CJK 版无缺字日志 | Fandol 版编译和预览成功 |
| `04-guji-spread.tex`：整幅古籍版面 | 1.0.20 终端生成 1 页并人工检查 | 1.0.21 Noto CJK 版新建构建记录，1 页，零缺字日志；版心、红色句读、夹注及预览通过 |

以上是小型样例验收，不能扩展为所有宏包特性、全部古籍字体、复杂全书模板、长篇跨页夹注、侧批/印章、所有 clreq 条款均已通过。

## 如何在平板使用

测试工程目前在平板：`~/Download/LuaTeXCn/LuaTeXCn/`。保持整个目录结构，使用 TeXstudio 打开 `01-horizontal.tex`、`02-guji.tex` 或 `03-modern-vertical.tex`，执行“工具 → 自动构建并预览（LuaLaTeX）”。不要选择 XeLaTeX 或 pdfLaTeX。

HiShell 中可直接进入该目录运行：

```sh
cd ~/Download/LuaTeXCn/LuaTeXCn
latexmk -lualatex -interaction=nonstopmode -halt-on-error 02-guji.tex
```

这是**工程随附宏包**的方式；ZIP 是普通工程压缩包，不是应用的离线资源导入包。此前 1.0.21 的资源策略不接受 `.lua`。1.0.23 已增加 Lua 配置，并提供单独的 `luatex-cn-v0.4.1-user-resources.zip`；已实测从私有用户层加载的横排样例。使用方法和替换用户层的注意事项见 `LUA-RESOURCES-CLI-1.0.23.md`。任意上游 ZIP 仍不等于本应用的资源包。

### 两个实测注意点

1. **本地目录搜索。** 宏包横排入口按文件名加载 `luatex-cn-hori.sty`，实际文件位于 `hori/`。安装在标准递归 TEXMF 树时可自动找到，但放在普通工程目录时需要搜索路径。样例中使用：

   ```tex
   \makeatletter\def\input@path{{hori/}}\makeatother
   \usepackage[style=taiwan]{luatex-cn}
   ```

   保留 `core/`、`shared/`、`hori/` 等子目录；不要只复制顶层 `.sty`。

2. **字体覆盖。** 初测 `FandolSong-Regular.otf` 对样例部分繁体字没有字形。最终试用工程使用此设备已存在的系统字体：

   ```tex
   \setmainfont{NotoSerifCJK-Regular.ttc}[Path=/system/fonts/,FontIndex=3]
   ```

   该字体未打包、未从系统复制分发。其他设备需要确认字体文件和集合索引；找不到时换成用户合法取得且覆盖正文字符的字体。直接换成 Fandol 不保证繁体古籍零缺字。

默认古籍模板开启筒子页拆分，将整张版式分成左右两个 PDF 页面，版心在中缝处拆开是上游设计。整幅页用例单独保留为 `04-guji-spread.tex`，在文档开始后调用 `\disableSplitPage`。

## 证据

- `validation/luatex-cn/upstream-lock.json`：上游提交锁定。
- `validation/luatex-cn/app-initial/`：1.0.20 应用构建的 Fandol 版源文件、日志和 PDF。
- `validation/luatex-cn/app-1.0.21/LuaTeXCn/04-guji-spread.*`：新版本应用整幅页验收；此目录其他文件来自既有终端构建，不视为 1.0.21 应用复测。
- `validation/luatex-cn/hishell-1.0.20/`：Noto CJK 版终端构建证据。
- `validation/luatex-cn/pdf-audit.json` 与 `pdf-review/`：页数、摘要、缺字检查及直接 PDF 渲染。
- 初测截图位于 `validation/compat-review-2026-09-25/cn-*.png`。不要混淆应用截图和电脑上的 PDF 栅格图。

官方源码注明 Apache-2.0；工程样例保留上游许可证。此次未运行上游字体下载器，也未向 GitHub 发布代码或反馈。

可分发试用工程：`artifacts/luatex-cn-v0.4.1-harmony-demo.zip`（约 433 KiB），已复制到平板 Download。解压后保留整个目录并选择 LuaLaTeX；ZIP 本身编译时无需保留。包内不含系统字体。
