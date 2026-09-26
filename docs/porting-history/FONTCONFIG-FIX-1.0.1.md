> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.1：XeLaTeX 字体配置修复

## 设备反馈

用户确认 1.0.0 的英文 pdfTeX 编译成功。中文 XeLaTeX 截图显示 `Fontconfig error: Cannot load default config file` 和 `internal error; cannot read font names`。

## 改动

- 在 TeXstudio 启动引擎的两个入口共享字体环境配置逻辑，显式传递 `FONTCONFIG_FILE`。
- 在应用自身的缓存目录生成 Fontconfig 配置，使用 HNP 内 OpenType/TrueType 字体的绝对路径及 `/system/fonts`，缓存同样放在应用可写目录。避免继承构建机器的默认配置和工作目录相关的字体路径。
- 将 `TEXMF` 和 `TEXMFDIST` 指向本次实际交付的 `texmf` 目录。
- 独立 ExecProgram 启动时保留系统环境，防止覆盖 PATH 等必要变量。
- HAP 版本升级为 1.0.1（1000001）。HNP 内容及版本不变；修复由应用在启动引擎前生效。

## 已验证

- ARM64 TeXstudio 编译和 Hvigor HAP 打包通过。
- 宿主环境采用同样的绝对字体目录配置，发现 121 个字体条目，全部来自交付的 texmf；测试没有借用宿主系统字体目录。
- 同源宿主 XeLaTeX 连续编译中文样例两次成功；公式、中文和第 3 节引用已检查 PDF 页面。英文 pdfLaTeX 回归通过。
- 真实开发者证书签名、完整 HAP/HNP 代码签名验签、Profile 验证通过。当前连接设备匹配 Profile 的唯一授权设备。
- 新 HAP 内所有原始条目与签名前内容一致；内嵌 HNP 与 1.0.0 完全相同。

宿主测试不能替代 HarmonyOS 应用沙箱内的验证。尚未安装新包，设备端 XeLaTeX 是否恢复需复测。

## 交付和复测

安装 `artifacts/TeXstudioHarmony-1.0.1-arm64-device-signed.hap`，在 HoKit 选择“仅安装”进行覆盖更新。关闭后重新打开 TeXstudio，再用 XeLaTeX 编译 `xelatex-cjk.tex` 两次。旧 1.0.0 安装包保留。

SHA256：`3a4ba7915c355462cdc6a78b3d446122d2ff9f6e64e4534317e0fd86fe8920e2`。

日志与结果：`logs/fontconfig-fix-build.log`、`logs/fontconfig-fix-package.log`、`validation/fontconfig-fix/`、`validation/device-signing-1.0.1/`。
