> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 内置 PDF 预览中文缺失修复：1.0.4

## 已确认的原因

用户提供的设备生成 PDF 可以由 MuPDF 正常渲染全部中文。FandolSong-Regular 和 FandolSong-Bold 已嵌入 PDF，使用 Adobe-GB1 CID 字符集合，没有单独的 ToUnicode 表。该 PDF 本身包含可显示的中文字形。

应用使用的 Poppler 源码在 `GfxFont.cc` 中检查 Adobe-GB1 的 CID 映射；没有映射时报告 `Missing language pack for 'Adobe-GB1' mapping` 并停止初始化中文字体。鸿蒙 Poppler 默认数据目录为 `/usr/share/poppler`，此前安装包未包含对应语言数据。这解释了英文和数学正常、中文全部空白的现象。

## 修复

- 将 poppler-data 0.4.12-1 的 cMap、cidToUnicode、nameToUnicode、unicodeMap 数据及版权/许可声明打入 HNP 的 `share/poppler`。包含简体、繁体、日文、韩文映射。
- TeXstudio 在创建首个 Poppler 文档前调用 `GlobalParamsIniter::setCustomDataDir()`，指向已打包的数据目录。
- 开启当前固定版本 Poppler 的内部接口头文件安装，供 TeXstudio 使用该接口；应用与 Poppler 版本配套构建。
- 增加 `ohosBundledTexRoot()`，让预览资源路径与 TeX 子进程沙箱回退路径共享根目录。
- HAP/HNP 同步升至 1.0.4，texmf.cnf 同步更新；保留先前 ICU、Fontconfig、xdvipdfmx 导出与 tex-text.tec 修复。

## 对照验证

使用用户原始 PDF 和与应用相同源码版本的宿主机 Poppler/Splash 渲染器：

1. 指向空数据目录：复现 `Missing language pack for 'Adobe-GB1' mapping`，页面中文全部消失，外观与设备截图相符。
2. 指向新 HNP 对应的 Poppler 数据：上述错误消失，标题、作者、中文正文、日期和章节名全部恢复。
3. 人工检查前后渲染图；像素变化共 8071 个（96 DPI）。对照图左侧为缺少数据，右侧为修复后。
4. ARM64 TeXstudio 构建、HNP/HAP 打包通过；完整签名包验证通过；当前连接设备与签名授权匹配。
5. 签名 HAP 内的 HNP 版本、映射文件、版权声明、texmf 根路径，以及原生库中的预览数据路径均通过检查。

证据位于 `validation/cjk-rendering/`，包括原始 PDF、同版本 Poppler 对照日志、`preview-comparison.png` 和 `final-package-check.json`。宿主机渲染验证不能替代鸿蒙应用沙箱内复测；本次未安装新包到设备。

## 交付与复测

安装包：`artifacts/TeXstudioHarmony-1.0.4-arm64-device-signed.hap`

SHA256：`054437f391fff6d9ba97b1adbf0f762f2b01e9ee41b450d1c71640ea9ae9d1ea`

独立 HNP：`artifacts/texlive-1.0.4.hnp`，已包含在签名 HAP 内。

覆盖安装后完全退出并重启 TeXstudio，直接打开已有 `xelatex-cjk.pdf` 检查中文显示。无需重编译文档来验证此项修复。确认显示恢复后可再正常编辑、编译和预览。

构建脚本：`build-support/build-preview-fix.sh`；同版本渲染对照：`build-support/validate-poppler-preview.sh`；签名：`python build-support/sign-with-deveco.py --version 1.0.4`。

已知独立问题：先前定位的 TeX 格式文件句柄 fdsan 检查仍未在本次修改中修复。
