> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# Biber 1.0.19 收尾记录

2026-09-18：**1.0.19 完整版已签名安装，并完成真机验收。** Biber 的空路径/未初始化警告及 xdvipdfmx 的配置/字体映射查找警告已在本轮样例中消除。最终证据：`validation/biber/polish-1.0.19/device-result.json`。

## 修复

- 安装版 Biber 入口不再执行 `use lib $FindBin::RealBin`。公共原生启动器已经通过绝对 `-I` 路径提供完整模块目录，避免沙箱 realpath 失败后向 @INC 添加空值。
- 内置 texmf.cnf 新增 DVIPDFMXINPUTS / XDVIPDFMXINPUTS，字体映射目录加入 dvipdfmx；应用显式指向内置驱动配置，继续保持用户宏包/字体层与驱动控制配置分离。
- 保留有效的 pdftex.map、ckx.map；不再默认加载没有随兼容发行提供的 kanjix.map。这不新增日文字体兼容性承诺。
- Perl 在独立 biber-perl-1.0.19 树重新编译，编译期安装路径为 texlive_1.0.19，不依赖旧 HNP。1.0.18 运行库与测试证据保留。

## 已完成检查

45 项模块最低版本及加载检查通过；真实 Biber 中文路径、排序、crossref、更新、失败/恢复回归通过，BBL 与 1.0.18 一致；编码、转写、日期数据冒烟通过。

生产 C++ 资源配置结合真实 kpathsea 检查通过：应用和终端均找到驱动配置和两份有效字体映射，用户层同名驱动配置不能替换内置配置。冻结资源核对通过：108,646 个基线文件未变化，允许 texmf.cnf、dvipdfmx.cfg、ls-R 的已审查变化，新增 5,358 个运行库/工具文件。

真机使用 B319 全新样例：HiShell 的 Biber 版本输出正确、启动 stderr 为 0 字节；首次编译、直接 Biber 控制文件/模型校验、增量跳过、修改文献、畸形输入及恢复全部通过。所有处理日志未出现此前的启动/配置警告。xdvipdfmx 详细日志明确加载 1.0.19 内的 pdftex.map、ckx.map。

应用自动 XeLaTeX 构建与预览通过；在 Biber 处理 16,000 条文献的测试输入时停止，进程组 37802 中的 latexmk、shell、Biber 全部退出，界面显示“已取消编译”，应用 PID 32022 保持运行。之后普通文献样例再次构建完成。大文献仅用于取消测试，不代表已完成其全量排版性能验收。

已渲染检查三份 PDF（HiShell 自动构建、直接驱动输出、应用构建），中英文文献、继承书名/年份和更新标记正确，每份六种字体全部嵌入。截图、PDF、文本及字体检查见上述证据目录。

## 交付

- `artifacts/TeXstudioHarmony-1.0.19-arm64-device-signed.hap`：1,453,511,741 字节，SHA256 `c490c401d85dc19804440cb259978e7e14b128a89bca27ad7358d26d3e89db1c`。
- `artifacts/texlive-1.0.19.hnp`：1,376,889,263 字节，SHA256 `6b1c722b534738fc2015de75fbd700a1b0e21c5d828315ae49c87383d650bf61`。
- 签名与载荷校验见 `validation/device-signing-1.0.19/result.json`；完整校验和见 `artifacts/SHA256SUMS-1.0.19.txt`。签名时记录的 installed=false 是当时状态，安装与验收状态以最终 device-result.json 为准。

远程 HTTPS 仍未真机验收；原有编码覆盖范围等限制见 BIBER-B32.md。下一项主要移植为 LuaHBTeX/LuaLaTeX。

证据目录：`validation/biber/polish-1.0.19/`。复现顺序：`build-biber-polish.sh` → `test-biber-polish.sh` → `package-resource-release.sh` → `verify-latexmk-payload.py` → `check-polish-resource-env.sh` → 签名 → 真机验收。脚本均在 `build-support/`；沿用已锁定的 1.0.18 Biber 原生源码树。
