> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# B3.1：Perl 与 latexmk 自动构建

当前交付已更新为 **1.0.17 默认完整版**，取消状态和 locale 收尾已真机验收，见 `LATEXMK-POLISH-1.0.17.md`。本文保留 **1.0.16 基础功能及工作目录修复验收**（2026-09-17）。1.0.15 是已发现应用路径故障的中间测试版；历史失败证据保存在 `validation/latexmk/device-result-1.0.15.json`。

## 修复与功能

公共 HNP 内置 Perl 5.40.3、latexmk 4.87。TeXstudio 的“工具”菜单提供“自动构建并预览（pdfLaTeX）”和“自动构建并预览（XeLaTeX）”；HiShell 可直接使用公共命令，不需要配置 TeX 或 Perl 资源路径。

1.0.15 的故障来自鸿蒙限制原生当前目录查询。1.0.16 为应用子进程明确设置实际工作目录的 PWD；latexmk 启动器预加载 HarmonyCwd，在原生查询失败时比较 PWD 与当前目录的设备号、inode，仅身份一致时回退到逻辑路径。fastcwd 使用不改变目录的查询，避免失败后停留在祖先目录。修复仅作用于 latexmk，不改变任意文件 abs_path/realpath 的语义。

## 已通过的验证

- 11 项路径测试：有效逻辑路径恢复，拒绝过期、相对和缺失路径，子目录切换、File::Find 遍历及恢复；启动器参数、退出码和进程组取消回归。
- 宿主四组文档自动构建，以及 OHOS Perl 仿真执行。
- 真机 HiShell：中文 Beamer、PGFPlots、newpx、BibTeX 自动多轮构建；无修改时跳过、文献更新、报错后恢复、中文空格目录和嵌套 `-cd` 目录。未设置 TeX/Perl 资源覆盖变量；旧版的未初始化路径警告消失。
- 真机应用：XeLaTeX 自动构建并预览三页中文 Beamer；pdfLaTeX 自动构建并预览 newpx。
- 真机取消：停止按钮同时终止 latexmk、shell 和 pdflatex 三个进程，应用仍存活；取消后再次自动构建正常。
- 回收的七份 PDF（终端五份、应用两份）字体均嵌入。
- 108,647 个基线文件保持一致；仅安装版本路径与索引属于允许变化。签名、ZIP CRC、内嵌 HNP 一致性、最终 HarmonyCwd 模块内容均检查通过。

总结果：`validation/latexmk/device-result-1.0.16.json`。界面截图为 `xe16.png`、`pdf16.png`、`cancel16.png`、`recovered16.png`；取消前后进程表为 `cancel-before-1.0.16.txt`、`cancel-after-1.0.16.txt`，均位于 `validation/latexmk`。

## 1.0.16 历史交付

- `artifacts/TeXstudioHarmony-1.0.16-arm64-device-signed.hap`，1,434,590,847 字节，SHA256 `df829eda00ae45bc49888761666e5657511e6efc7a57a8ee5ddac8d7d8451528`。
- `artifacts/texlive-1.0.16.hnp`，1,357,968,726 字节，SHA256 `8cb06c266acf5ee89302874ae38b069ebd6815d64079ecedef70a740166c65b6`。
- 完整兼容资源仍为 2025.2，冻结引擎/内核基线仍为 1.0.5；开发用资源 ZIP 没有因此新增可执行程序。

## 使用方式

```sh
latexmk -pdf main.tex
latexmk -xelatex main.tex
latexmk -cd -xelatex "目录 空格/main.tex"
latexmk -c main.tex
```

latexmk 决定重跑次数并按需要调用 BibTeX；`-c` 清理中间文件并保留 PDF。应用私有用户资源不会自动共享给 HiShell，沿用 `USER-RESOURCES.md` 的同步方式。

## 边界与后续

1.0.16 曾出现 en_US.UTF-8 回退 C 和停止后显示“命令崩溃/出现错误”的问题；二者均已在 1.0.17 修复并真机验证，详见 `LATEXMK-POLISH-1.0.17.md`。历史测试当时已确认中文编译和子进程终止正常。

不支持动态加载第三方 XS 二进制模块；可选 re 调试扩展未链接，普通正则正常。Biber、LuaLaTeX 和外部绘图程序不在本次验收范围。下一步为 Biber 的依赖锁定及第三方 XS 构建验证，见 `BIBER-B32.md`。

构建使用 OHOS SDK 编译器与 sysroot、perl-cross 1.6.4 提示，保留 `_GNU_SOURCE` 与隐式声明编译报错检查。1.0.16 的 Perl 前缀锁定 texlive_1.0.16；当前 1.0.17 已重编译为对应路径，后续升级仍需同步重编译。源文件、构建与测试脚本快照见 `validation/latexmk/source-1.0.16`。构建链为 build-perl-ohos.sh → test-perl-qemu.sh → test-harmony-cwd.sh → regress-latexmk.sh → package-resource-release.sh → 项目签名及真机验收流程。
