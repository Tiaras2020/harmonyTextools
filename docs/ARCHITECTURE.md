# 架构与文件导航

| 层 | 作用 | 入口 |
|---|---|---|
| Harmony 应用壳 | 生命周期、权限、Qt 宿主与 HNP 打包 | texstudio_harmony/ |
| Qt Widgets 编辑器 | 文档、结构、菜单、构建调度与 PDF 窗口 | third_party/texstudio/src/texstudio.cpp |
| 资源与用户层 | ZIP 导入、路径校验、索引、字体与宏包搜索 | harmonyresources* / harmonyuserresources* |
| CLI | 授权工程、token 请求、任务日志与恢复 | harmonyautomation.h / harmonyproject.h / harmonyclihelp.h |
| AI | 请求、工具、历史、字体/Markdown/UI | harmonyaiworkbench.h / harmonyaitools.h / harmonymarkdown.h |
| 校对与浮窗 | 在线中文检查、结果列表、窗口重挂接 | harmonyproofpanel.h / harmonyfloatingpanel.h |
| 引擎运行包 | TeX 引擎、Perl/latexmk、Biber 与资源树 | scripts/texlive/；Release HNP |
| PDF | Poppler 与 SyncTeX | third_party/poppler；src/pdfviewer/ |

TeX 源码由选定引擎读取宏包、字体、图片等资源，经排版生成 PDF。latexmk 调度引擎和文献处理的重复轮次，PDF 预览器再加载产物。AI/CLI 是控制入口，并不替代 TeX 引擎。

修改 UI 不需要重建所有 TeX 宏包；修改发行资源或引擎需要独立升级 runtimeVersion 并验证格式/字体/搜索路径。不要把能成功交叉编译当作真机排版正确。

父工程脚本、TeXstudio 和 Poppler 原来有独立 Git 历史；本仓库为保全所有本地修改，直接收录最终源码树，来源提交在 UPSTREAM-SOURCES.json。没有指向未公开本地提交的子模块。
