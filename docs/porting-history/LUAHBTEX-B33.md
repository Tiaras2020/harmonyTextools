> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# B3.3 LuaHBTeX / LuaLaTeX 移植

2026-09-21：1.0.20 默认完整版已签名安装，B3.3 范围内真机验收完成。签名包：`artifacts/TeXstudioHarmony-1.0.20-arm64-device-signed.hap`；公共运行包：`artifacts/texlive-1.0.20.hnp`；校验和：`artifacts/SHA256SUMS-1.0.20.txt`。

## 已实现

- 独立交叉编译 TeX Live 2025 LuaHBTeX 1.21.0（development id 7667），复用已交付 OHOS HarfBuzz、Graphite、zlib 和 C++ 运行库。
- 修复 Lua 格式文件的 fdsan 所有权冲突：zlib 只关闭 `dup` 得到的描述符，原 `FILE*` 由 `fclose` 释放；打开失败回收两类句柄。
- 从锁定的 TL2025 final 元数据提取并校验 Lua 字体加载、LuaTeX-ja、中文字距和 CTEX Lua 资源。没有开放整个 collection-luatex，也没有引入其他平台二进制。
- 应用环境增加 Lua 宏包/模块搜索路径，将字体缓存放在随用户字体修订号变化的 `TEXMFVAR` 内；保持 Kpathsea 输出访问限制。
- 新增自动构建并预览 LuaLaTeX 菜单，复用 latexmk 的进程组取消机制。

## 当前验证

OHOS ARM64/QEMU 已通过引擎启动、格式生成、HarfBuzz 英文 PDF、Lua 执行、Fandol 中文混排与两轮交叉引用。两份 PDF 已渲染检查；英文 4 个、中文 10 个字体全部嵌入。证据：`validation/luahbtex/qemu/`。

应用资源环境真实 Kpathsea 搜索及字体修订缓存隔离通过：`validation/luahbtex/app-env-result.json`。

新 LuaLaTeX 格式从冻结资源中的 `latex.ltx` 生成，实际报告 `LaTeX2e <2025-11-01>`、L3 `2026-01-19`。旧 pdfTeX/XeTeX 二进制和格式保留，不能把旧格式记录的内核版本直接套到新 Lua 格式。

## 构建与续接

先 source `build-support/env.sh`，再在 WSL 运行：

1. `build-support/build-luahbtex.py`：独立目录 `build/luahbtex-ohos`。
2. `build-support/prepare-luahbtex-resources.py`：读取 `validation/luahbtex/archives` 的锁定归档，生成资源清单。
3. `build-support/test-luahbtex.py`：完整 QEMU 测试；`--reuse-format` 仅用于同一引擎的调试续跑。
4. `build-support/prepare-lua-release-perl.py` 和生成的 `validation/luahbtex/perl/build.sh`：独立重建 1.0.20 前缀。Time::HiRes 明确报告 Makefile rebuilt 时仅重跑一次。
5. `build-support/test-lua-release-biber.sh`：新前缀的 45 项依赖和文献工作流回归。
6. `build-support/package-resource-release.sh`：应用、独立候选、HNP/HAP。若候选目录已经存在，应检查状态，不覆盖现有产物。

资源和运行时测试输出位于 `validation/luahbtex/`。真机输入由 `prepare-luahbtex-device.py` 生成在 `device-input/B3320`，通过 HiShell 执行其中 `run.sh`；HDC 裸命令执行不能替代公共 HNP 场景。设备 HOME 已实测为 `/storage/Users/currentUser`。

## 真机验收与使用

HiShell 可直接执行 `lualatex main.tex` 或 `latexmk -lualatex main.tex`，无需为内置宏包另设资源路径。公共 HNP 新增 `luahbtex`、`lualatex` 两个入口，共 17 个入口。默认字体缓存实测写入 `/storage/Users/currentUser/.texstudio/luahbtex-1.21`；应用使用自己的可写缓存。应用私有用户资源仍需按 `USER-RESOURCES.md` 导出同步，才可供 HiShell 使用。

应用中选择“工具 → 自动构建并预览（LuaLaTeX）”。真机测试通过中文/英文/数学混排、Lua 执行、HarfBuzz 字形处理、Biber 中文文献、无改动增量构建、修改文献后重建、中文和空格路径。应用自动预览通过；停止编译后 latexmk、Shell、LuaLaTeX 同组进程全部退出，随后新文档仍能自动构建和预览。

五份真机 PDF 均已渲染检查，字体全部嵌入（HarfBuzz 样例 1 个，其余各 11 个），最终日志没有缺字、未解析引用或字体缓存错误。机器可读结论：`validation/luahbtex/device-result.json`；屏幕证据：`validation/luahbtex/device/lua-app-complete.png`、`lua-cancelled.png`、`lua-recovery-status.png`。

版本前缀更新后，Perl/Biber 的 45 项依赖和文献错误恢复工作流通过 OHOS/QEMU 回归。载荷审计确认单独重建的 Perl 层以外，111,941 个旧基线文件保持一致；原有 pdfTeX/XeTeX 二进制与格式保留。证据：`validation/luahbtex/payload-check.json`、`validation/luahbtex/perl/`。源码快照：`validation/luahbtex/source-1.0.20/SHA256SUMS.txt`。

## 后续范围

本次加入九个经过锁定校验的 Lua 相关资源包，合并新增 254 个文件。尚未验证整个 `collection-luatex`、ConTeXt、所有外部 Lua 原生模块或全部桌面 TeX Live 功能。下一步宜增加实际论文模板、用户字体与用户 Lua 宏包的真机覆盖，再逐包开放更多资源；其他原生工具另行移植与验收。
