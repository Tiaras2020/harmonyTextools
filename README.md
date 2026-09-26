# harmonyTextools

面向 HarmonyOS 平板/二合一设备的本地 LaTeX 工作环境：TeXstudio 编辑器、内置 PDF 预览和离线 TeX Live 运行资源，并集成工程 CLI、用户资源管理和可选在线 AI 对话。

当前交付：**应用 1.0.36 / TeX 运行包 1.0.30 / arm64-v8a**。本仓库是上游 TeXstudio Harmony 移植版本的继续开发快照，包含改过的第三方源码，不是 TeXstudio 官方发行版。

## 先选你的用途

- **安装使用**：[Releases](https://github.com/Tiaras2020/harmonyTextools/releases/tag/v1.0.36) → 下载签名 HAP。包内已有运行资源，无须再装单独 HNP。该包使用原测试设备的开发签名，**不能承诺任意设备直接安装**；其他设备按[签名说明](docs/SIGNING.md)自行签名。
- **学习功能**：[功能与使用](docs/FEATURES.md)、[CLI 与 AI](docs/AUTOMATION.md)。
- **修改代码**：[从 clone 恢复开发](docs/BUILD.md)、[工程架构](docs/ARCHITECTURE.md)。不要直接运行 tools/legacy 下的历史迁移脚本。
- **了解问题与版本**：[已知问题](docs/KNOWN-ISSUES.md)、[更新日志](CHANGELOG.md)、[验收边界](docs/VALIDATION.md)。

## 主要功能

- 本地 TeX 编辑、项目/主文档管理、PDF 预览、SyncTeX 定位。
- 离线 pdfLaTeX、XeLaTeX、LuaLaTeX、latexmk、BibTeX、Biber；宏包和字体有平台兼容边界。
- 预装资源、导入扩展资源和可编辑用户资源层。
- 工程 CLI：帮助、文件/缓冲区状态、刷新、构建、清理重编、日志和诊断。
- 中文词典与手动 LanguageTool 校对；词典与在线校对是两种功能。
- AI 工程对话：读写文本、查看日志/PDF、可选 Shell/回收删除、Markdown、可调字号、置顶窗口、会话管理。

## 重要状态

当前带已知缺陷交付：**字体粗细不自然；CLI 多工程显式主文档后关闭文档可能崩溃；改变应用字号后 AI 上下导航图标可能偏离居中。** 请先读已知问题页。1.0.34–1.0.36 未执行功能回归，安装成功不等于所有能力均已验收。

AI 是调用用户配置的远端服务，不是本地运行大模型；上下文没有自动摘要压缩。Shell 默认关闭，打开后以应用权限运行。

## 源码与恢复附件

Git 中保存应用源码、移植脚本、说明、历史记录和第三方许可；Release 保存较大的预编译依赖、已修改依赖源码及冻结 HNP。**clone 之后还须安装 SDK 并运行恢复脚本下载附件**，Git 本身不包含完整开发 SDK 或所有 TeX 资源。

```bash
git clone https://github.com/Tiaras2020/harmonyTextools.git
cd harmonyTextools
# 按 docs/BUILD.md 安装 SDK、设置 TOOL_HOME，然后：
python3 tools/restore_deps.py
bash tools/build.sh
```

第三方源码已直接收录，不需要 `git submodule update`。迁移后的恢复验证范围见 docs/VALIDATION.md；源码全量重编 Qt/TeX/Biber 是不同于复用冻结依赖的高级工作流。

## 许可与上游

根目录 LICENSE 为工程脚本原有 MIT 许可，**不覆盖所有第三方组件**。TeXstudio、Qt、Poppler、TeX Live、字体和 Perl/Biber 各自许可继续适用。上游来源和对应源码见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 与 docs/UPSTREAM-SOURCES.json。保留了各组件原始版权声明。
