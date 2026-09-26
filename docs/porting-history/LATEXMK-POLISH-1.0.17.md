> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# B3.1 收尾：取消状态与 UTF-8 locale

当前交付 **1.0.17 默认完整版，已签名安装并通过本阶段真机验收**（2026-09-17）。

## 改动

停止按钮调用独立的 `ProcessX::cancel()`，只对正在运行的进程记录用户取消，再沿用进程组终止逻辑。取消后显示“已取消编译”，不显示由 SIGKILL 引起的“命令崩溃”，也不弹出误导性的“无法启动”提示。超时仍调用 `kill()`，真实启动失败、编译错误、崩溃仍保留错误状态。调度器检测到取消后终止当前命令链，不再继续预览或重跑；不改变原始进程退出码。

Perl 的 locale 故障并非设备不支持 UTF-8。使用设备 libc 的原生探针确认，OHOS `LC_ALL` 使用 12 个分号分隔的有序值；perl-cross 默认声明 glibc 的名称/值形式。Perl 将六项未启用的可选类别恢复为 C 时生成错误格式，导致整个初始化失败。1.0.17 明确指定 OHOS 的分隔符和类别顺序，保持标准 UTF-8 类别及混合 locale 往返。不设置 `PERL_BADLANG=0`，也不强制覆盖应用或 HiShell 的 LANG/LC_ALL。

Perl 已按新 HNP 安装路径重编译。冻结 TeX 引擎/内核和 2025.2 完整资源方案保持原有发布策略。

## 已通过的开发验证

- OHOS Perl + 设备 libc 的 QEMU 执行：基础文件读写、Unicode、正则、归一化、摘要、路径、时间与 latexmk 启动。
- C、C.UTF-8、en_US.UTF-8：有效类别、UTF-8 代码集、混合 locale 保存恢复、中文空格文件名和 UTF-8 内容读写；stderr 均为空。
- 原有 11 项 Cwd 路径测试，以及启动参数、退出码、应用进程组保护和编译子进程组终止测试。
- 宿主四组 Beamer、PGFPlots、newpx、BibTeX 自动构建、增量跳过、文献更新、故障恢复回归。

证据目录：`validation/latexmk`。Biber 的后续依赖检查见 `BIBER-B32.md`，Biber 本身未加入 1.0.17。

## 真机验收记录

结果：`validation/latexmk/device-result-1.0.17.json`，`passed: true`。

- HiShell：三种 locale、中文空格文件读写、四组文档自动多轮与增量编译、文献修改、错误恢复、子目录切换全部通过。未设置 TeX/Perl 资源覆盖变量，测试日志中无 locale 回退或未初始化路径警告。
- 应用：XeLaTeX 中文 Beamer 三页预览，以及取消和真实错误之后的 pdfLaTeX newpx 自动构建及预览通过。
- 取消：界面显示“已取消编译”，没有崩溃提示；latexmk 29864、shell 29874、pdflatex 29875 均退出，应用 24917 存活，后续命令链终止。
- 故意包含未定义命令的文档仍显示“出现错误”并标注正确错误行，没有误报为取消。
- 回收七份 PDF，字体均嵌入；108,647 个基线文件保持一致。

界面截图：`b317-xe.png`、`b317-cancel.png`、`b317-error.png`、`b317-error-message.png`、`b317-recovered.png`，位于 `validation/latexmk`。

预览超时和外部崩溃未在本轮单独注入真机测试；源码中它们继续走与用户取消分离的 kill/error 路径。本轮不是所有引擎和第三方工具的全面认证。

## 交付文件

- `artifacts/TeXstudioHarmony-1.0.17-arm64-device-signed.hap`：1,434,590,091 字节，SHA256 `cfaf19803f6edc5e1dad8da95a57331c697544028ca8d36c2498a74fe1d21360`。
- `artifacts/texlive-1.0.17.hnp`：1,357,969,580 字节，SHA256 `4e069e84184bb443b2f60abf47bd8eaea727fef5a5de240c335edd60dd2a53c1`。
- 版本前缀：`/data/service/hnp/texlive.org/texlive_1.0.17`。后续更改版本必须重编译 Perl。

最终命令链修复只重建应用壳，HNP 未改变；早期未签名应用壳保留于 `validation/latexmk/repack-1.0.17/before-command-chain-fix.hap`，不作为交付。完整性与签名检查分别见 `artifacts/package-check-1.0.17.json` 和 `validation/device-signing-1.0.17/result.json`。后者的 installed=false 仅表示签名步骤自身未执行安装，实际安装与验收结果在上述 device-result 中。
