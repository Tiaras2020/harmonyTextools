> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# XeLaTeX ICU 数据路径修复：1.0.2

## 原因与修改

用户确认 1.0.1 中文编译仍输出 `internal error; cannot read font names`。XeTeX 的 `XeTeXFontMgr_FC::initialize()` 在 ICU 转换器初始化出错时向 stderr 输出该消息并退出，因而 TeX 日志可能仅停在 `size10.clo` 的基础字体初始化位置。

HNP 使用 ICU 73.2 的 archive 数据模式。`share/icu/icudt73l.dat` 已随包提供，但 1.0.1 启动代码遗漏 `ICU_DATA`，原有引擎可执行路径初始化又可能被沙箱回退逻辑跳过。

本次在 TeXstudio `setOhosTexEnvironment()` 中显式设置 `ICU_DATA=<已解析的 HNP 根目录>/share/icu`。应用版本更新为 1.0.2；HNP 仍为 1.0.0，其内容未改动，因此设备路径中的 `texlive_1.0.0` 是预期结果。

## 验证

- ARM64 TeXstudio 增量编译与 Hvigor HAP 打包通过。
- 从实际 HNP 提取 ICU 数据，用相同版本的 Linux ICU 73 和空数据占位库测试，避免宿主机内置数据掩盖缺陷。
- 无有效 ICU_DATA 时，`macintosh` 转换器复现 `U_FILE_ACCESS_ERROR`。
- 设置实际包内数据路径后，`macintosh`、`UTF16BE`、`UTF8` 均返回 `U_ZERO_ERROR`。
- 完整 HAP 的代码签名、签名验证、授权文件验证通过，当前连接设备与授权设备匹配。
- 签名包的版本号、更新后的 libtexstudio.so 及 ICU_DATA 路径字符串已核验。

转换器验证结果见 `validation/icu-fix/missing-data.json` 和 `with-data.json`；签名结果见 `validation/device-signing-1.0.2/`。

这些是宿主机组件验证与安装包检查，尚未证明修复包在鸿蒙应用沙箱内完成中文排版。

## 交付及设备复测

已签名文件：`artifacts/TeXstudioHarmony-1.0.2-arm64-device-signed.hap`

SHA256：`1fcefce8a8563deb9eb696c352cb0b1d659d76251c7f5d34c0e01a784c5b7a93`

覆盖安装后完全退出并重新打开 TeXstudio，用 XeLaTeX 编译 `xelatex-cjk.tex` 两次，检查中文、公式与交叉引用。若仍失败，保留底部消息和新的 .log。

本次交付尚未安装到设备；先前定位的格式文件句柄 fdsan 问题未包含在此修复中。
