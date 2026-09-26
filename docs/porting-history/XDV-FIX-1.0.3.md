> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# XeLaTeX PDF 输出修复：1.0.3

## 设备证据

用户提供的新版日志已成功加载 Fandol 中文字体，并完成第 1 页排版，随后出现 `Error 32512 (driver return code) generating output`。消息截图明确指出 `/data/service/hnp/bin/xdvipdfmx: inaccessible or not found`。

1.0.2 所含 HNP 内存在 `bin/xdvipdfmx`，但 `hnp.json` 的公共入口清单遗漏它。XeTeX 默认通过自身入口所在目录调用该驱动，因此最终 PDF 生成失败。

同份日志中的 `Font mapping ... tex-text.tec ... not found` 来自缺少 XeTeX 的标点、连字映射文件。单独的 missfont.log 仅有 `unisong62` 位图字体生成请求，无法据此认定属于当前 XeLaTeX 调用；当前主日志使用的是 Fandol 字体。

## 修改

- HNP 清单新增 `bin/xdvipdfmx` 公共入口。
- 从本次使用的 TeX Live 源码复制 `libs/teckit/tex-text.tec`，安装到 `texmf/fonts/misc/xetex/fontmapping/`。
- 在 texmf.cnf 中显式配置 `MISCFONTS = .;$TEXMFDIST/fonts/misc//`。
- HAP 与 HNP 均升级为 1.0.3；同步更新 texmf.cnf 默认根路径与 TeXstudio 沙箱回退路径，避免将内容更新留在旧 HNP 版本号下。
- 保留之前的 Fontconfig 与 ICU_DATA 修复。本次没有修改 fdsan 相关引擎代码。

## 验证与边界

1. ARM64 TeXstudio 构建、HNP 打包和 Hvigor HAP 打包通过。
2. 从实际新 HNP 解包资源，按其清单建立测试入口。测试中的 xelatex、xdvipdfmx、pdflatex 使用相同 TeX Live 源码的 Linux 宿主机程序，其余字体、宏包和格式资源来自新 HNP。
3. 不指定 `-output-driver`，让 XeTeX 自动查找旁边的 xdvipdfmx。中文样例两遍和英文样例编译成功；没有映射缺失或输出驱动错误。
4. 中文 PDF 为 1 页；文字提取与人工预览确认中文、公式、标题及“第 3 节”交叉引用正常。仍有 cmex 非标准字号替代警告，不阻止生成 PDF。
5. 最终已签名 HAP 的版本、嵌入 HNP 哈希、导出清单、映射文件、MISCFONTS 配置、应用回退根路径均核验通过。SDK 验签与当前设备授权匹配检查通过。

本次没有在设备上安装新包，宿主机验证不能替代 HarmonyOS 沙箱内的实际运行验收。

## 交付

- 安装用：`artifacts/TeXstudioHarmony-1.0.3-arm64-device-signed.hap`
- SHA256：`9b9e474dba54e6e4330229c33fb79c72426b811014c6ab8e7dc8abd19851dc45`
- 独立 HNP：`artifacts/texlive-1.0.3.hnp`，已包含在签名 HAP 内。
- HNP SHA256：`c10d617885dfb90a7de86b2e69d7d6453acc862d6effff75ec45d14efb2cb181`
- 验证结果：`validation/xdv-fix/` 和 `validation/device-signing-1.0.3/`。
- 参考 PDF：`validation/xdv-fix/xelatex-cjk.pdf`。

覆盖安装已签名 HAP，完全退出并重新打开 TeXstudio，用 XeLaTeX 编译中文样例两遍，确认设备端 PDF 正常生成与预览。无需手动指定 PDF 驱动；如果仍失败，请保留新的消息和 .log。

构建：`build-support/build-xdv-fix.sh`；验证：`build-support/validate-xdv-fix.sh`，Windows PDF 检查：`python build-support/render-xdv-fix.py`；签名：`python build-support/sign-with-deveco.py --version 1.0.3`。
