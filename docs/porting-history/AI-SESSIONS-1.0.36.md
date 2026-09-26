> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.36：会话名称与存储说明

**后续用户反馈：字体粗细问题没有修好，已停止修复并带已知问题交付；以下字体变更仅是实施记录，不代表修复成功。**

本次增加顶部对话名称及会话列表右键“重命名”，以 JSON 的 `title` 字段保存；旧会话没有 title 时继续用第一条提问作为标题。支持最长 120 字符，空名称不保存。旧消息与工程内容不受影响。当前对话正在请求模型时不开放改名。

AI 正文与输入框改为继承应用字体、普通基础字重，移除正文通用 sans-serif 覆盖；Markdown 中显式加粗及标题仍保留。设备设置的界面字体核对为 HarmonyOS Sans / 10 磅。截图能看到中英文不同字形/字重，但没有逐字形字体追踪，不能确认所有设置页的粗体都来自同一个问题；本次未修改全局字体回退或取消全局粗体。

## 本地存储

本次通过 HDC 目录查询确认设备实际路径：

`/data/app/el2/100/base/com.ohos.texstudio/preferences/texstudio/ai_workbench/`

每条记录是 `<UUID>.json`，包括 root、messages、新增的 title。启用“记录对话”才保存；工具输入/输出及 PDF 页图的 base64 内容也可包含在 messages 内。旁边 `ai-workbench-ui.ini` 保存近期工程、字体、界面选项与分隔位置。

这是应用私有数据，不在工程目录；普通文件管理器/HiShell 可能不能访问。源码通过 configBaseDir 决定目录，上述路径是当前设备经 HDC 看到的真实位置。未读取会话内容或导出密钥。

## 工程与上下文机制

选择工程只绑定规范化目录路径；未复制工程、未建立 Git 仓库、索引数据库或独立 AI 进程。请求由 Qt C++ 侧通过 HTTP 流式 Chat Completions 发送到选定服务；模型请求工具调用后，由应用执行文件读取/受控修改、日志读取、PDF 渲染和可选 Shell，再把结果返回模型。会话列表按 root 过滤。

每次请求发送现有消息、工具历史、系统提示、工具描述，以及选择启用的当前编辑器上下文。文件读取按工具请求发生，不默认加载整个工程。单次交互最多八轮工具调用。

**当前没有自动摘要压缩或按 token 计算的上下文管理。** JSON 请求超过 400,000 字节（启用视觉时 4 MiB）就提示新建对话；这是序列化请求的字节限制，不是模型 token 上限。编辑器上下文有局部截断；这不等于压缩历史。服务自身 token 上限仍可能先触发错误。

按此前用户要求，本次构建、签名、安装，不运行功能测试。安装证据见 validation/workbench-1.0.36/device-result.json。自动压缩属于后续功能，本次未实现。
