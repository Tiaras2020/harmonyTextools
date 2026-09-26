> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# B2.4：常用宏包、字体和 BibTeX 验证

本阶段已完成，默认完整版 **1.0.14 已签名并安装真机**，开发资源包为 **2025.2**。继续采用公共 HNP 完整资源、开发用精简本体加资源导入、可编辑用户层的结构。最终证据见 `validation/common-resources/device-result-1.0.14.json`。

## 当前交付

| 文件 | 大小（字节） | 用途 |
| --- | ---: | --- |
| `artifacts/TeXstudioHarmony-1.0.14-arm64-device-signed.hap` | 1,419,333,132 | 默认完整版，真机已安装 |
| `artifacts/texlive-1.0.14.hnp` | 1,342,718,033 | 与 HAP 内嵌内容一致 |
| `artifacts/harmony-full-resources-2025.2.zip` | 1,040,997,108 | 完整开发导入集合，91,998 文件，展开 1,948,074,279 字节 |

完整 HNP 与 ZIP 的 91,998 个资源逐文件 SHA-256 一致。签名后原始载荷保持不变，压缩校验和设备授权匹配均通过。

## 真机验收

应用内从系统文件选择器打开中文 Beamer 和 newpx 样例，编译完成并在内置 PDF 阅读器预览，分别为 3 页和 1 页。日志确认读取 1.0.14 公共 HNP，不读取私有导入集合。

全新 HiShell 会话中，TEXINPUTS、TEXMF、TEXMFCNF、TEXMFHOME、TEXFONTMAPS、TFMFONTS 均为空。直接通过公共 pdftex、xelatex、bibtex 和 kpsewhich 完成四类样例，资源查找指向公共 HNP；BibTeX 两条书目和正文交叉引用正确解析。四份终端 PDF 加两份应用 PDF 的字体全部嵌入，视觉检查通过。

开发 ZIP 已通过真实生产导入器导入精简基线，新增资源、映射优先级、四类文档编译、回退检查全部通过。此轮精简导入验证在主机进行；真机新增验收针对默认完整版。上一轮 1.0.12 精简导入真机证据保留在 `FULL-RESOURCES.md`。

## 本次内容

- 纳入 Beamer、translator 字典、PGFPlots 普通 TeX 后端、newpx 文本和数学字体，新增 974 个资源文件。
- 根据功能审核文件，而非因一个包包含可选工具就整包排除。PGFPlots 的外部脚本、ConTeXt 和 Lua 后端明确省略，必需依赖仍严格检查。未知文件仍进入待审核。
- 从经过归档校验的 cs、metapost、ttfutils 包中仅提取四份编码表，不执行脚本，也不表示移植了这些工具。
- 两份生成字体映射各有 35,460 条，隔离仍缺资源的 44 条，保留 35,416 条。相比首批集合减少 74 条缺失映射；未通过补空文件或隐藏错误声称支持。
- 开发包采用 `runtime-extension-v2`：仅在指定目录允许 Beamer PDF/EPS 图标、translator `.dict` 和 newpx `.fontspec`。原来的 v1 和 additive-v1 限制不变；引擎、配置、格式和内核仍不可覆盖。

## 已完成的主机验证

16 项解析/提取测试、24 项生产导入器文件边界检查，以及原导入 17 项、管理 9 项和用户层 10 项检查通过。

九组隔离编译通过：既有英文、中文空格路径、MCM 17 页、新宏包与 Type1 字体，以及新增加的中文 Beamer 3 页、PGFPlots 二维曲线/三维曲面/CSV 表格、newpx 字体、中文论文 BibTeX 多轮编译。四个新样例字体全部嵌入，最终无未解析引用或缺字，PDF 外观已检查。

BibTeX 验证顺序为 XeLaTeX → BibTeX → XeLaTeX → XeLaTeX，包含两条英文书目和中文正文交叉引用。这不构成 Biber 或任意 Unicode 书目数据库兼容声明。旧 MCM 示例存在既有引用警告，本次仅确认原有 17 页输出和资源隔离回归。

核对 107,203 个既有资源文件，只有索引和两份生成映射发生预期变化；204 个原生文件全部保持冻结基线哈希。

## 构建及证据

- `build-support/build-common-resources.py`：从保留的 v1 候选构造 v2，拒绝覆盖已有候选。
- `build-support/audit-full-maps.py`：审核并隔离不可用映射。
- `build-support/regress-common-resources.sh`、`verify-common-resources.py`：编译并验证候选。
- `build-support/make-common-resource-pack.py`：生成完整 2025.2 开发 ZIP。
- `build-support/test-common-import.sh`：真实 ZIP 导入到精简基线后编译。
- `build-support/package-resource-release.sh`：默认使用 v2 完整候选；开发可选 `HARMONY_RESOURCE_PROFILE=slim`。
- `build-support/verify-b24-payload.py`：逐文件比较开发 ZIP 与交付 HNP。
- `validation/common-resources/`：来源清单、略过文件原因、哈希、映射审计、回归、导入检查及真机证据。

2025.2 包需要 1.0.14 起的导入器，旧 1.0.12 精简测试版不能导入 v2。今后精简构建应递增版本号后使用同一新版源码。完整版无需重复导入自己的资源；应用私有导入和用户编辑资源仍需显式同步到 HiShell。

## 保留的限制和后续

PGFPlots 仅验证普通 TeX 绘图；Lua 加速、外部化、调用外部程序生成等高线等功能未纳入。Beamer 验证 PDF 输出，未新增 EPS 转换工具；newpx 验证 Type1 方案，未据此声称全部 OpenType/fontspec 选项可用。

后续优先独立推进 Perl + latexmk 自动多轮构建，再处理 Biber、LuaHBTeX/LuaLaTeX。这些需要原生运行时或引擎移植，继续增加静态宏包不能替代它们。
