# CLI 和 AI 的区别

CLI 是本地程序调用应用功能的接口；AI 对话是应用调用用户选择的模型服务。两者授权、会话和命令不同，AI 的 Shell 选项不等于 CLI 开放 Shell。

## HiShell / 本地 AI 使用 CLI

在应用“选项 → CLI 自动化会话”中选择工程，导出连接 JSON。将本仓库 tools/texstudioctl.py 放到终端可访问位置；不需要安装额外 Python 库。

```bash
python3 tools/texstudioctl.py help
python3 tools/texstudioctl.py help --json
python3 tools/texstudioctl.py --session session.json capabilities
python3 tools/texstudioctl.py --session session.json documents.list
python3 tools/texstudioctl.py --session session.json project.refresh
python3 tools/texstudioctl.py --session session.json build --path main.tex --engine xelatex --wait
```

先用 `help <命令>` 获取该版本准确参数；build.clean、document.reload 等恢复命令的参数不要凭猜测。连接 JSON 内含机器可读帮助和临时令牌，不要提交到 GitHub。关闭会话后令牌失效。

`ok:true` 表示请求被处理，**不是构建成功**。必须看 terminal、buildSucceeded、state、exitCode。编译遇到未保存编辑/冲突时不会静默覆盖；按 blockers 和 recoveryHint 操作，必要时读取文件 revision 后重载。diagnostics 使用最终引擎日志；失败缓存给出 build.clean 指引。

外部 AI 可修改磁盘上的工程文本；应用刷新须处理与未保存缓冲区的冲突。不要把关闭多工程主文档当作自动恢复冲突的万能方法，已知可能崩溃。

## 应用内 AI 实现

C++ 工作台绑定工程目录，HTTP 流式发送消息并执行模型请求的工具。可读编辑缓冲区、精确版本校验修改、创建文件、读日志、渲染现有 PDF 页图。没有复制工程，没有本地大模型进程或向量数据库。

“记录对话”启用时，每条会话存为 configBaseDir/ai_workbench/<UUID>.json，包含 root、title、messages，图像可能以 base64 存入。UI 偏好位于旁边 ai-workbench-ui.ini。HarmonyOS 中这是应用私有数据，不在工程目录，普通终端不一定能读取。

当前不做上下文自动压缩。请求体上限 400,000 字节，视觉开启时 4 MiB；模型 token 上限可能先触发。新对话不会继承历史，需要自行交接摘要与文件路径。
