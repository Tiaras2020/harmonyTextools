> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.22 平板界面与输入优化

范围来自 2026-09-25 的五项界面反馈；暂不做 LuaTeX 专项体验或 CLI 扩展。

## 改动

1. 菜单栏改为白色，按可用窗口宽度增加各菜单之间的空隙；窄窗口保留 Qt 的溢出处理。保留短菜单栏，不改成大按钮导航。
2. 工具栏、组合框、下拉菜单采用 Fusion 控件与统一的浅色扁平样式，使用项目自带的 Colibre 矢量图标和深色下拉箭头，关闭系统图标回退。这是接近 Windows 参考图的跨平台样式，不是移植 Windows 原生主题插件。
3. 鸿蒙构建隐藏不可用的外部 PDF 查看器入口，以及文件标签和结构树中的“打开所在文件夹”；保留复制路径和内置预览。桌面系统的实现不删除。
4. PDF 鼠标双击跳转源码；源码双击同步 PDF 并保留选词行为。触摸单次轻点不再直接跳转，短按释放保留链接操作，双击才同步。触摸双击窗口至少 500 毫秒，避免平台 300 毫秒鼠标阈值漏判普通手指双击。PDF 默认使用拖动浏览；手指在拖动或放大镜工具下都按拖动处理，按住不弹出放大镜。拖动使用屏幕坐标，避免内容滚动改变局部坐标造成抖动。鼠标仍可手动使用放大镜工具。
5. “工具 → 清理构建缓存并重新编译”提供 pdfLaTeX、XeLaTeX、LuaLaTeX 三个选项。只删除主文档同目录的 `.fdb_latexmk`，用 `-g` 强制重新构建；不调用会大范围删除产物的 `-C/-gg`，不主动删除 `.tex/.bib/.sty/.cls`、图片、用户 `.bbl` 或 PDF。构建期间禁用此菜单。

旧工程配置自定义输出目录时，`-g` 仍会强制运行；本次仅清理主文档同目录的依赖缓存，不递归搜索或清理其他目录。编译本身会正常更新其生成的文件。

## 版本与空间

应用版本 1.0.22，运行包仍为已签名交付验收过的 `texlive-1.0.21.hnp`，内容 SHA256 不变。`release.json` 显式记录 `runtimeVersion`，应用资源根目录使用该字段。后续改变引擎资源时需要同步更新运行包版本并重新验收。

构建与打包顺序：WSL 执行 `build-support/stage-ui-app.sh`；Windows 执行 `build-support/assemble-ui-package.py`、`build-support/check-ui-package.py`、`build-support/sign-with-deveco.py --version 1.0.22`、`build-support/check-device-profile.py --version 1.0.22`，随后安装签名 HAP。Windows 组装避免 WSL 跨盘大量小块 ZIP I/O。组装脚本拒绝覆盖已存在的 unsigned HAP，正式迭代应递增版本并更新这些本轮专用脚本中的版本。

本次复用既有 HNP，不生成另一份完整运行资源，不删除旧版交付文件，不清空 WSL。过程中产生的同版本候选 HAP 不作为交付件；最终交付用 SHA256 区分。

## 验证记录

应用代码已完成 OHOS ARM64 编译，最终候选 9 已签名安装。结果见 [device-result.json](validation/ui-polish-1.0.22/device-result.json)。真机通过：白色全宽菜单、统一图标、鼠标双向 SyncTeX、触摸双击同步、单击及 800 毫秒按住不误跳转、单指拖动、双指缩放，以及 PDF 内部链接单击翻页。

通过新菜单选择 XeLaTeX，成功恢复人为注入的旧版 BibTeX 失败记录，生成一页 PDF 和三条正确编号的参考文献。取回文件后，七个源文件/保留文件的 SHA256 全部不变；包括 `.tex`、`.bib`、`.sty` 和保留用 `.bbl`。菜单中的 pdfLaTeX、LuaLaTeX 选项共用清理实现，本轮没有分别重跑。

输入测试使用真机 `uinput` 鼠标事件和 `uitest/uinput` 触摸事件，不能替代实体鼠标、触控板的硬件与手感验收。右键事件注入未成功展开上下文菜单，因此“打开所在文件夹”移除依据为三个入口的源码条件编译与构建核对。额外探测发现：显式选择 PDF 文本工具后，手指拖动未出现文本选区；此项未建立旧版对照，尚不列为已通过。演示模式也未验收。

最终签名包：`artifacts/TeXstudioHarmony-1.0.22-arm64-device-signed.hap`。SHA256：`48a49abc1e95d5fdcb1716b185777820dc6d46fe743334654de6ac6a3148dbcf`。复用运行包 `artifacts/texlive-1.0.21.hnp`；安装、签名和嵌入资源一致性见 `validation/device-signing-1.0.22/result.json`。

已清理本轮生成的候选 1–8 的 16 个 HAP，释放 23,364,633,027 字节（约 21.76 GiB）。候选摘要和检查记录保留，旧版交付与 WSL 未删除。精确清单见 `validation/ui-polish-1.0.22/candidate-cleanup.json`。

![最终界面与缓存恢复结果](validation/ui-polish-1.0.22/ui22-final-clean-done.png)

隔离测试工程在平板 Download/Ui22；测试前源文件摘要记录在 `validation/ui-polish-1.0.22/source-hashes.json`。原始反馈截图也保存于此验证目录。
