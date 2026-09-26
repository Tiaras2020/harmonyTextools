> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.21 兼容性修复

2026-09-25：已签名并安装到本次连接的鸿蒙设备。修复范围是 BibTeX 基础资源缺失与 HiShell 字体族名查找；不是全量 TeX Live 兼容性认证。

## 修改

- 内置资源加入锁定的 `bibtex` 包 revision 77677，共 11 个运行文件，包含 plain、abbrv、unsrt、alpha 等八种样式。下载档案与原 TeX Live 元数据 SHA512 一致。
- Fontconfig 两个字体目录改为相对配置文件定位，避免随终端工作目录变化而失效。
- HNP 打包前检查四种基础 BST 必须存在；交付校验逐文件核对新增资源和字体配置。
- 版本统一更新到 1.0.21，Perl、latexmk、Biber 启动路径对应新 HNP。pdfTeX、XeTeX、LuaHBTeX 和 LuaLaTeX 格式保持 1.0.20 验收基线字节一致。

## 验证

HiShell 中执行真实终端脚本，清除手工 TEXINPUTS、TEXMFCNF、TEXMFROOT、FONTCONFIG_FILE、FONTCONFIG_PATH、LUAINPUTS 设置后：

| 用例 | 结果 |
|---|---|
| plain、abbrv、unsrt + XeLaTeX/latexmk | 编译通过，三条文献及数字编号正常，资源定位到 1.0.21 HNP |
| alpha + XeLaTeX/latexmk | 资源定位与编译通过；中文作者生成的字母式标签乱码，视觉验收未通过 |
| 两个工作目录中的 Latin Modern Roman、FandolSong 字体族名 | 两项通过 |
| LuaLaTeX + 中文文献 Biber 自动构建 | 通过；Biber 版本命令标准错误为空 |
| 应用内旧 BibTeX 失败工程 | 清理旧缓存后重建成功，预览三条文献及正确编号 |
| 应用内 luatex-cn 古籍整幅页 | LuaLaTeX 自动构建和 PDF 预览通过 |
| 应用内字体族名 | Latin Modern Roman、FandolSong 编译和中文预览通过 |

脚本的七条 PASS 只代表命令成功，不能替代 PDF 检查。`alpha.bst` 中文标签问题保留为限制；需要中文作者字母式标签时改用支持 Unicode 的 Biber 工作流并验证样式，不在本次资源补齐中修改上游 BST。

**升级后恢复旧失败工程：** latexmk 会保留先前失败状态。若资源已修复但仍立即显示旧错误，先备份并删除该工程的 `.fdb_latexmk` 构建缓存，再重新自动构建。本次只清理隔离测试工程的这一文件，没有删除用户源文件。

打包 CRC、签名、签名前后负载一致性均通过。宿主侧 OHOS/QEMU Biber 工作流与 45 项直接 Perl 依赖检查通过；这些证据和真机结果分开保存。新版本源码增量已归档，但尚未完成干净环境全量重建，因此仍不能据此清除 WSL。

## 交付与证据

- `artifacts/TeXstudioHarmony-1.0.21-arm64-device-signed.hap`
- `artifacts/texlive-1.0.21.hnp`
- `artifacts/SHA256SUMS-1.0.21.txt`
- `validation/compat-fix-1.0.21/`：资源清单、宿主检查、源码增量、真机输入输出及结果。
- `validation/compat-review-2026-09-25/fix21-*.png`：应用实测截图。
- `LUATEX-CN-COMPATIBILITY.md`：第三方宏包试用、字体与目录要求。

本次不包含测试报告所提 CLI、失败时旧 PDF 提示的界面改造、Beamer 示例排版修改或用户资源层 `.lua` 导入支持。取消构建仍沿用 1.0.20 的已测实现，本次未重复取消测试。
