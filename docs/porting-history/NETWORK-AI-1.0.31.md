> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.31：中文在线校对、DeepSeek 与外部终端

应用版本 1.0.31，复用内容不变的 1.0.30 HNP。本轮不继续处理用户暂缓的文档关闭问题，也不代表全量兼容性复测。

## 使用

- **DeepSeek**：设置 TeXstudio → 语言检查 → AI，选择 `DeepSeek V4.1-Flash`，模型 `deepseek-flash`，接口 `https://api.deepseek.com/chat/completions`。API Key 由用户在设备上填写，不放入聊天、测试证据或仓库。打开“向导 → AI 聊天”。当前预设关闭思考模式。需要流式输出时在聊天窗口齿轮选项中启用；启用函数调用时使用完整 JSON 响应，避免把不完整工具参数当成完整调用。真实账号鉴权、额度、模型输出尚待用户提供设备端配置后验证。
- **中文校对**：选中文字 → 向导 → 中文校对。先检查过滤后的预览，再点开始；只有此时才把选中内容发送到界面所示服务。默认 LanguageTool 公共 HTTPS 服务，可改为自己的兼容服务，地址单独保存在 `harmony-proofread.ini`。结果列出相对于选择内容的行号、原文和建议，不自动修改源文件。
- **外部终端**：工具 → 打开外部终端，选“复制 cd 命令并打开”，允许系统打开 HiShell，在空闲 shell 粘贴并执行。也可只打开终端。HiShell 可能复用当前终端窗口；如果正在运行 AI/其他程序，请先新建终端标签再粘贴。当前没有自动执行命令或自动切换目录。

中文功能是在线规则校对，不是完整离线中文字典。实测能发现“迫不急待”“再接再励”“按步就班”，也存在漏检；英文 Hunspell 检查继续保留。LaTeX 过滤保持位置，屏蔽常见公式、命令名、引用和文件参数，但不是完整 TeX 解析器，复杂自定义宏应先核对预览。

## 实现与复现

- Qt 5.12.12 OHOS 网络库改为链接现有 OpenSSL 3.5.8 静态库；使用 curl 分发的 Mozilla 根证书，保持证书与主机名验证，不忽略 TLS 错误。证书来源和摘要见源码 `utilities/certificates/README.md`。
- `harmonynetwork.h` 提供 TLS 初始化及按 SSE 事件边界收包；中文 UTF-8、跨包 JSON、CRLF、正文里的 `data:` 不再被错误拆开。请求增加超时、取消与状态恢复。AI/校对窗口按可用屏幕调整大小。
- `harmonyproofread.h` 实现显式发送的选区校对；终端使用 QtOhosExtras 的 `startAbility`，目录通过 shell 引号安全转义后复制。
- 禁止桌面 TeXstudio 更新检查向鸿蒙版提示不适用的桌面升级；鸿蒙版继续使用本项目安装包升级。
- WSL 构建：先 `bash build-support/build-network-tls.sh`，再 `bash build-support/build-network-app.sh`；宿主回归为 `bash build-support/test-network.sh`（使用 `/mnt/e/CodeProjects/harmonytexlive` 路径）。Windows 组装、签名分别为 `python build-support/assemble-network-package.py`、`python build-support/sign-with-deveco.py --version 1.0.31`。脚本拒绝覆盖已有交付，应先明确保存或迁走旧候选。`prepare-network.py` 是一次性初始补丁工具，不应在当前源码上重跑。

## 验证范围

证据入口：`validation/network-1.0.31/`，截图在 `validation/compat-review-2026-09-25/network-*.png`，详细状态以 `device-result.json` 为准。

- 宿主通过 SSE 各种分包位置、逐字节 UTF-8、CRLF、多行事件、截断/清空、URL 策略及 LaTeX 掩码测试。
- 真机真实 HTTPS 中文校对获得纠错建议；自签名不可信 TLS 服务被拒绝。
- 真机回环模拟 AI 服务通过中文分段流式显示、完整回复、取消及后续请求。模拟服务只记录请求路径、长度、时间，不记录密钥或请求正文。
- 真机从应用身份打开 HiShell，复制并执行 cd，pwd 确认进入当前文档目录。
- 尚未完成真实 DeepSeek 账号对话、长时间弱网、所有供应商和全量 TeX 回归。不能把回环 AI 模拟测试等同于真实模型验收。

官方参考：[DeepSeek API](https://api-docs.deepseek.com/zh-cn/)、[LanguageTool 支持语言](https://dev.languagetool.org/languages)、[curl CA extract](https://curl.se/docs/caextract.html)。
