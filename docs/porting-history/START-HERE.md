> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 鸿蒙 TeXstudio 开发交接入口

**阶段收尾：** 用户确认 1.0.36 字体粗细问题仍未修好，要求停止修复并整理交付。当前按“带已知问题交付”保留；先读 `DELIVERY-1.0.36.md`，实际文件清单见 `handoff/release-1.0.36/current-delivery.json`。未上传 GitHub，未删除文件，未清理 WSL。

**当前交付 1.0.36：** 顶部对话名称及会话列表支持右键改名，AI 正文跟随应用字体。核对私有会话目录、工程绑定与上下文限制；尚无自动上下文压缩。说明见 `AI-SESSIONS-1.0.36.md`，安装记录见 `validation/workbench-1.0.36/device-result.json`。未运行功能测试，运行包保持 1.0.30。

**上一版 1.0.35：** 补充常用 Markdown 渲染，默认对话/输入字号降为 10 磅并支持独立设置，输入区可拖动调高；工具记录字号小 1 磅并合并连续背景。按用户要求不运行功能测试，由用户检查后决定收尾。说明见 `AI-TYPOGRAPHY-1.0.35.md`，构建与安装记录见 `validation/workbench-1.0.35/device-result.json`；运行包保持 1.0.30。

**上一版 1.0.34：** 调整 AI 顶部名称标签、工具按钮和半透明消息导航，删除入口移至会话列表右键菜单；修正侧栏图标方向、移除侧栏文字，精简文案并中文化按钮。按用户要求不运行功能测试。操作检查步骤见 `AI-LAYOUT-1.0.34.md`，构建与安装状态见 `validation/workbench-1.0.34/device-result.json`；运行包保持 1.0.30。

**上一版 1.0.33：** 修复粘贴后的控件反色，校对结果可展开；重构工程对话、折叠操作记录、快捷发送与滚动导航，支持置顶窗口、读取日志、PDF 页图及可选 Shell/回收删除。已签名安装并完成限定真机测试，DeepSeek 设置已恢复。真实视觉模型识图质量未验收。说明见 `AI-UX-1.0.33.md`，证据见 `validation/workbench-1.0.33/device-result.json`；运行包保持 1.0.30。

**上一版 1.0.32：** 新增可切换的本地中文词典、左侧校对入口和底部结果栏，重构 AI 侧栏，支持工程文件读取、受控修改、新建、撤销及对话删除；修复显式剪贴板粘贴。真实 DeepSeek 文件修改已在隔离工程验证。详情与测试边界见 AI-WORKBENCH-1.0.32.md，运行包保持 1.0.30。

**上一版 1.0.31：** Qt HTTPS、DeepSeek 预设和流式回复、手动中文在线校对、打开 HiShell/复制工程目录命令。已签名安装并完成限定真机测试；真实 DeepSeek 账号对话仍需用户在设备填写 Key 后验收。运行包保持 1.0.30，详见 `NETWORK-AI-1.0.31.md`。

**上一版 1.0.30：** 修复失效文档列表缓存，内容相等时不再触发结构重载；CLI 区分 `file_missing` 和非法路径。pdfTeX/XeTeX 已编入格式文件描述符所有权修复，应用和运行包均升级为 1.0.30。已签名安装，37 项 CLI 检查、关闭文档、三引擎构建及 Biber 离线处理通过；偶发时序仍需观察。见 `CRASH-FIX-1.0.30.md`。

**上一版 1.0.29：** 新增带 revision 校验的 `document.reload`、内容一致时自动解除冲突、构建拒绝恢复提示。已签名安装并完成限定真机验收；20 条命令帮助同步更新。见 `RELOAD-CLI-1.0.29.md`，运行包仍为 1.0.21。

**上一版 1.0.28：** CLI 构建检查统一到授权工程，返回具体 blockers；连接后自动收进左侧 CLI 入口，后台打开/构建不主动抢前台。已签名安装并完成限定真机验收，见 `BACKGROUND-CLI-1.0.28.md`。运行包保持 1.0.21。

**上一版 1.0.27：** 新增 19 个命令的离线中文 help 和 JSON 帮助；导出的连接 JSON 自带参数、示例和结果含义，保持旧连接字段兼容。已签名安装并完成帮助/连接限定真机验收，见 `CLI-HELP-1.0.27.md`。运行包保持 1.0.21。

**上一版 1.0.26：** 外部文件按内容自动刷新，CLI 读取/构建前主动刷新；未保存冲突保留编辑并拒绝构建。新增明确构建结果、最终轮诊断、旧失败缓存提示和 `build.clean`。已签名安装并完成限定真机验收，见 `REFRESH-CLI-1.0.26.md`。运行包保持 1.0.21。

**上一版 1.0.25：** 工程级只读/打开/主文件切换/构建 CLI 已签名安装并完成限定真机验收；会话不阻挡编辑器，按任务读取日志和 PDF 摘要，未保存编辑受保护。中文不再被英文词典误报，英文拼写检查保留；不是中文错别字词典。使用方式与限制见 `PROJECT-CLI-1.0.25.md`。运行包仍为 1.0.21。

**上一版 1.0.24：** 已签名安装，完成限定范围真机界面验收。修复菜单快捷键间距、设置/Tabular/资源/CLI 窗口布局，新增资源目录树、多选、新建文件夹与 ZIP 合并导入；配置英文词典与同义词。AI 的 HTTPS 被当前 Qt 缺少 TLS 阻断，外部终端桥接尚未实现。结果见 `INTERACTION-1.0.24.md`；工程级 CLI 设计见 `CLI-ROADMAP.md`（此处为 1.0.24 历史状态；后续交付见上文）。

**上一版 1.0.23：** Lua 用户资源导入和应用内构建 CLI 已签名安装并完成限定范围真机验收，复用 1.0.21 运行包。先读 `LUA-RESOURCES-CLI-1.0.23.md`，环境架构与开发学习见 `TEX-ENVIRONMENT-GUIDE.md`。用户资源 ZIP 恢复仍会替换整个用户层，已有内容先备份。

**上一版界面交付 1.0.22：** 已签名安装到新设备，复用内容不变的 1.0.21 运行包。菜单、图标、双向定位、触摸浏览与旧失败缓存恢复的结果及边界见 `UI-POLISH-1.0.22.md`。下一步由用户体验实体鼠标/触控板与窗口布局，再推进 GitHub 整理。

**2026-09-25 新设备兼容性复核：** 见 `COMPATIBILITY-REVIEW-2026-09-25.md`。已核对终端 AI 报告并补测应用字体、Beamer、BibTeX、错误恢复、取消及后续构建；确认 plain.bst 工作流失败，HiShell 字体问题不影响本次应用字体族名用例。报告含遗漏版面问题、CLI 可行性与未测边界；其中 BibTeX 基础资源和 HiShell 字体路径已在 1.0.21 修复，见 `COMPAT-FIX-1.0.21.md`；alpha 中文标签仍有问题，不能视为全量兼容性验收通过。

**2026-09-25 工作顺序更新：先整理空间与恢复材料，再调整界面和操作手感，之后上传 GitHub。** 文件盘点、源码迁移风险与 WSL 退役条件见 `PROJECT-STORAGE-AND-GITHUB-PLAN.md`。目前尚未完成干净环境恢复验证，不能直接清空 WSL；本次盘点未删除或上传文件。

**运行资源基线：1.0.21 默认完整版，修复与新版本验证见 `COMPAT-FIX-1.0.21.md`。1.0.20 的B3.3 LuaHBTeX/LuaLaTeX 已完成真机验收。** HiShell 公共命令、中文与数学、HarfBuzz、Biber、应用自动构建预览、取消和取消后新文档构建通过。详情见 `LUAHBTEX-B33.md`；全量 collection-luatex 与 ConTeXt 尚未验收。

上一交付 **1.0.19 默认完整版，B3.2 收尾已完成真机验收**：Biber 启动路径警告与 xdvipdfmx 配置/映射警告已修复。应用和 HiShell 的中文文献自动构建、增量重建、错误恢复、PDF 预览、运行中取消及取消后构建均通过。最新结果见 `BIBER-POLISH-1.0.19.md`，基础移植与功能边界见 `BIBER-B32.md`。远程 HTTPS 尚未真机验收。

整理日期：2026-09-21。当前开发交付版本：**1.0.36 默认完整版（运行包 1.0.30）**；pdfTeX/XeTeX 已重新编译并包含格式文件所有权修复，格式与资源保持原基线，新 Lua 引擎和格式的独立版本见 `LUAHBTEX-B33.md`。B2.4 已完成 Beamer、PGFPlots、newpx 和 BibTeX 多轮编译真机验收。交付与证据见 `COMMON-RESOURCES-B24.md` 和 `validation/common-resources/device-result-1.0.14.json`。历史精简测试版为 1.0.12，不支持新的 v2 导入包；后续精简构建需使用新版源码并递增版本号。

在 1.0.8 的资源包管理之上，B2.1 增加可编辑用户层：添加、新建、编辑、删除、启停、索引/字体缓存刷新、备份恢复。HiShell 已实测通过导出 ZIP 同步用户宏包并用 pdfTeX/XeLaTeX 编译；应用私有资源不会自动共享给终端。操作说明见 `USER-RESOURCES.md`。

用户最新确定：**默认发布公共 HNP 预装完整兼容运行资源的版本；开发阶段保留精简本体 + 资源包导入；另设可编辑用户层**。B2.2/B2.3 已完成首批集合处理与双版本交付，91,024 个发行资源在完整 HNP 和开发 ZIP 中逐文件一致。真机完成精简版导入和完整版内置编译、预览；HiShell 无资源环境配置即可编译新增宏包及字体。仍有待审核包和不支持字体，详见 `FULL-RESOURCES.md`。

阶段 B1 已实现离线附加资源导入、校验、索引、版本选择及恢复内置资源。1.0.7 已签名安装，真机完成“系统选择 ZIP → 导入 → 重启 → 引用新增宏包编译 → PDF 预览”验收。范围、限制与证据见 `RESOURCE-EXTENSION.md`。1.0.6 是发现 ZIP 库符号冲突的中间调试版，不应使用。

阶段 A 最新结果见 `BASELINE-AUDIT.md`：统一版本配置、实际依赖锁、源码快照和宿主回归已经建立。fdsan 修复已接入后续引擎构建，但新引擎的签名安装及应用内真机验收尚未完成。用户主动删除的历史交付件不需恢复。

新增第三方宏包试用：`LUATEX-CN-COMPATIBILITY.md`，含可在平板打开的工程 ZIP 和已测边界。

## 新对话先读什么

1. `AI-WORKBENCH-1.0.32.md`：当前交付和验收边界；`LUAHBTEX-B33.md`：Lua 引擎验收；`BIBER-POLISH-1.0.19.md`：上一版文献工作流；`BIBER-B32.md`：Biber 基础移植；`LATEXMK-POLISH-1.0.17.md`：上一版取消与 locale 修复；`LATEXMK-B31.md`：自动构建基础；`BIBER-B32.md`：Biber 候选版与真机验收；`COMMON-RESOURCES-B24.md`：资源基线与使用边界；`DEVELOPMENT-HANDOFF.md` 保留早期环境背景。
2. `RESOURCE-EXTENSION.md`：阶段 B1 的资源导入协议、平台边界及后续 B2 路线。原 `CLEANUP-PLAN.md` 已由用户删除，不需要恢复。
3. `DELIVERY-MANIFEST.json`：交付和验证状态；历史产物是否还在，以本次 inventory 为准。
4. `MCM-FIX-1.0.5.md`、`RUNBOOK.md`：最近修复与构建命令。RUNBOOK 中较早版本记录属于历史。

## 可直接复制到新对话

```text
继续开发 <legacy-workspace> 的鸿蒙 TeXstudio 项目。
先阅读 START-HERE.md、RESOURCE-EXTENSION.md、DEVELOPMENT-HANDOFF.md 和 DELIVERY-MANIFEST.json。
当前应用是 1.0.32 完整版（先读 AI-WORKBENCH-1.0.32.md；CLI 帮助见 CLI-HELP-1.0.27.md；文档重载见 RELOAD-CLI-1.0.29.md），运行包为 1.0.30，界面改动和真机验收边界先读 UI-POLISH-1.0.22.md，资源包为 2025.2 加已校验 Lua 子集，pdfTeX/XeTeX 基线是 1.0.5，LuaHBTeX 为 1.21.0；B1 证据见 RESOURCE-EXTENSION.md，B2.1 用户层与 HiShell 私有资源同步说明见 USER-RESOURCES.md，不要重新从零移植。
阶段 A、B2.2/B2.3 和 B2.4 已完成。阅读 COMMON-RESOURCES-B24.md：中文 Beamer、PGFPlots、newpx、BibTeX 多轮编译已真机验证；44 条字体映射仍隔离，不是桌面 TeX Live 全功能移植。
B3.1 Perl + latexmk 自动多轮构建及工作目录修复已真机验收，见 LATEXMK-B31.md。1.0.17 已修复取消状态和 locale，见 LATEXMK-POLISH-1.0.17.md。B3.2 已锁定 107 个 CPAN 发行包、完成 17 个原生模块和 Biber 2.21 组装；45 项直接依赖及实际文献工作流已在 OHOS/QEMU 通过。1.0.19 已签名安装并通过 B319 真机验收，消除了 Biber 启动及 xdvipdfmx 配置/字体映射警告，应用预览和运行中取消正常。详见 BIBER-POLISH-1.0.19.md；远程 HTTPS 不在已验收范围。B3.3 LuaHBTeX/LuaLaTeX 已在 1.0.20 签名安装并完成真机验收，见 LUAHBTEX-B33.md；后续扩展 Lua 宏包和真实项目覆盖，其他原生工具单独审核。不要重复构建或覆盖已签名交付包。旧 1.0.12 精简包不支持 runtime-extension-v2；精简构建需新版源码与新版本号。
Windows 源码和 WSL 构建源码是两个目录；增量同步需要修改的文件，保留未提交修复和有效签名配置，不要动其他 DevEco 项目。
清理清单只作参考，不要把未审查的目录当垃圾删除。已有编译、打包、本机测试和项目签名授权；不需要反复询问同一授权。
最终功能必须在鸿蒙真机验证；宿主编译成功和二进制存在都不能替代真机验收。
```

无需把完整历史聊天或账号密码复制到新对话。
