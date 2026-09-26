> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 阶段 A：版本、依赖与回归基线

本次保留可安装基线 1.0.5。用户主动删除的清理文档、示例 ZIP 和旧交付件没有恢复。现有签名 HAP、HNP 的 SHA256 与原交接记录完全一致。

## 已落实

1. `texstudio-harmony/release.json` 成为版本与兼容配置的唯一来源。HNP、HAP 组装、签名默认值、C++ 运行目录和生成的应用版本都接入该配置。删除最终打包默认回落到 1.0.0 的行为；环境变量冲突、生成文件过期和 HAP/HNP 版本不一致会失败。交付组装拒绝覆盖同版本既有产物。
2. `texstudio-harmony/dependencies.lock.json` 冻结 152 个归档（150 个资源归档及 TeX Live、Qt 源码归档）、16,653 个运行文件、TeX 构建配置和关键引擎源文件的 SHA256。下载/解包入口核对归档哈希，缺包或损坏不会继续被当成打包成功。此锁是已用本地内容的审计记录，不代表独立验证了上游供应链签名，也不是完整 TeX Live 的依赖求解器。
3. `validation/baseline/source/` 保存主仓库、TeXstudio 子模块的 HEAD、源码补丁、修改文件 ZIP 和 build-support 脚本快照。签名和机器专用 build-profile 不进入快照，也未修改。未 reset/clean 或自动提交整个脏工作树。
4. Windows 到 WSL 只同步明确列出的文件；每次同步先保存被替换文件及前后哈希。记录位于 `validation/baseline/sync/`。快照范围内的源码最终逐文件比较差异为 0，见 `validation/baseline/source/copy-differences.json`；这不包含有意排除的机器配置。保留原 dist、SDK 路径和签名配置。
5. 最小回归样例和可重复执行脚本已建立；原始 MCM 测试目录没有被回归运行覆盖。
6. 旧 `build-*-fix.sh` 版本迁移脚本保留历史正文，但入口明确拒绝重放，避免重新执行旧的版本替换。今后修改统一版本配置并按下方流程构建。

## 实际兼容组合

| 对象 | 本轮证据 |
|---|---|
| pdfTeX | 1.40.27，TeX Live 2025；宿主版本输出 |
| XeTeX | 0.999997，TeX Live 2025；宿主版本输出 |
| kpathsea | 6.4.1 |
| 已装载格式内核 | `LaTeX2e <2026-06-01> pre-release-1 (develop 2026-9-15 branch)`；本轮三组编译日志 |
| L3 层 | 2026-01-19 |
| biblatex | 3.21；归档包元数据 |
| Biber | 尚未移植与验收，不标记任何 Biber/biblatex 运行组合已通过 |
| Qt | 5.12.12 Harmony 源码归档，固定实际归档 SHA256 |

`latex/base/latex.ltx` 和 `latex-dev/base/latex.ltx` 都与其归档文件一致，但**当前格式实际包含开发内核**。因此本轮冻结“可用的现有组合”，没有将其改名为稳定版或静默替换内核。格式、内核、L3、字体映射及资源必须一起审核；后续换稳定内核需重新生成格式，再跑宿主和真机回归。回归脚本会检查当前日志的内核与 L3 标识。

宿主与 ARM64 配置不同：宿主启用 Lua 相关引擎，目标构建禁用主要 Lua 引擎；不能把宿主能力当目标能力。原始配置完整记录在 `validation/baseline/dependency-audit.json`。

## 本轮验证

| 检查 | 结果 |
|---|---|
| 依赖锁前后复核 | 通过，运行 dist 未变更 |
| 版本变更及过期文件检测 | 在独立测试副本用 1.0.6 验证通过；正式配置仍为 1.0.5 |
| 冲突 PACKAGE_VERSION | 正确拒绝 |
| Python 语法、Shell 语法 | 通过 |
| TeXstudio ARM64 增量构建 | 通过；只构建，未重新打包交付 |
| pdfLaTeX 英文 | 1 页，9 种字体全部嵌入 |
| XeLaTeX 中文、中文和空格路径 | 两次编译通过，1 页，14 种字体全部嵌入，交叉引用正确 |
| MCM | 三次编译通过，17 页，14 种字体全部嵌入 |
| recorder 输入隔离 | 三组均未读取测试目录与交付 texmf 之外的 TeX 输入 |
| Fontconfig | 154 个字体面，均来自交付资源 |
| 同版本 Poppler 中文渲染 | 已有设备 PDF 在指定交付 Poppler 数据下渲染通过，无缺失语言包/未知字体错误 |
| 视觉复核 | 检查中文页、Poppler 渲染页及 19 页总览；MCM 原有 LastPage 等警告仍保留 |

结果入口：`validation/baseline/regression/result.json`、`windows-checks.json`、`lock-verification.json`、`texstudio-build.log`、`preview/render.log`。宿主回归不是当前应用沙箱的真机自动化验收。

## fdsan 独立修复的边界

增加 `scripts/texlive/patches/harmony_dump_io.h` 和精确上下文补丁脚本，接入下一次 ARM64 TeX 引擎构建。处理方式为：复制文件描述符，关闭原 FILE，再把新的描述符交给 zlib；对 dup、fclose、gzdopen、gzsetparams 失败分别释放资源。没有关闭 fdsan。

- C 与 C++ 宿主测试：200 次压缩写入/读回及四类失败注入通过，未发生描述符泄漏。
- ARM64 探针编译通过；补丁在隔离源文件上连续应用两次通过。
- 设备连接正常，但执行推送到临时目录的原生探针返回 `Permission denied`。未绕过设备执行策略。
- **尚未重新构建并安装包含该补丁的 TeX 引擎；现有 1.0.5 HAP/HNP 和运行 dist 保持原样。fdsan 的应用内真机关闭项仍未完成。** 后续应随新版本签名 HAP 验证格式读入、格式生成和异常清理，不能仅以该单元探针代替引擎验收。

## 日常复核命令

Windows 项目根目录：

```powershell
python texstudio-harmony/scripts/release_config.py
wsl -d Ubuntu-24.04 -- bash /mnt/e/CodeProjects/harmonytexlive/build-support/run-baseline.sh
wsl -d Ubuntu-24.04 -- bash /mnt/e/CodeProjects/harmonytexlive/build-support/check-preview-baseline.sh
python build-support/verify-baseline-windows.py
```

回归脚本优先使用 WSL 的 `pdfinfo`/`pdffonts`，本机缺失时使用已检测的 Windows 工具。路径写在 `regress-baseline.py` 中；换机器需调整。Windows 渲染检查需要 PyMuPDF、Pillow。

## 下一次修改版本

1. 编辑 `texstudio-harmony/release.json` 的 `version` 和递增的 `versionCode`。资源变化时同时审核兼容标识，不能仅改版本号绕过锁。
2. 执行 `python texstudio-harmony/scripts/release_config.py --write` 生成头文件和 AppScope 版本。
3. 通过 `sync-baseline.py` 做有备份的单向同步。`check-baseline-build.sh` 会完成该同步和 TeXstudio 增量构建。
4. 根据修改范围重新构建引擎或资源。`build_texlive_ohos.sh` 会重建目标构建目录，不应当作普通增量编译命令。
5. 新版本必须更新资源中的 `texmf.cnf` 安装根目录并验证。资源重新打包脚本现在从统一版本配置生成该值；不要直接对旧 dist 组装新版本 HNP。
6. 重新跑完整回归，审核后显式更新依赖锁；锁检查默认不会自动接受新哈希。
7. 依次打包 HNP、HAP、运行 `finalize-packages.py`，再运行 `sign-with-deveco.py`。不再需要手动导出 PACKAGE_VERSION；版本冲突会报错。同名交付件不会被覆盖。

进入阶段 B 前可使用本次冻结基线。资源管理开发不能将此版本的格式、字体缓存或内核无条件复用于其他资源组合。
