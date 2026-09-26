> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# B2.2/B2.3 资源集合与双版本交付

> 本文保留 B2.2/B2.3 历史交付与验证。最新为 **1.0.14 / 2025.2**，见 `COMMON-RESOURCES-B24.md`：Beamer、PGFPlots 普通 TeX 后端、newpx 和 BibTeX 已完成真机验收，新增 974 文件，缺失映射降至 44 条。下文“当前”和“后续”均指 B2.3 时点；构建入口现已指向审核后的 v2 候选。

2026-09-16：B2.2 资源处理与 B2.3 双版本分发已完成。**1.0.13 默认完整版已签名安装，应用与 HiShell 真机验证通过**；1.0.12 为精简开发测试版，已验证完整资源导入、重启、编译和预览。这里的完整版包含首批审核集合，不表示所有桌面 TeX Live 包或外部工具均已支持。

## 当前交付与使用

| 交付件 | 大小（十进制） | 用途 |
| --- | ---: | --- |
| `artifacts/TeXstudioHarmony-1.0.13-arm64-device-signed.hap` | 1,411,125,835 字节 | 默认完整版；资源预装公共 HNP，当前真机已安装 |
| `artifacts/TeXstudioHarmony-1.0.12-arm64-device-signed.hap` | 379,048,522 字节 | 精简开发测试版，需导入下列 ZIP 才获得新增集合 |
| `artifacts/harmony-full-resources-2025.1.zip` | 1,032,766,865 字节 | 开发导入包，91,024 个文件，解压 1,929,545,349 字节 |
| `artifacts/texlive-1.0.13.hnp` | 1,334,501,057 字节 | 与完整版 HAP 内嵌 HNP 相同，供构建核对 |

默认完整版无需再导入同一资源 ZIP。HiShell 新会话中可直接执行 `pdftex -progname=pdflatex -halt-on-error main.tex` 或 `xelatex -halt-on-error main.tex`。已验证 `qrcode`、`tabularray`、Accanthis 和 `cmathbb`，无需设置 TEXINPUTS、导出或解压同步发行资源。用户自行编辑的私有用户层仍按 `USER-RESOURCES.md` 显式同步。

精简版使用「选项 → 离线资源管理 → 导入资源包」，导入成功后完全退出并重新打开应用。导入后的应用私有集合不会自动提供给 HiShell；终端直接使用完整发行资源需要安装完整版。ZIP 解压保存后不再是运行依赖，删除 ZIP 不会删除导入内容。

同一设备已安装较高版本时，不能把安装旧精简测试版作为日常切换流程。后续开发构建应使用新的版本号及 `HARMONY_RESOURCE_PROFILE=slim`，避免公共 HNP 的同版本缓存混淆。默认不设置该变量即构建完整版。

开发包导入前检查展开大小并保留 1 GiB 空间，未知可用容量时拒绝导入。已有资源保留；当前真机因同时保留开发导入集及公共完整版，测试后可用空间从约 82 GiB 降至约 75 GiB。若不再需要私有导入集，可在已切回内置资源并重启后删除该导入版本；用户资源层独立保留。

新协议 `runtime-extension-v1` 扩展字体、映射和样式文件支持，仍拒绝脚本目录、原生程序、web2c 配置、格式与核心内核覆盖。兼容标识仍为 `tl2025-harmony-baseline-1.0.5`。格式和可执行程序搜索路径保持冻结；只有审核的扩展字体映射优先于内置映射。旧 `additive-v1` 限制保持不变。

## B2.3 验证证据

- 原导入 17 项、管理 9 项、用户层 10 项回归通过；新增协议与实际完整 ZIP 的 6 组检查通过。
- 完整版 HNP 与开发 ZIP 的 **91,024 个资源逐文件 SHA-256 相同**；204 个原生文件与冻结基线相同。见 `validation/full-resources/b23-payload.json`。
- 精简版真机导入后编译并预览新增 Type1 字体；完整版切回内置资源后编译并预览同一文档，日志确认读取公共 HNP，不读取私有导入目录。
- 全新 HiShell 会话中六个资源覆盖变量均为空；通过公共命令完成 pdfTeX 宏包、Type1 字体及 XeLaTeX 编译。所有输入均来自公共 HNP 或测试项目。
- 五份真机 PDF 均为 1 页且字体全部嵌入。最终报告：`validation/full-resources/device-result-1.0.13.json`；HiShell 原始证据：`device-full/hishell-full-1.0.13/`；源码快照：`source-1.0.13/manifest.json`（均在 `validation/full-resources/`）。
- 当前仅完成项目开发签名和已授权真机安装，未验证 AppGallery 上架与渠道包体限制。

## 结果与边界

- 固定 TeX Live 2025 `tlnet-final` 元数据，SHA-256 为 `56df038e9070a3d587eeceb5def3f154b2cacccef36d4295bb49e0618977c34a`。每个下载归档另按元数据校验 SHA-512 和大小。
- 从 `scheme-full` 解析：3,194 个静态资源候选包、150 个冻结基线包、247 项排除、1,170 项待审核、7 个现有原生程序提供项、37 个集合节点。集合被排除时不展开其子项，因此这些数字不是整个 TeX Live 的逐包总量。
- 新增 91,002 个文件，实际解压 1,920,511,579 字节；归档下载量 690,103,916 字节。下载与暂存容量预检要求 6,024,119,916 字节。这是构建端要求，不能替代设备安装/导入空间检查。
- 不下载桌面平台原生程序作为鸿蒙程序；已知缺少 Python、Perl、Biber、LuaTeX 等工具的项目排除或待审核。未知文件、未知安装动作及未满足依赖进入待审核。筛选是保守静态分析，不能证明所有宏包的可选后端均可用。
- 保留冻结引擎、内核及格式。新增资源不能覆盖不同内容的已有文件。基线缓存包名只表示冻结来源集合，实际冻结文件哈希另行记录与核对。
- 文档、源码、完整桌面脚本与工具链没有纳入。`beamer`、`pgfplots` 等仍有未审核文件或功能，不能声称当前已经覆盖所有常用宏包。

## 字体映射

隔离运行宿主 `updmap`，只读取候选树及指定配置，不修改宿主全局字体配置。固定版本 `texlive-scripts` 归档只提取三份基础映射数据，不执行归档内脚本。

原始生成 35,127 条字体映射。核对实际字体/编码文件后，修正 7 条唯一确定的大小写引用，隔离 118 条缺少资源的条目；审核后的映射保留 35,009 条。被隔离的字体仍不支持，不能把对应字体功能标为可用。完整清单见 `validation/full-resources/maps-reviewed.json`。

`cmathbb` 上游声明与实际文件名大小写不一致；添加 17 个内容相同的文件名别名，保留上游文件，逐项记录 SHA-256。见 `validation/full-resources/font-adaptations.json`。没有通过放宽整个文件系统大小写规则解决问题。

## 验证

12 项解析和解压测试通过，覆盖依赖缺失、未移植二进制、循环依赖、基线冻结、未知安装动作、路径穿越、链接、未声明/重复/缺失文件、容量超限和校验失败。

五项宿主编译回归通过：英文、中文空格路径、MCM 17 页、新增 `tabularray`/`qrcode`、新增 Accanthis/`cmathbb` 字体。所有字体嵌入，录制的 TeX 输入未落到宿主其他资源树。结果见 `validation/full-resources/regression/result.json`。这是宿主验证，不替代鸿蒙真机验证。

最终来源核对见 `validation/full-resources/result.json`，包决策清单见 `plan.json`，逐文件来源与哈希见 `assembly-v1.json`。以上均在 `validation/full-resources/`。

## 复现与后续

WSL 构建目录：`/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915/build`。已生成 `full-resources-stage-v1` 和 `full-runtime-v1`，冻结的 `build-texlive-ohos-dist` 保持原样。该目录本身不能直接导入；B2.3 的 `make-full-resource-pack.py` 将审核后的差量和映射生成为 `runtime-extension-v1` ZIP，需要 1.0.12 起的新导入器。

工具入口：

1. `build-support/plan-full-resources.sh`：仅传默认参数生成计划；加 `--cache <归档缓存目录> --stage <新的空目标路径>` 下载并提取。策略位于 `texstudio-harmony/scripts/texlive/resource-policy.json`。
2. `build-support/assemble-full-resources.py --baseline <冻结运行时> --resources <提取目录> --output <新候选目录> --report <报告路径>`：组装并生成待审映射。失败后 `--resume-maps` 会重新核对已存在的资源内容，不能用于覆盖任意差异。
3. `build-support/audit-full-maps.py <候选目录> --report <报告路径>`：严格检查；本次明确使用 `--quarantine-unavailable` 隔离并记录不可用字体条目后安装映射。
4. `build-support/adapt-full-fonts.py <候选目录>`：应用已审核的 cmathbb 文件名适配。
5. `build-support/regress-full-resources.sh`：刷新索引并执行五项回归。当前指向本次 v1 候选目录。
6. `build-support/verify-full-candidate.py`：核对基线、引擎和新增资源哈希并生成最终报告。当前指向本次报告路径。

B2.3 打包入口为 `build-support/package-resource-release.sh`，默认 full，开发版可设置 `HARMONY_RESOURCE_PROFILE=slim`。每次改变交付内容先更新 release.json 的版本并运行 `scripts/release_config.py --write`；不覆盖已交付版本。签名工具为 `build-support/sign-with-deveco.py`。当前项目兼容集合仍指向 B2.2 v1，变更资源集合须重新走解析、审核和回归流程。

后续重点：按实际项目需求审核待纳入宏包（包括 beamer、pgfplots），补齐不可用字体引用，并独立推进 BibTeX 项目回归及 Perl/latexmk、Biber、LuaHBTeX 工具链移植。不能仅因资源可导入就把这些功能标为支持。
