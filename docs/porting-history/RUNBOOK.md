> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 本机继续构建与设备验收

> 阶段 A 后以 `BASELINE-AUDIT.md` 的命令为准。版本唯一来源为 `texstudio-harmony/release.json`，生成配置后单向同步到 WSL。旧 `build-*-fix.sh` 迁移脚本已经加保护，不能直接重放；历史 1.0.0 命令不作为当前交付入口。

> 当前交接入口：`START-HERE.md` 和 `DEVELOPMENT-HANDOFF.md`。当前基线为 1.0.5，用户已反馈最近项目编译和宏包悬停问题解决。下面 1.0.0 等章节属于历史记录；不要按旧版本号重新交付。清理候选见 `CLEANUP-PLAN.md`，本次未删除文件。

## 1. 使用本次现成构建目录

在 Windows 终端进入 WSL：

```powershell
wsl -d Ubuntu-24.04
```

在 WSL 中加载环境：

```bash
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
```

构建产物、完整源码和缓存保存在此 Linux 目录。Windows 可编辑副本在 `<legacy-workspace>\texstudio-harmony`。两个目录不是同一个目录；编辑 Windows 源码后需同步对应文件再重新编译。

## 2. 按需执行构建步骤

以下脚本都在 `<legacy-workspace>\build-support`，从 WSL 用 `bash` 执行对应路径。

| 脚本 | 用途 |
| --- | --- |
| `env.sh` | 本机 SDK、Java、Linux PATH、并行数和目录配置 |
| `prepare.sh` | 从 Windows 源码准备 Linux 工作副本；不覆盖已有 build 目录 |
| `resume-qt.sh` | Qt 增量编译和安装 |
| `resume-host.sh` | TeX Live 宿主工具增量编译和检查 |
| `build-poppler.sh` | 安装 Qt 基础模块并构建 Poppler |
| `build-texstudio.sh` | 安装所需 Qt 模块并构建 TeXstudio |
| `build-tex-ohos.sh` | 重建 TeX Live ARM64 目标目录，然后收集引擎 |
| `prefetch-texmf.sh` | 下载并校验 TeX Live 2025 宏包缓存 |
| `package-texmf.sh` | 装配资源、生成格式文件并检查 ELF |
| `validate-texmf-host.sh` | 用宿主引擎验证交付资源及中英文样例 |
| `package-hnp.sh` | 创建未签名 TeX Live HNP |
| `package-hap.sh` | 集成动态库并创建未签名 HAP 基础包 |
| `finalize-packages.sh` | 将 HNP 加入 HAP，导出交付文件并验证 |
| `sync-source.sh` | 将 Linux 工作副本的主项目修复同步回 Windows；不覆盖子模块 Git 数据 |

`build-tex-ohos.sh` 调用上游脚本，会删除并重新创建本次 TeX 目标构建目录；需要增量调试时应直接进入对应 build 目录执行 make。

如果修改 Qt/TeXstudio/Poppler，重新执行对应构建步骤，再执行 `package-hap.sh`、`finalize-packages.sh`。如果修改 TeX 引擎或宏包，则重新执行相关构建及 `package-texmf.sh`、验证、`package-hnp.sh`、`finalize-packages.sh`。

不要执行上游 `scripts/common/sign/sign_push.sh`：它包含签名和向设备安装的步骤，本次未使用。

## 3. 已完成的设备调试签名（2026-09-15）

安装时使用 `artifacts/TeXstudioHarmony-1.0.0-arm64-device-signed.hap`。它已包含 TeX Live HNP，并使用 DevEco Studio 为 `com.ohos.texstudio` 生成的开发者签名材料完成签名。

官方 SDK 的 HAP 签名、代码签名、Profile 验证均通过；Profile 内唯一授权设备与当前通过 hdc 连接的设备一致。Profile 到期时间为 2027-09-15 13:37:11 UTC。签名只适用于获授权设备，尚未进行设备安装和运行验证。

无需再单独签名或替换内部 HNP；不要修改已签名 HAP 的内容。此前未签名的 HAP、独立 HNP 仍保留用于重建。测试证书产物 `TEST-ONLY-DO-NOT-INSTALL.hap` 不是安装交付件。

验证摘要见 `validation/device-signing/result.json` 与 `device-profile-check.json`。重新签名脚本为 `build-support/sign-with-deveco.py`，从当前 TeXstudio 工程读取 DevEco 配置，不输出明文密钥库密码。该脚本为避免覆盖签名交付件，在输出已存在时会停止。

## 4. 真机最小验收

1. 签名并安装 HAP，确认 TeXstudio 可以启动、显示界面且不闪退。
2. 从 `validation/` 复制 `pdflatex-basic.tex` 和 `xelatex-cjk.tex` 到设备上可读写的文档目录。
3. 用 pdfLaTeX 编译英文样例并在内置预览中打开 PDF。
4. 用 XeLaTeX 编译中文样例两次，检查中文、公式和“第 3 节”的交叉引用。
5. 修改正文、保存、重新编译，确认输出更新。
6. 如失败，保留系统版本、签名工具结果、安装错误、TeXstudio 编译输出和相关日志；这些信息用于下一轮修复。

TeXstudio 的命令名通常可以使用 `pdflatex` 和 `xelatex`。HNP 导出的公共入口由系统安装器管理；实际设备路径和沙箱行为以设备测试为准。

本次验收目标是编辑、英文/中文排版和 PDF 预览。LuaLaTeX 支持另行验证，详见 BUILD-REPORT.md。
# 最新交付：1.0.5 MCM 项目与宏包提示修复

当前请使用 `artifacts/TeXstudioHarmony-1.0.5-arm64-device-signed.hap`。说明见 `MCM-FIX-1.0.5.md`。新增 MCM 项目宏包/字体依赖、虚拟字体路径与 ls-R 宏包索引，保留此前中文预览修复。宿主机完整项目验证为 17 页；用户后续反馈最近项目编译和宏包悬停问题已解决。本次整理没有重跑真机测试，其他未移植工具仍未验收。前文保留原构建流程记录。
