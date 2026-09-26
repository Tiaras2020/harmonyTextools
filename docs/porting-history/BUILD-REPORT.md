> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# TeXstudio Harmony 本机构建记录

构建日期：2026-09-15。目标：鸿蒙 2in1 / ARM64。

## 交付与验收边界

- `artifacts/TeXstudioHarmony-1.0.0-arm64-unsigned.hap`：主应用包，包含 Qt、TeXstudio、Poppler，以及 `hnp/arm64-v8a/texlive.hnp`。
- `artifacts/texlive.hnp`：同一份 TeX Live 原生软件包，单独提供给设备端签名工具。
- 两者均由未配置签名的构建流程生成。本次未调用签名命令、未安装到设备。官方 HAP 校验工具返回 `signature not found` / `No Hap Signing Block`，确认 HAP 尚未签名。
- 已完成交叉编译、未签名应用构建、宏包/格式资源装配、ELF 检查和宿主资源测试。
- 真机启动、文件选择与保存、应用内调用排版引擎、PDF 预览仍需设备签名安装后验收。
- 本机 QEMU 尝试因 SDK 不包含实际动态加载器而未能执行目标程序；不把宿主测试当作 ARM64 真机验证。

## 源码版本

| 组件 | 本次版本 |
| --- | --- |
| texstudio-harmony / main | `a8bfb147dcd173fa378687ae474ad152cd20f597` |
| TeXstudio 子模块 | `efc191c5d66ffcd0ca3b41b05b4f83a279b184ae`，工程版本 4.9.5 |
| Poppler 子模块 | `d1f91ff9b4e26532b4bd3ce09048e236d27039e5` |
| Qt | 5.12.12 鸿蒙快照，20260403 |
| TeX Live 源码 | TeX Live 2025，20250308 源码包 |
| TeX 宏包 | TeX Live 2025 `tlnet-final` 冻结版本，130 个声明包 |
| ICU / HarfBuzz | 73.2 / 7.1.0 |

Qt 源码包 SHA256：`473fd069cbafad0b111701c00a74831abbfec24cb07495bf0d217368307df53a`，与官方下载响应提供的摘要一致。

## 环境

- Windows 11，约 32 GB 物理内存；WSL2 Ubuntu 24.04.4，约 15 GB 可用总内存配置。
- DevEco Studio 6.1.1.280；HarmonyOS SDK 6.1.1.125 / API 24。
- 编译器：SDK Clang 15.0.4；CMake 3.28.2；Ninja 1.12.0；OpenJDK 17。
- HAP 为 debug 构建；目标 API 24，兼容版本声明保留 API 20，架构限定 arm64-v8a。
- API 20 是工程兼容性声明，并非已经在 API 20 真机上验证。设备具体系统版本尚待确认。

实际 Linux 构建目录：

`/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915`

Linux SDK 根目录：

`/home/tiarasubuntu2404/ohos-commandline-tools-6.1.1.280/command-line-tools`

Windows 可编辑源码：

`<legacy-workspace>\texstudio-harmony`

## 本次必要修复

1. 使用纯 Linux PATH，避免配置脚本反复搜索 Windows 挂载目录。
2. 补齐 Java、zip/unzip、CMake/Ninja、字体开发库和宿主 Xaw 开发依赖。
3. 为旧 Qt 脚本提供任务私有的 `python -> python3` 别名，不改系统默认 Python。
4. 限制多数编译步骤为 6 个并行任务。
5. Qt 下载使用同文件镜像并校验官方摘要；bzip2 使用同一官方仓库的 codeload 归档端点。
6. HarfBuzz 的链接参数原先被 SDK 强制覆盖，改用保留的 CMake 标准库参数传入 FreeType 的传递依赖。
7. 依赖框架重复解压 ZIP 时改用非交互覆盖，避免无人值守重试卡住。
8. 修正 TeX 目标构建引用的 Brotli 静态库文件名，使用实际的 `*-static.a`。
9. 固定 TeX Live 2025 的宏包源，避免旧引擎混入滚动升级的宏包。
10. HAP 使用本机 API 24 SDK、ARM64 配置和空签名配置；本次 entry 构建去掉不使用的测试框架下载依赖。
11. 显式携带 C++ 共享运行库，并检查实际动态库依赖。
12. HNP 打包修正 `hnpcli` 名称参数；不导出尚无格式文件的 `lualatex` 入口。

## Lua 的实际情况

原脚本关闭了 LuaTeX、LuaHBTeX、LuaJITTeX，但没有关闭 LuaJITHBTeX。实际构建生成了 ARM64 `luajithbtex`，并保留在 HNP 内；这修正了仅根据前三个禁用选项推断“没有任何 Lua 引擎”的判断。

目前没有准备完整的 LuaLaTeX 资源和 `lualatex.fmt`，因此本次不将其作为已验证功能，也不在 HNP 公共入口列表中导出 `lualatex`。后续可以在现有编译产物基础上继续验证。

## 已执行验证

- Qt 构建与安装完成，安装后的 qmake 报告 5.12.12。
- Poppler 和 TeXstudio 完整构建成功。
- TeX Live 宿主构建完成，pdfTeX 1.40.27、XeTeX 0.999997 能正常启动。
- TeX Live ARM64 目标构建完成。
- 130 个宏包下载成功并通过 XZ 解压完整性检查。
- 生成 `pdflatex.fmt`、`latex.fmt` 和 `xelatex.fmt`。
- 185 个 ELF 文件检查通过：全部为 ARM64；依赖名称在对应包或 API 24 SDK 中可找到。详见 `validation/elf-report.json`。
- 使用同源码版本宿主引擎和交付资源编译英文、中文与数学公式样例；中文样例二次编译后交叉引用解析成功。
- 样例 PDF 已渲染检查，中文、公式和页码可读。样例为宿主资源验证结果。
- 最终 ZIP CRC、包内必需文件、11 个 HNP 公共入口和内嵌 HNP 一致性检查全部通过；详见 `artifacts/package-check.json`。Windows 侧再次计算 SHA256，与构建侧一致。

宿主样例保留普通的数学字体尺寸替代提示；输出已目视核对，不存在缺失中文或未解析交叉引用。

## 日志

`logs/` 保留下载、环境安装、编译、打包和验证日志。日志包含失败的初次尝试以及后续成功重试，应结合末尾成功状态阅读。

关键日志：`qt-build.log`、`texstudio-build.log`、`texlive-host.log`、`texlive-ohos.log`、`texmf-package.log`、`hap-native-build.log`、`hnp-package.log`、`final-package-check.log`。
# 2026-09-15 签名补充

已通过 DevEco Studio 在 `texstudio_harmony` 工程生成真实开发者调试签名材料，并使用同一安装目录下的官方 SDK 签名工具对完整 HAP 签名。输出为 `artifacts/TeXstudioHarmony-1.0.0-arm64-device-signed.hap`（361616220 字节）。

HAP 和内嵌 HNP 的代码签名验签通过；原包 34 个条目的内容保持不变，SDK 添加 `.pages.info`。Profile 验证通过，包名为 `com.ohos.texstudio`，当前设备匹配且授权有效。没有进行设备安装或运行验证。以下原始构建记录中的“未签名”描述对应较早交付阶段。
