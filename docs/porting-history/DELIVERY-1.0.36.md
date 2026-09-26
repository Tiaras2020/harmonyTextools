> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# TeXstudio Harmony 1.0.36 阶段交付

状态：**带已知问题收尾，保留当前版本，停止字体修复。** 用户反馈 1.0.36 的字体粗细仍不自然，此问题未解决。本文不表示无缺陷发布或全量验收通过。

## 当前交付件

所有路径相对于 `<legacy-workspace>`。

| 项目 | 路径 / 状态 |
|---|---|
| 平板安装包 | `artifacts/TeXstudioHarmony-1.0.36-arm64-device-signed.hap` |
| 安装包大小 | 1,494,567,624 字节 |
| SHA256 | `51e07585d7a8a038a1cafeede05d1c5e94fb4c8b4de54f3ac459a9642d91083d` |
| 内置运行包 | 1.0.30；独立文件 `artifacts/texlive-1.0.30.hnp`，HAP 已包含它，日常安装不需再次安装独立 HNP |
| 安装状态 | 上轮已安装到设备 6UZ0226107000081；本次整理没有重装 |
| 当前文件实存、大小、哈希 | `handoff/release-1.0.36/current-delivery.json` |
| 签名记录 | `validation/device-signing-1.0.36/result.json` |
| 安装与验证范围 | `validation/workbench-1.0.36/device-result.json` |

本次重新计算了当前 15 项关键文件的哈希；签名包与签名记录一致，所记录的源码哈希与最后一次构建一致。这是文件交付核对，不是功能测试。

历史 `README/DELIVERY-MANIFEST.json` 的 artifacts 列表含已删除文件，不能用作实存清单。本次单独生成 `handoff/release-1.0.36/historical-artifact-existence.json`，记录 37 项当前不存在的历史条目；不恢复、不删除、不把它们计入当前交付。

## 本阶段功能入口

- TeX 编辑、内置 PDF、离线完整版运行资源、用户资源和 HiShell/CLI 等既有能力，继续以各阶段文档的已测范围为准。
- AI 工程绑定、文件工具、日志/PDF 页图、可选 Shell、回收删除及置顶窗口：`AI-UX-1.0.33.md`。
- 顶部工程/会话标签、半透明导航、图标和中文按钮：`AI-LAYOUT-1.0.34.md`。
- 常用 Markdown、字号设置、可调输入区、紧凑工具记录：`AI-TYPOGRAPHY-1.0.35.md`。
- 对话重命名、私有会话文件位置、上下文机制：`AI-SESSIONS-1.0.36.md`。

## 已知问题与验证边界

1. **FONT-WEIGHT-001：未解决，用户要求暂不继续修复。** 中英文/部分界面字重不自然；1.0.36 调整 AI 字体继承后，用户仍确认存在。没有逐字形确认所有页面的字体回退，因此不要把推测记录成根因。
2. **AI-CONTEXT-001：没有自动上下文压缩。** JSON 请求限制为 400,000 字节；启用视觉时 4 MiB。不是 token 预算，超过限制需要新对话。
3. Markdown 是适配 Qt 5.12 的常用语法子集，不是完整 CommonMark；聊天内没有数学公式排版，也不自动加载远程图片。
4. 1.0.34–1.0.36 按用户要求只构建、签名、安装，未运行功能测试；不能套用 1.0.33 的限定测试结果作为新版本全部功能验收。
5. 真实视觉模型质量、长会话/弱网耐久和全量 TeX 兼容性不在本次收尾验收内。既有关闭文档等被用户延后的问题仍按原记录保留，不因收尾而标为修复。
6. Shell 默认关闭，开启后是应用权限范围，不是工程文件系统沙箱。删除文件工具的回收行为与任意 Shell 命令不同。

## 源码与后续开发

- 主源码：`texstudio-harmony/`。真实版本来源：`texstudio-harmony/release.json`。
- TeXstudio 源码：`texstudio-harmony/third_party/texstudio/src/`。AI 核心为 `harmonyaiworkbench.h`、`harmonyaitools.h`、`harmonymarkdown.h`；校对为 `harmonyproofpanel.h`；应用集成在 `texstudio.cpp`。
- 本机实际构建/打包支持：`build-support/`，不是可直接搬到 CI 的通用脚本集合。
- 当前主仓库及 TeXstudio 子仓库存在未提交改动；状态记录在 `handoff/release-1.0.36/*-git-status.txt`。**直接推送现有提交不会包含所有当前开发成果。** 本次未自动提交或推送。
- 不要重复运行 `upgrade-*`、`integrate-*`、`adjust-*`、`title-menu36.py` 等一次性变更脚本；它们是实施记录，不是构建入口。

现有增量构建链路（仅供后续开发，收尾未重跑）：

1. 修改 release.json 并递增应用版本；同步 `build-workbench.sh`、`assemble-workbench-package.py` 中对应版本输出路径，保持旧交付件。
2. WSL：`bash /mnt/e/CodeProjects/harmonytexlive/build-support/build-workbench.sh`，使用 Ubuntu-24.04 内现有依赖和增量构建目录。
3. Windows：`python build-support/assemble-workbench-package.py`；目标 HAP 已存在时脚本会拒绝覆盖，应使用新版本路径。
4. Windows：`python build-support/sign-with-deveco.py --version <新版本>`，使用本机私有签名材料。
5. 经所需验收后用 HDC 安装，将新版本的范围、哈希与结果另行归档。

当前 WSL 工程：`/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915`。SDK 等位置由 `build-support/env.sh` 指定。

## GitHub 与磁盘整理边界

本次只整理入口、实存清单、状态和交接说明，**没有删除/移动大型文件、制作完整恢复备份、上传 GitHub 或清理 WSL**。

后续发布前需要：收敛主仓库/子仓库未提交变更；收录 build-support 中必要构建逻辑；排除签名配置、证书私钥、设备/个人项目日志和本机路径；大体积 HAP/HNP 放发布附件而非普通 Git 历史。当前构建配置含本机签名材料引用，不要整个目录直接公开。

**WSL 暂不具备可直接完全清除的条件。** 当前构建依赖现有 WSL 安装库、构建产物和历史组装路径，尚未完成干净环境重建。原评估见 `PROJECT-STORAGE-AND-GITHUB-PLAN.md`；其中磁盘容量和版本是历史测量，不代表现在。

下一阶段若开始 GitHub 整理，应先完成可恢复源码与构建依赖的归档及干净构建验证，再决定清理范围。
