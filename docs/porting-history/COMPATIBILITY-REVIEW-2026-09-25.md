> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 真机兼容性复核、应用补测与 CLI 评估

日期：2026-09-25。结论：核心编译链可用，但不能将此次报告表述为“完整兼容性验收通过”。基础 BibTeX 样式缺失已在应用中复现；HiShell 字体族名问题不能推广到应用；自建 Beamer 存在原报告遗漏的内容裁切。建议先修复资源与构建状态，再增加应用自动化入口。

## 1. 范围与证据

- 新连接设备：`6UZ0226107000081`，QXS-W00；原环境记录 HarmonyOS 7.0.0.107、API 26。
- 本次通过设备包管理器确认 `com.ohos.texstudio` 为 **1.0.20 / 1000020**，不是根据引擎目录推断应用版本。
- 原始报告：设备 `~/.dsh/work/texstudio-compat-test`，完整拉取 355 个文件，8,949,431 字节。电脑副本位于 `validation/compat-review-2026-09-25/texstudio-compat-test/`。原报告、原工程未改写。
- 隔离补测目录：设备 `/storage/Users/currentUser/Download/CompatReview/`；电脑输入 `validation/compat-review-2026-09-25/device-input/CompatReview/`，输出 `app-output/`。
- 本文以下相对证据路径均位于 `validation/compat-review-2026-09-25/`。`evidence-manifest.json` 记录原始副本和应用输出共 411 个文件的 SHA-256；`review-result.json` 记录补测结论和 PDF 文本、摘要。
- 编译由真机 TeXstudio 菜单触发，HDC 只负责文件传输、界面操作、截图和进程观察。没有把 HDC shell 中直接调用引擎当成 HiShell 或应用验收。
- 本次没有重建、签名、安装新版，也没有修改应用实现；资源缺陷仍待修复。

## 2. 对原报告的核对

| 原结论 | 复核结论及边界 |
|---|---|
| `plain.bst` 等基础样式缺失 | **确认 plain 工作流阻断，并在应用复现。** `app-output/02-bibplain.blg` 明确报无法打开 plain.bst。其他三种基础样式的缺失保留为原报告中的目录/查询证据，未逐个在应用编译。不能用 natbib 已通过推断基础 BibTeX 已完整。 |
| 字体族名不可用 | **限定于原 HiShell 环境。** 应用中按 `Latin Modern Roman`、`FandolSong` 族名编译和预览成功。应用生成独立 Fontconfig 配置，搜索路径与终端不同。 |
| 用户资源不可用 | **默认 HiShell 搜索路径没有自动接入用户层，不等于所有路径都不可用。** 应用有私有用户资源层；已有导出后配置 TEXINPUTS 等的终端使用方式，见 USER-RESOURCES.md。此次没有重新验收私有用户层的导入/编辑全流程。 |
| 失败后旧 PDF 保留 | **现象确认，但保留上次成功稿本身不是移植错误。** 应分别记录当前构建失败、最后成功版本、部分产物。应用会显示错误；不应描述为完全无错误提示。 |
| 自建 Beamer 仅少量缺字、无大段丢失 | **不成立。** PDF 第 5、6、14 页有内容超出页面；第 5 页表格、第 14 页代码明显被裁切。日志有 51.4482pt、5.76193pt、24.40535pt 的 Overfull vbox。属于样例版面未通过，不能单凭编译退出码判定视觉通过。尚无桌面对照证明这是移植特有缺陷。 |
| pdfLaTeX 不支持中文/空格路径 | **该测试不能单独证明此泛化结论。** 同一个 ctexart/Fandol 中文样例切换 pdfLaTeX，混入字体和引擎适配因素。需用英文 article、分别控制目录/图片名/主文件名并做桌面对照。XeLaTeX/LuaLaTeX 原路径样例的 PDF 已复核。 |
| N2/N3/N4 为 FAIL | 它们是故意缺宏包、缺字体、语法错误的负例。引擎失败是预期行为，应评价是否正确报错，不能直接计入产品失败率。N1 字体族名则属于实际兼容性问题。 |

原报告对 Fontconfig 的解释还需修正：`prefix="default"` 的相对目录按**当前工作目录**解释，`prefix="relative"` 才按配置文件所在目录解释，并非按“安装前缀”。见 [Fontconfig 官方用户文档](https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-user.html)。修复后必须在至少两个工作目录验收，避免只在偶然正确的 cwd 中通过。

原 `run-all.sh` 的陈旧 PDF 用例会修改源文件且不恢复；路径用例轮流清理同名输出。重复执行前需复制隔离目录，不能直接把第二次输出覆盖原证据。原 `evidence/screenshots/` 是文档渲染图，报告也已注明不是应用截图。

## 3. 本次应用补测

| 用例 | 结果 | 证据 |
|---|---|---|
| 系统选择器打开测试源文件 | 通过，实际授权路径可读写 | `fixture-picker.png`、`picker-cancel.png` |
| XeLaTeX 按字体族名加载中英文字体 | 通过，1 页 / 7,360 B，正文和中文预览正确 | `font-result.png`、`app-output/00-font.*` |
| 自建多文件 Beamer 自动构建和预览 | 构建通过，15 页 / 186,449 B；缺字与超高版面仍在 | `beamer-result.png`、`app-output/01-beamer.*` |
| BibTeX plain 自动文献构建 | 失败已复现；应用报错，同时能显示带 `[?]` 的部分 PDF，不能作为成功稿 | `bib-result.png`、`bib-final.png`、`app-output/02-bibplain.*` |
| 正确 ALPHA → 未定义命令 BETA | 应用显示 Undefined control sequence，失败后磁盘 PDF 仍为 ALPHA；SHA-256 完全相同 | `recovery-beta.png`、`recovery-alpha.pdf`、`recovery-beta.pdf` |
| 修正为 GAMMA 后重新构建 | 通过，PDF 文本更新为 APP-RECOVERY-GAMMA，1 页 / 3,405 B | `recovery-gamma.png`、`app-output/03-recovery.*` |
| LuaLaTeX 长计算中点击停止 | 通过，停止前捕获 Perl/latexmk、sh、lualatex 同进程组；停止后 2 秒该组无残留 | `cancel-result.json`、`cancelled.png` |
| 取消后新文档自动构建/预览 | 通过，APP-AFTER-CANCEL-PASS，1 页 / 3,785 B | `after-cancel.png`、`app-output/05-after-cancel.*` |

失败恢复测试最初有一次中文输入法干扰 UI 注入，生成了非预期源文件；`recovery-edit.png`、`recovery-failed.png` 属于这次操作诊断，不纳入正式用例。随后通过隔离目录传入确定的 BETA 源文件、确认编辑器重载，再执行正式失败和 GAMMA 恢复。最终输入目录保留 GAMMA；正式 BETA 内容为 `\documentclass{article}\begin{document}APP-RECOVERY-BETA\undefinedcommandhere\end{document}`。

本轮已覆盖报错、修复重建、停止进程组和后续构建，并非整个应用的稳定性压力测试。

## 4. PDF 复核范围

使用 PyMuPDF 直接打开原始 PDF、提取页数/文本并渲染；使用 pdffonts 记录字体信息。不是再次通过 XDV/dvisvgm 模拟 PDF。结果见 `pdf-audit.json` 与 `pdf-review/`。

- 原证据 10 份 PDF 均已解析；少于等于 15 页的文档渲染全部页面并查看联系表；自建 Beamer 第 5、14 页额外放大查看。
- 60 页用户 Beamer 检查第 1、2、16、26、36、37、46、60 页，**未逐页目视验收全部 60 页**。
- 自建多文件论文、用户概率论文、natbib/Biber、Xe/Lua 中文空格路径样例的已查看页面，未发现 Beamer 那样的明显裁切。
- 缺字体失败产生的空白 PDF、失败后保留 ALPHA 的 PDF 也已查看。PDF 文件存在或可打开不能代表此次构建成功。

## 5. CLI 建议是否可行

**值得做，但应是“应用自动化接口 + HiShell 客户端”，而不是再包装一套终端编译命令。** 当前源码已有桌面命令行参数（打开文件、主文件、行号、PDF 浏览等），却没有面向测试的结构化构建任务、日志、取消和资源状态接口。相关入口：

- `texstudio-harmony/third_party/texstudio/src/texstudio.cpp` 的 `executeCommandLine()`（约 7704 行）。
- `src/harmonyresources.cpp`（约 490–545 行）：应用配置 TEXMFHOME、TEXINPUTS、BSTINPUTS、字体目录和私有缓存；终端自己运行引擎不能代表这段流程正确。
- `texstudio-harmony/texstudio_harmony/entry/src/main/ets/qability/QAbility.ets` 与 `qabilitystage/QAbilityStage.ets`：生命周期/Want 与 Qt 启动交接，尚无上述任务协议。

### 鸿蒙边界

现有签名 HNP 公共命令已证明此项目能提供终端可执行程序；但 CLI 进程不会因此获得 TeXstudio 的 UID、私有资源或启动后台应用的权限。不能设计成调用 HiShell 中不存在的 `aa`，也不能把电脑 HDC 的权限当成终端 AI 的权限。

[华为 UIAbilityContext 文档](https://developer.huawei.com/consumer/cn/doc/doccenter-references/api/js-apis-inner-application-uiabilitycontext)提供 Ability 启动及 Want 参数机制，具体调用仍受系统启动规则约束。[华为外部二进制说明](https://developer.huawei.com/consumer/cn/doc/doccenter-dev-faq/faqs-access-control-23)说明签名、沙箱模式和目录权限是独立条件。现有开发设备可行不等于已验证所有发行渠道或后台启动场景。

第一版建议要求 TeXstudio 已打开、用户开启本次自动化会话；先做 **HiShell 实际 UID → 应用 → JSON 返回** 的通信原型。候选为受令牌保护的本机服务，或用户授权共享目录中的请求/响应队列。跨沙箱连通性、目录权限和应用后台行为都需实测，当前尚未验证某一种传输方案。

### 最小功能范围

| 命令示意（尚未实现） | 必须返回/执行的内容 |
|---|---|
| `texstudioctl status --json` | 应用/协议版本、当前项目、繁忙状态 |
| `texstudioctl open <path>` | 仅打开已授权路径；有未保存编辑时明确拒绝覆盖 |
| `texstudioctl build --engine xelatex --wait --json` | 进入应用 BuildManager，在 Qt 主线程协调；沿用 GUI 的资源环境、主文件和构建链 |
| `texstudioctl cancel <job-id>` | 取消实际构建进程组，确认退出后返回 |
| `texstudioctl logs <job-id>` | 结构化错误、警告与原始日志位置 |
| `texstudioctl resources status --json` | 生效资源层、版本、字体配置、关键资源定位，避免输出敏感配置 |
| `texstudioctl preview status --json` | 当前显示文档、页数、关联构建任务；明确当前失败/上次成功/部分产物 |

任务结果至少包含 job-id、状态、引擎、退出码、错误/警告数、PDF 摘要和来源任务；区分成功、失败、取消、超时、忙碌。协议只提供列出的动作，不暴露任意 shell 执行能力。用户启用会话、路径校验、并发/超时处理是接口设计的一部分。

CLI 可以让鸿蒙端 AI 完成应用构建、日志判定、资源定位、取消与结果新旧判定。**不能替代触控命中、键盘/输入法、窗口布局、滚动缩放、SyncTeX 实际跳转和页面视觉检查。** 通过 CLI 导出页面图像也仅覆盖内容渲染，不等于界面操作通过。

## 6. 建议的执行顺序

1. 补齐并锁定 BibTeX 基础资源，在干净构建资源树中检查依赖闭包；应用和 HiShell 分别跑 plain、abbrv、unsrt、alpha 的文献用例。
2. 修正公共 Fontconfig 的相对路径，在全新 HiShell 会话与不同工作目录验证字体族名；确认应用已有字体行为不回归。
3. 为预览增加明确的构建状态与来源标识，保留上次成功稿；不要默认删除用户可能需要的旧 PDF。修正 Beamer 样例的分页和字体覆盖。
4. 做上述 CLI 通信原型，通过真实 HiShell 往返验证后，再接入 open/build/cancel/logs；对同一项目比较 CLI 与 GUI 的资源、日志和 PDF。
5. 完成尚缺的私有用户资源导入/编辑闭环、受控 pdfLaTeX 路径对照，以及触控、输入法、预览缩放/跳转和长时稳定性测试。`dvisvgm --pdf` 的外部依赖支持也未因本次复核而变成已验收。

本报告是下一轮修复和自动化开发的基线，不修改既有交付版本号，不宣称上述缺陷已修复。
