> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 开发交接：TeXstudio Harmony 1.0.5

> 此文主体是 1.0.5 历史交接。2026-09-16 最新开发交付为 1.0.14 完整版：B2.4 常用资源和 BibTeX 真机验收见 `COMMON-RESOURCES-B24.md`；B2.2/B2.3 历史双版本交付见 `FULL-RESOURCES.md`；B1 管理见 `RESOURCE-EXTENSION.md`；B2.1 用户层与私有资源同步见 `USER-RESOURCES.md`。当前入口及后续顺序以 `START-HERE.md` 为准。

## 1. 当前状态与范围

- 目标：Huawei MatePad Edge，HarmonyOS 2in1，ARM64；应用包名 `com.ohos.texstudio`。
- 用户最新反馈：“已经没问题了”，对应最近 MCM 项目编译和宏包悬停问题。记录为用户报告通过，不冒充本轮重新执行的真机测试，也不扩大到全部引擎。
- 当前正式交付：`artifacts/TeXstudioHarmony-1.0.5-arm64-device-signed.hap`。
- 本轮整理只新增交接/清理清单并更新状态，没有删除源码、缓存或产物，没有重新编译/安装。
- 下一步需求是资源库管理、完整离线资源、参考文献、自动编译和 LuaLaTeX。界面美化不属于下一阶段优先工作。

## 2. 已完成

| 部分 | 成果和证据 |
| --- | --- |
| 编译/打包 | Qt for Harmony、TeXstudio、Poppler、TeX Live 的 ARM64 构建以及 HNP/HAP 打包已跑通 |
| 签名 | 使用此 TeXstudio 工程的 DevEco 签名材料完成官方 SDK 签名和验签；不用 HoKit 测试签名 |
| 英文编译 | 用户此前报告 pdfLaTeX 英文编译成功 |
| 1.0.1 | 为 XeTeX 生成可写 Fontconfig 配置并设置 FONTCONFIG_FILE |
| 1.0.2 | 设置 ICU_DATA 指向 HNP 的 share/icu，解决字体名称初始化问题 |
| 1.0.3 | 导出公共 xdvipdfmx 入口，补 tex-text.tec 和 MISCFONTS，修复 PDF 输出链路 |
| 1.0.4 | 打包 Poppler 字符映射数据并设置 custom data dir，解决有效中文 PDF 在内置预览中缺字 |
| 1.0.5 | 补 MCM 宏包/字体依赖、VFFONTS、字体映射与 ls-R；宏包查找与悬停提示恢复 |
| MCM 验证 | 宿主使用交付资源编译完整项目为 17 页，14 种字体全部嵌入；recorder 检查没有借用宿主全局 TeX 宏包 |

1.0.5 追加的 20 个资源包：mcmthesis、biblatex、todonotes、tocloft、fancybox、appendix、paralist、bera、jknapltx、rsfs、logreq、xpatch、marginnote、amscls、carlisle、trimspaces、tex-gyre、symbol、mweights、kastrup。

MCM 示例另修正 `fig24.jpg` 引用与实际 `fig24.JPG` 的大小写差异。原项目 `E:\CODE FILE\texfile\mcmthesis-demo` 未修改。交付项目为 `artifacts/mcmthesis-demo-harmony.zip`。

## 3. 当前能力边界与未完成

- 当前是裁剪资源集，不是完整 TeX Live。ls-R 中 596 个 sty/cls 文件名不是 596 个发行包。
- 未实现独立资源导入、资源版本切换/回退、可写用户宏包库和完整离线资源包。
- 脚本使用 TeX Live 2025 final 资源，但也选取 latex-base-dev；不能称其为完全一致的标准稳定版。新增大规模资源前必须固定引擎、内核、格式、biblatex/Biber 兼容组合。
- 已有公共入口：pdftex、tex、xetex、bibtex、makeindex、dvipdfmx、xdvipdfmx、dvips、kpsewhich、latex、pdflatex、xelatex。
- bin 内有部分其他工具，不代表已导出或实际可用。存在 luajithbtex/lualatex 相关文件，但构建脚本禁用了几个主要 Lua 引擎选项，LuaLaTeX 完整链路未验证。
- latexmk、Biber 和 Perl 运行链路尚未完成。
- fdsan 问题独立保留：`texk/web2c/texmfmp.h` 的 `gzdopen(fileno(FILE*), ...)` 与 FILE 所有权可能冲突；证据在 `validation/fdsan-investigation/`。后续应修描述符所有权及异常清理，不以禁用 fdsan 掩盖。
- 原始 MCM 项目已有 LastPage、BibTeX 提示、页眉等警告；本轮未修改论文内容以消除全部警告。

## 4. 工作目录与构建环境

### Windows

- 工作根目录：`<legacy-workspace>`。
- 源码：`texstudio-harmony`；DevEco 工程：`texstudio-harmony\texstudio_harmony`。
- TeXstudio 源码：`texstudio-harmony\third_party\texstudio`。
- 主仓库基线：`a8bfb147dcd173fa378687ae474ad152cd20f597`。
- TeXstudio 基线：`efc191c5d66ffcd0ca3b41b05b4f83a279b184ae`（4.9.5）；有未提交修改，绝不能 reset/clean。
- Qt 基线为 Harmony 适配的 5.12.12，尚未迁移 Qt6。
- DevEco：`E:\Huawei\DevEco Studio`；SDK 位于其 `sdk\default\openharmony`。
- 签名配置来自此工程 `build-profile.json5`；可能含敏感签名配置，不全文输出、不要发布，不保存账号密码到交接文档。
- 不修改无关 StudyTide 工程。

### WSL

```powershell
wsl -d Ubuntu-24.04
```

```bash
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
cd "$BUILD_REPO"
```

- `BUILD_REPO=/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915`。
- SDK 工具目录：`/home/tiarasubuntu2404/ohos-commandline-tools-6.1.1.280/command-line-tools`。
- Java17，JOBS=6；env.sh 设置 Linux PATH，避免混入 Windows 工具。
- `build/build-texlive-host`：宿主引擎；`build/build-texlive-ohos`：目标引擎。
- `build/build-texlive-ohos-dist`：当前精确运行资源，尤其应保留。
- `build/build-texlive-ohos-hnp`：可重新生成的 HNP 暂存副本。
- `build/build-texstudio-ohos`：编辑器增量构建。
- Qt/Poppler 的 build 和 install 目录保留以便增量开发。

Windows 和 WSL 是两个独立副本。修改后只同步对应文件，并核对两端差异。不要盲目双向覆盖；尤其保留各自的 SDK 路径和签名配置。

## 5. 关键实现入口与操作注意

- `third_party/texstudio/src/utilsSystem.cpp`：`ohosBundledTexRoot()`、`setOhosTexEnvironment()`；现在 TEXMF 指向内置资源，下一阶段要扩展搜索树。
- `third_party/texstudio/src/execprogram.cpp`：子进程相关已修改文件。
- `third_party/texstudio/src/pdfviewer/pdfrendermanager.cpp`：Poppler 数据目录。
- `third_party/texstudio/src/buildmanager.cpp`：已有 BibTeX、Biber、latexmk、LuaLaTeX 命令定义。
- `scripts/texlive/build_pack_texmf.sh`：手工宏包列表、资源打包、格式生成。
- `scripts/common/build_texlive_hnp.sh`：公共入口、HNP、自动 ls-R。
- `scripts/texlive/build_texlive_ohos.sh`：引擎构建；会删除重建目标构建目录，不适合直接用于每次增量调试。
- `build-support/add-mcm-packages.py`：最新补包、字体映射和来源记录。
- `build-support/build-mcm-fix.sh`：1.0.5 修复构建记录，内含版本替换；下一版本先改为版本参数化，不直接重放旧升级脚本。
- `build-support/package-hap.sh` / `finalize-packages.py`：组装 HAP；最终程序使用 PACKAGE_VERSION，默认值需检查。
- `build-support/sign-with-deveco.py --version <新版本>`：签名；输出存在会拒绝覆盖。
- `build-support/check-device-profile.py --version <版本>`：验签材料与设备匹配；设备离线时返回未核对，不表示不匹配。
- 避免直接运行上游 `sign_push.sh`；它还包含推送安装操作。
- 修改复杂 WSL 命令时先写 LF 的 .sh，再从 PowerShell 调用，避免变量被外层 shell 提前展开。

当前设备公共命令路径 `/data/service/hnp/bin/`；1.0.5 内置资源根 `/data/service/hnp/texlive.org/texlive_1.0.5/`。不要把安装器管理目录当用户可写资源目录。

## 6. 下一步按阶段实施

### A. 固定版本与回归基线

1. 保留当前签名包和 dist，审计引擎来源、构建选项、资源清单及格式版本。
2. 把固定 1.0.x 路径/版本替换改为统一版本配置，明确运行库与资源版本兼容约束。
3. 建立 pdfLaTeX、XeLaTeX 中文、MCM、字体和内置预览的回归样例。
4. 独立修复/复测已有 fdsan 问题，避免在新引擎中延续。

### B. 资源管理与完整离线资源（首要交付）

1. 用应用持久化可写目录建立 resources/<版本>、texmf-home、texmf-var；缓存单独管理。
2. 扩展 TEXMF/TEXMFHOME/TEXMFVAR/TEXMFCONFIG 等搜索规则，处理项目、用户、资源版本、基础资源的优先级和内核混用风险。
3. 从固定仓库的 texlive.tlpdb 解析集合与依赖，生成完整编译资源包、可选说明文档包和清单；原生程序依赖明确列为需要移植。
4. GUI 增加导入、版本/占用查看、宏包搜索、完整性检查、索引刷新和回退。
5. 导入先检查空间、路径越界及校验值，暂存完成后再切换。编译期间固定资源版本；失败不损坏旧库。
6. 完成 ls-R、字体映射、Fontconfig、必要格式生成以及 TeXstudio 宏包/文档索引更新。
7. 验收：不换 HAP，只导入资源，使原缺包项目成功；重启、失败导入、回退、中文字体和预览均正常。

### C. BibTeX、Perl 与 latexmk

- 先测 BibTeX 的 aux/bib/bst 到 bbl 再回编译的真实链路。
- 移植 Perl 及必要模块，验证子进程/路径/文件系统操作，安装 latexmk。
- 接入已有构建入口，先做一次点击到引用稳定，再做持续监听。
- 测正文/图片/bib 增量更新、无修改不重复编译、错误停止、取消全部子进程和中文/空格路径。

### D. Biber

- 锁定与 biblatex 匹配的 Biber；复用 Perl，交叉编译需要的原生扩展并部署数据。
- 优先评估显式解释器+模块部署；不要假设其他平台自解包二进制能在鸿蒙运行。
- 验证 Unicode/中文参考文献、排序、样式、bib 修改更新和 latexmk 联动；版本输出不能代替验收。

### E. LuaLaTeX

- 审计现存 Lua 相关文件；优先建立明确可复现的非 JIT LuaHBTeX 构建。
- 补配套 Lua 模块、luaotfload、字体和匹配的 lualatex 格式，配置可写字体缓存。
- 验证英文、中文 ctex、OpenType、unicode-math、参考文献、多文件、中文路径、重复编译及内置预览。

每阶段记录源码变更、版本和真机结果。不要宣称“完整资源”等于所有外部程序均已支持。

## 7. 交付校验与证据

本轮重新计算 SHA256：

| 文件（artifacts/ 下） | SHA256 |
| --- | --- |
| TeXstudioHarmony-1.0.5-arm64-device-signed.hap | 5e52ac3a6a21dc2d95a6d51d159502e176664325e25160e2ddee1955d7778e99 |
| TeXstudioHarmony-1.0.5-arm64-unsigned.hap | 6c37f56969b8aa23385d74d3a04fe475e6fc2d726fe193c3a5adbaa52fd4cbf6 |
| texlive-1.0.5.hnp / texlive.hnp | 2d4ad4b87610720dec435b6837092d6a4bc697ff9ce3ed879994d91ce1f2ce32 |

证据：`validation/mcm-project/`、`validation/cjk-rendering/`、`validation/device-signing-1.0.5/`、`validation/fdsan-investigation/`。
最新验签时设备离线；用户后续反馈已解决，属于独立的用户验收来源。本次整理未查询当前连接设备，也未重跑真机编译。

## 8. 原始参考

- https://github.com/baitianyu-kun/texstudio-harmony
- https://tug.org/texlive/doc/tlmgr.html
- https://tug.org/texlive/doc/texlive-en/texlive-en.html
- https://ctan.org/pkg/latexmk
- https://github.com/plk/biber

后续实施时重新核对所选版本，不直接使用滚动仓库最新依赖。
