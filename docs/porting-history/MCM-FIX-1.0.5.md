> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# MCM 项目与宏包悬停提示修复：1.0.5

## 原因

设备日志的首个致命错误是 `File mcmthesis.cls not found`，后面的第 60 行 `mcmsetup` 是停止位置，并非该命令语法错误。电脑从全局 TeX Live 2024 安装加载该类；它并不在用户的项目目录中。此前鸿蒙精简资源未包含该类和多项依赖。

悬停提示使用 TeXstudio 的已安装宏包列表。KpathSeaParser 调用 `kpsewhich --show-path ls-R`，然后扫描数据库内的 .sty/.cls 文件名；此前没有打包 ls-R，因此已安装宏包也可能显示“没找到”。todonotes 在旧包中还确实缺失。

完整项目测试进一步发现：VFFONTS 未配置，搜索路径为 `/nonesuch`，导致现有 Courier 虚拟字体无法加载；原字体映射合并规则混入了非 dvips/pdftex 格式的数据。

## 修改

- 补充来自 TeX Live 2025 最终归档的 20 个运行包：mcmthesis、biblatex、todonotes、tocloft、fancybox、appendix、paralist、bera、jknapltx、rsfs、logreq、xpatch、marginnote、amscls、carlisle、trimspaces、tex-gyre、symbol、mweights、kastrup。下载源与文件哈希记录在 `validation/mcm-project/added-packages.json`。
- 打包时生成 ls-R 数据库，包含 596 个 .sty/.cls 文件条目，供 Kpathsea 和 TeXstudio 宏包提示读取。
- 配置 VFFONTS 搜索 `fonts/vf`；只合并 dvips/pdftex 格式的字体映射，并嵌入可用的 Type 1 字体，避免依赖桌面系统字体替换。
- HAP/HNP 同步升级到 1.0.5，保留此前中文编译和 PDF 预览修复。
- 创建完整项目测试副本，只把源码中的 `fig24.jpg` 引用改成实际文件名 `fig24.JPG`，解决大小写敏感平台的兼容问题。原电脑项目未改动。

## 验证

- 完整项目使用随包资源进行三次 pdfLaTeX 编译，成功生成 17 页 PDF，与电脑页数相同。
- 通过 recorder 文件核对所有 TeX 输入，未使用宿主机全局 TeX 资源补缺。
- 14 种 PDF 字体全部嵌入；所有页面有文字，页面总览检查可见插图、表格、公式和代码列表。
- kpsewhich 能找到 mcmthesis、biblatex、todonotes、tocloft、newtxtext、amsmath；对应文件存在于最终 HNP 和 ls-R 中。
- 核对 TeXstudio 内置宏包说明数据库包含所查宏包描述。实际鸿蒙悬停界面仍需重启应用后复测。
- ARM64 应用构建、HNP/HAP 打包、完整 HAP 签名与验签通过。签名授权文件与此前已验证的 1.0.4 完全一致，仍在有效期内；最终核对时设备已断开，未执行当前设备匹配和安装测试。

宿主机使用相同 TeX 源码的 Linux 程序和鸿蒙包资源进行测试，不等于已在鸿蒙沙箱内验证新包。

## 原项目已有的警告

电脑原始日志也包含 LastPage 未定义及 BibTeX 提示；项目还存在页眉高度、浮动体位置等警告。本次保留论文内容与模板用法，没有修订这些问题。因此生成 PDF 成功不表示文档已消除全部警告，页眉总页数仍可能显示问号。

## 交付与使用

1. 覆盖安装 `artifacts/TeXstudioHarmony-1.0.5-arm64-device-signed.hap`，完全退出并重新打开 TeXstudio。
2. 将 `artifacts/mcmthesis-demo-harmony.zip` 完整解压到设备文档目录，保留 figures 和 code 子目录。
3. 打开其中的 mcmthesis-demo.tex，用 pdfLaTeX 编译两至三遍，检查 PDF 和宏包悬停提示。

签名 HAP SHA256：`5e52ac3a6a21dc2d95a6d51d159502e176664325e25160e2ddee1955d7778e99`

项目 ZIP SHA256：`6a1c018e6ea091ec8f98a625766adfefb17294442e7b8024fa62a6a538d6c82f`

参考 PDF：`validation/mcm-project/project/mcmthesis-demo.pdf`；检查结果与页面总览位于 `validation/mcm-project/`。

本版本仍是按需求补充宏包的精简 TeX Live，未声称覆盖完整 TeX Live 的所有包。此前 fdsan 格式文件句柄问题独立保留。

## 后续用户验收与交接

用户后续回复“已经没问题了”，记录为最近 MCM 项目编译和宏包悬停问题已解决。上文“仍需复测”和设备断开描述保留作为构建当时的历史状态，不代表当前仍在等待用户验收；本次整理没有重新执行真机测试，也不代表 Biber、latexmk 或 LuaLaTeX 已通过。

继续开发从 `START-HERE.md` 开始，技术交接见 `DEVELOPMENT-HANDOFF.md`，可清理项见 `CLEANUP-PLAN.md`。
