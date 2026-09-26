> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 离线资源扩展：平台边界与 B1 实现

## 鸿蒙是否允许

技术路线是：用户通过系统文件选择器授权读取 ZIP，应用把宏包、模板和字体保存到自己的持久化 filesDir，已签名的 TeX 引擎通过显式搜索路径读取这些文件。

官方资料：

- [应用 Context 与文件目录](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/application-context-stage)：区分 filesDir、cacheDir 等沙箱目录。
- [文件选择器](https://developer.huawei.com/consumer/en/doc/harmonyos-references/js-apis-file-picker)：DocumentViewPicker 提供用户选取文件能力。
- [OpenHarmony 代码签名组件](https://github.com/openharmony/security_code_signature/blob/master/README.md)：说明运行时代码完整性与安装时代码签名机制；OpenHarmony 资料解释基础机制，不代替华为商业系统的全部产品策略。

已核对本项目实际 Qt 5.12.12 Harmony 源码：QStandardPaths 的 DataLocation/AppLocalDataLocation 对应 QOhosAppContext 的 filesDir。因此使用该 API 取得应用持久化目录，未写死设备沙箱路径。

`.sty`、`.cls` 本身包含 TeX 指令，由已有引擎解释；不能简单称它们为“毫无执行语义的纯数据”。它们的导入不需要把新 ELF 程序放进可写目录执行。Perl、Biber、LuaHBTeX 和动态库继续通过移植、签名、打包和应用升级交付，不纳入这个 ZIP 资源导入器。

技术可行性与应用市场审核是不同问题。本文没有声称取得上架审核许可；若准备公开发布，需按届时应用市场规范确认解释器、内容更新和资源分发要求。

## 本轮 B1 范围

菜单入口：选项 → 离线资源管理。

1.0.8 已补充导出、删除；终端、完整版分发和用户资源层设计另见 `RESOURCE-DESIGN.md`。

- 导入 `additive-v1` ZIP；核对兼容标识、逐文件大小和 SHA256。
- 拒绝绝对路径、路径越界、重复条目、符号链接、加密 ZIP、未声明文件，以及程序、内核/格式等不支持的内容。
- 在暂存目录解压，完成索引后再提交；失败不改变原资源选择。
- 导入后安排启用；也可选择已安装版本或恢复内置资源。
- 导出所选资源为可重新导入的 ZIP，无需保留原始 ZIP。
- 删除未被当前会话或下次启动选择的资源及其缓存；当前使用版本先切换并完整重启后再删除。
- 当前进程固定资源选择；所有切换在完整重启后生效。
- 生成 ls-R，接入 kpsewhich 和 TeXstudio 原有宏包扫描。
- 接入 OpenType/TrueType 字体搜索和按资源版本隔离的 Fontconfig 缓存。
- 当前保留基础资源优先级，扩展不能覆盖内置内核和既有宏包。

内部目录：

```text
filesDir/tex-resources/
  active.json
  resources/<内容标识>/manifest.json
  resources/<内容标识>/texmf/
  var/<兼容标识>/<内容标识>/fontconfig/
  config/
  texmf-home/  # B2.1 已接入可编辑用户层；B1 阶段仅预留
```

B1 只同时启用一个扩展集合。多个宏包需要装在同一个资源包中；以后再做多个集合的依赖与冲突处理。它不是完整离线 TeX Live 管理器，也不会安装任意 CTAN ZIP。

## 资源包协议

ZIP 根目录有 `manifest.json` 和 `texmf/`。清单包括 schema、profile、id、version、title、compatibilityId，以及每个文件的 size、sha256。兼容标识绑定阶段 A 的实际内核/格式组合。

第一版支持 tex/latex、tex/generic 内的常见 TeX 宏包文件，bibtex 的 bib/bst，fonts/opentype 的 otf，fonts/truetype 的 ttf/ttc，以及 doc 下的 txt/md/pdf。Type1 字体映射合并、Lua 模块和格式升级留给 B2。

使用 `build-support/make-resource-pack.py` 制作资源包。例如：

```powershell
python build-support/make-resource-pack.py --texmf validation/resources/fixture/texmf --output artifacts/my-resources-1.zip --id my-resources --version 1 --title "我的宏包"
```

SHA256 用于一致性校验；用户自带 ZIP 的清单不是发行者身份证明。正式发布资源时应再增加可信发布清单和来源核验。

## 接下来 B2

1. 从固定 texlive.tlpdb 解析集合与依赖，构建经过审核的离线编译资源集。
2. 加入资源集占用统计、包名/文件检索、许可证清单与可选说明文档包。
3. 加入 Type1 字体映射、相关索引及确定性的生成流程。
4. 为内核/格式升级定义独立兼容配置与完整资源切换流程；不得通过普通附加资源覆盖内核。
5. 独立完成 BibTeX → Perl/latexmk → Biber → LuaLaTeX；新的原生工具仍经签名应用升级。

## 1.0.7 验收结果（2026-09-16）

- 17 项宿主回归通过：合法导入、索引、启用、重复版本、兼容性、路径越界、程序文件、未声明文件、SHA256、重复条目、缺失文件、符号链接、内核替换、实际查找/编译、回退及安装后损坏检查。见 `validation/resources/host-tests.json`。
- 独立生成的测试字体经真实导入器导入后，可被 Fontconfig 找到；回退后不再选中；缓存目录隔离。见 `validation/resources/font-tests.json`。新增字体的真机 XeLaTeX 编译尚未单独验收。
- ARM64 构建、ZIP CRC、内嵌 HNP 一致性、官方签名验证、设备授权匹配通过。1.0.7 已覆盖安装到已连接设备。
- 真机使用系统文件选择器导入 `artifacts/harmony-resource-demo-1.zip`，完整重启后，应用内 pdfLaTeX 编译输出一页 PDF，显示 `Offline resource import works.`；内置 PDF 预览正常。
- `validation/resources/device-compile.log` 明确记录宏包读取自 `/data/storage/el2/base/files/tex-resources/resources/…/texmf/`。PDF 与截图分别为 `device-compile.pdf`、`device-compile-1.0.7.png`，导入成功截图为 `device-import-1.0.7.png`。
- 真机发现并修复了系统 libz 与内置 QuaZip 的 minizip 同名符号冲突：将内置实现设为隐藏符号，已检查最终 ELF 的 `unzGoToFirstFile` 为 LOCAL HIDDEN。1.0.6 为失败调试候选，不应作为交付使用。

本节对应 1.0.7 历史交付，后续版本见下方验收记录。保留 1.0.5 原产物。新版本仍使用原引擎；阶段 A 的 fdsan 引擎修复未包含在此包中，不能据此宣称该修复已真机通过。完整工具链、任意 CTAN ZIP、完整离线 TeX Live 和市场上架均不在本轮验收结论内。

## 1.0.8 资源管理验收

交付：`artifacts/TeXstudioHarmony-1.0.8-arm64-device-signed.hap`、`artifacts/texlive-1.0.8.hnp`。

- 原 17 项宿主回归通过；新增 9 项导出/删除回归通过，见 `validation/resources/management-tests.json`。
- 真机经系统保存选择器导出 ZIP，取回文件逐项对比，清单和资源内容与原包一致，见 `validation/resources/device-export.zip`。
- 真机已验证使用中删除保护；恢复内置资源并完整重启后可删除测试资源；随后用导出的 ZIP 成功重新导入。对应截图：`device-export-1.0.8.png`、`device-protected-delete-1.0.8.png`、`device-delete-1.0.8.png`、`device-reimport-1.0.8.png`。
- 官方签名验证、包内容一致性与设备授权匹配通过，1.0.8 已覆盖安装。
- 从导出包恢复并重启后，应用内 pdfLaTeX 再次生成一页 PDF，文本检查与内置预览通过。见 `validation/resources/device-result-1.0.8.json`、`device-compile-1.0.8.log`、`device-compile-1.0.8.pdf`。原有字体映射警告仍存在，未把无致命错误误记为无警告。


## B2.1 可编辑用户层（1.0.11）

在 B1 资源包管理之外新增独立可编辑用户层，支持文件添加、新建/编辑、删除、启停、备份恢复与索引/字体缓存刷新。普通宏包保存后下一次编译生效，内核/格式仍绑定冻结基线。

用户层和 HiShell 的使用说明见 `USER-RESOURCES.md`，最终证据见 `validation/resources/device-result-1.0.11.json`。开发中的 1.0.9、1.0.10 用于真机功能与布局检查，最终交付选择 1.0.11。

HiShell 公共 HNP 引擎可用，但不会自动读取应用私有用户层。应用导出 ZIP 后，在授权公共目录解压并显式设置 TEXINPUTS，已验证 pdfTeX 与 XeLaTeX 编译修改后的宏包。此流程是快照同步，不能当作两应用实时共享。

宿主 17 项导入、9 项管理、10 项用户层回归通过。原有字体映射警告仍存在；用户字体的 Fontconfig 添加/停用/删除已做宿主验证，新增字体家族名在 HiShell 的发现不在真机通过范围内。下一步是 B2.2 完整资源依赖、映射和容量预检。
