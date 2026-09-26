> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# B3.2：Biber 2.21 鸿蒙移植

最新收尾版为 **1.0.19**，已修复本文所述的 1.0.18 启动/配置警告并重新真机验收，见 `BIBER-POLISH-1.0.19.md`。下文保留 1.0.18 基础移植的证据与边界。

2026-09-18：Biber 已完成 OHOS ARM64 静态移植与本地离线工作流真机验收。**1.0.18 默认完整版已签名、安装**，支持应用和 HiShell 自动调用 Biber；保留两项非阻断启动/配置警告，详见下文。证据为 `validation/biber/device-result-1.0.18.json`。

## 版本与实现

冻结 biblatex 3.21 + Biber 2.21，引擎/内核仍为 1.0.5 基线，完整资源为 2025.2。依据官方 [Biber 2.21 Build.PL](https://github.com/plk/biber/blob/v2.21/Build.PL) 和 [biblatex 兼容性表](https://tug.ctan.org/macros/latex2e/contrib/biblatex/doc/biblatex.pdf)。

- Perl 5.40.3 静态注册 17 个第三方原生模块，继续禁用 DynaLoader，未引入桌面 Linux .so。107 个 CPAN 发行包版本、来源、SHA256 见 `validation/biber/dependencies.lock.json`。
- 原生库包括 libxml2 2.15.4、libxslt 1.1.45、btparse 0.91、OpenSSL 3.5.8，均由 OHOS SDK 构建静态库。源归档锁位于 `validation/biber/native/`。
- 补齐 DateTime/Locale、编码表、Lingua::Translit 转写表、AutoLoader 文件及 Biber schema/config。五项许可证元数据 unknown 已根据归档许可声明解决；HNP 保留许可文件和依赖锁，见 `validation/biber/license-audit.json`。
- 公共原生 biber 启动器负责参数原样传递、HNP 路径及 HarmonyCwd 初始化。直接调用时创建进程组；latexmk 嵌套调用时验证并继承父构建进程组，使取消可终止整条命令链。
- 应用与 HiShell 共用公共 HNP 的 biber。用户私有资源仍需显式导出、导入同步。
- 基线逐文件核对：108,647 个冻结文件保持一致，新增 5,358 个运行库和工具文件；只允许安装版本路径、ls-R 变更。见 `validation/biber/payload-check-1.0.18.json`。

## 验证

下表测试使用实际 OHOS ARM64 Perl，通过 QEMU 和设备 libc 执行；启动器参数/进程组回归使用宿主。证据路径均相对于 `validation/biber/`。

| 范围 | 结果和证据 |
| --- | --- |
| 直接依赖 | 45/45 模块加载和最低版本检查通过，无 stderr；`assembled-dependency-audit.json` |
| Biber 处理 | 中文空格路径、中文键/姓名/标题、排序、crossref 继承、BCF/数据模型校验、重复一致、修改重建、错误恢复；`workflow/result.json` |
| 剩余原生模块 | 33 个精选上游测试文件通过，覆盖严格 UTF-8、排序、换行、日期、编码、TLS；`remaining-upstream/result.json` |
| 运行数据 | ISO 9 转写、中文 locale、闰年、GB18030 BMP、UTF-8 扩展汉字、日文编码；`runtime-data-result.json` |
| TLS | 本地 HTTPS：显式信任 CA 成功，主机名错误和未知签发者均被拒绝；`tls/result.json` |
| 启动器 | 中文/空格/元字符参数、直接/嵌套进程组及无效标记；`launcher-result.json` |

第一批 CSV、XML/XSLT、BibTeX 历史上游测试保留于 `xs-bootstrap/`、`native/upstream/`；其解释器哈希和范围在原始 JSON 中，不与最终解释器测试次数混算。

## 限制

- 真机启动时，上游 `use lib $FindBin::RealBin` 产生空路径警告，并引发 Data::Compare 的未初始化路径警告；已测离线构建成功，但不应声称日志无警告。后续在安装版入口移除对沙箱 realpath 的依赖，按新版本重新打包验收。
- HiShell 的 xdvipdfmx 报缺少 dvipdfmx.cfg；本轮两份 PDF 页面正确、各六种字体全部嵌入。后续与启动警告一起收尾。
- 离线本地文献是主要验收范围；QEMU TLS 不等于鸿蒙真机远程 URL/HTTPS 已验收。未关闭证书验证。
- Encode::HanExtra 0.23 上游 GB18030 表不能表示 U+20000，扩展汉字使用 UTF-8。
- Unicode::LineBreak 使用 Sombok 2.4.0 / Unicode 8.0.0 表，未启用 libthai。XML 的 Python、ICU、iconv、压缩以及 XSLT crypto 等可选功能未开启。
- 未穷尽 Biber 全部选项与文献组合；LuaHBTeX/LuaLaTeX 仍待独立移植。

## 复现

前提：锁定的 Perl/perl-cross、107 个 CPAN、Biber 源归档，设备 libc/QEMU 根目录和 OHOS SDK。Windows 与 WSL 源码目录独立，按 sync-baseline.py 精确同步。

```bash
bash /mnt/e/CodeProjects/harmonytexlive/build-support/build-biber-runtime.sh
bash /mnt/e/CodeProjects/harmonytexlive/build-support/package-resource-release.sh
```

首条构建隔离运行库并测试，不安装。第二条按 release.json 打包并检查 HNP/HAP，有防覆盖保护，不要删除有效证据来重跑。Windows 签名入口为 `python build-support/sign-with-deveco.py --version 1.0.18`。

## 真机验收结果

样例位于下载目录 `TeXstudioResourceTest/B318`，生成入口为 `build-support/prepare-biber-device-tests.py`。HiShell 的 `run.sh` 已通过自动构建、中文空格路径、无变化跳过、修改、畸形输入及恢复。直接 Biber 的控制文件和数据模型校验通过，PDF 包含中文作者、交叉引用继承的书名/年份和更新后的标题。

应用通过“工具 → 自动构建并预览（XeLaTeX）”完成 `app-biber.tex`，已检查预览和导出的 PDF。16,000 条文献的 `app-cancel.tex` 在 Biber 活跃时点击停止，latexmk、shell 和 Biber 三个进程共用组 13704，随后全部退出；界面显示“已取消编译”，应用保持运行，之后普通样例再次构建成功。取消用大文献样例未完成排版，不能视为 16,000 条文献完整编译性能验证。

交付文件：`artifacts/TeXstudioHarmony-1.0.18-arm64-device-signed.hap`（1,453,512,111 字节）、`artifacts/texlive-1.0.18.hnp`（1,376,889,062 字节）。哈希见 `artifacts/SHA256SUMS-1.0.18.txt`；签名与未签名载荷相同。`candidate-result-1.0.18.json` 是安装后、验收前快照，最终状态以 `device-result-1.0.18.json` 为准。

上述警告已在 1.0.19 收尾；下一阶段独立推进 LuaHBTeX/LuaLaTeX；不要将本地 Biber 验收扩展为所有 TeX Live 工具均已适配。
