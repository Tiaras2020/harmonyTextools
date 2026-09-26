> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.23 Lua 用户资源与应用 CLI

本版扩展 Lua 源码导入，并提供面向 HiShell AI 的小型应用自动化会话。TeX 引擎和运行资源继续复用 1.0.21 HNP。理解各层职责先读 [TeX 环境学习说明](TEX-ENVIRONMENT-GUIDE.md)。已签名安装并完成限定范围真机验收，结果见 `validation/lua-cli-1.0.23/device-result.json`。HiShell 调用应用构建、日志、错误恢复、并发拒绝、取消及取消后构建通过；用户层 luatex-cn 横排样例生成一页 PDF，中文英文显示正常且无缺字日志。此结果不代表宏包所有功能均已验证。

## Lua 资源

- 用户资源“添加文件”和文本编辑支持 `.lua`；推荐放在 `tex/luatex/包名/`，完整保留子目录。
- ZIP 使用新的 `additive-lua-v1`，支持 `tex/latex/`、`tex/generic/`、`tex/luatex/` 内的 Lua 源码。旧 `additive-v1` 和完整资源配置不被悄悄扩展；含 Lua 的备份自动使用新格式，旧版应用会拒绝它。
- 路径穿越、符号链接、摘要/大小校验、内核保护保留。原生 `.so`、Lua 字节码 `.luc`、程序和格式文件不属于此次开放范围。
- `.lua` 是会在编译中执行的源码，请使用可信宏包。允许导入不等于包的所有原生依赖均兼容鸿蒙。

提供 `artifacts/luatex-cn-v0.4.1-user-resources.zip`：上游固定提交的 101 个未修改宏包文件及许可证，共 102 项，52 个 Lua 文件，不包含系统字体。

**作为可编辑用户层使用：** 选项 → 离线资源管理 → 用户资源 → 从 ZIP 恢复。此操作仍然是替换全部用户树；已有内容时先导出备份。不是任意上游 ZIP 都能直接导入，必须包含本应用的清单和标准资源布局。也可以通过主资源管理窗口作为只读附加包导入，但其启用需要重启，优先级低于内置和用户资源。

导入后编译依赖的是解压后的树，不依赖原 ZIP。HiShell 使用用户备份时，在已有 `TEXINPUTS` 等设置之外增加：

```sh
export LUAINPUTS=".:$TEXSTUDIO_USER_TREE/{tex,scripts}//:"
```

此变量将字面大括号交给 kpathsea 展开；解压根目录下的 `texmf` 才是 `TEXSTUDIO_USER_TREE`。这是导出的独立快照，不会自动跟随应用修改。

## CLI 使用

1. 在 TeXstudio 打开并保存主文档。
2. 选项 → CLI 自动化会话 → 导出连接文件，保存到 HiShell 可访问的目录。
3. 保持会话窗口打开，在 HiShell 运行客户端。连接文件含本次会话的令牌，关闭会话后失效；不要公开上传。

```sh
python3 texstudioctl.py --session ../texstudio-session.json status
python3 texstudioctl.py --session ../texstudio-session.json resources
python3 texstudioctl.py --session ../texstudio-session.json build --engine lualatex --wait
python3 texstudioctl.py --session ../texstudio-session.json logs
python3 texstudioctl.py --session ../texstudio-session.json cancel
```

客户端是 `tools/texstudioctl.py`，需要 HiShell 已有 Python 3。输出默认为 JSON；成功退出码 0，应用拒绝或构建失败/取消为 1，客户端连接或文件错误为 2。`--wait --timeout 300` 的超时只结束客户端等待，不自动取消应用任务。

请求经带会话令牌的本机 TCP 连接交给 Qt 主线程，再进入与 GUI 共用的 BuildManager、latexmk 和资源环境。不会在 HiShell 另起一套引擎来假装应用构建。服务只监听回环地址，连接文件不暴露任意 shell 接口。

首版范围：当前固定主文档；一次一个任务；三种引擎；最近一次任务的状态、进程退出码和最多 65,536 字符的日志尾部；运行中取消。任何已打开文档存在未保存编辑/磁盘冲突时，构建会明确拒绝，不自动保存用户修改。

目前不提供远程 open、任意命令执行、多任务历史、后台启动应用、完整结构化警告分析或 PDF 来源任务证明。`succeeded` 表示该构建链返回成功且捕获的子进程未报错，不能单靠它断言页面视觉正确。`failed` 也不意味着屏幕上旧 PDF 会消失。

## 实现与验证入口

- `src/harmonyresources.cpp`：Lua 资源配置、白名单、备份格式。
- `src/harmonyautomation.h`：单请求 JSON 传输、回环监听、认证与请求长度限制。
- `src/texstudio.cpp::harmonyAutomationSession()`：会话、构建、日志、取消与未保存编辑检查。
- `build-support/test-lua-user-resources.py`：生产资源模块八类回归。
- `build-support/test-automation.py`：实际 Qt 服务与 Python 客户端的六类协议测试。
- `build-support/device-lua-cli-probe.py`：在 HiShell 自身 UID 下调用应用并保存结果，不使用 HDC 权限执行编译。

构建：`build-support/stage-lua-cli-app.sh` → `assemble-lua-cli-package.py` → `check-lua-cli-package.py` → `sign-with-deveco.py --version 1.0.23`。不要覆盖已发布的版本产物；后续正式迭代递增版本。
