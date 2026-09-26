> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# CLI 冲突恢复（1.0.29）

新增 `document.reload`，连接 JSON 与离线 `help` 现在包含 20 条命令。构建拒绝及排队后出现编辑的任务状态附恢复建议。

## 推荐流程

先用 `document.read --path main.tex` 查看缓冲区、modified、conflict、revision，并与磁盘文件比较。保留需要的本地编辑后，再决定采用哪份内容。

```sh
# 默认保护未保存内容；仅重载已打开的工程内文本文件
python3 texstudioctl.py --session texstudio-session.json document.reload --path main.tex

# 明确采用磁盘内容，REV 必须来自刚才的 document.read
python3 texstudioctl.py --session texstudio-session.json document.reload --path main.tex --discard-local --expected-revision REV
```

显式丢弃缺少 revision 返回 `expected_revision_required`；缓冲区内容已变化返回 `revision_mismatch`。客户端也会在发送前检查缺失参数。新指令仍可能遇到忙碌、路径不合法、文档未打开、编码不合法、读取失败或超过 4 MiB 等错误，不应盲目重试丢弃。

默认重载遇到不同于磁盘的未保存内容返回 `unsaved_edits`；只有 conflict、但缓冲区没有本地修改时允许重载。文件不存在时须先恢复磁盘文件；重载不创建、保存或删除工程文件。

返回包含新的 revision、modified、conflict，以及成功时的 discardedLocalChanges。重载将经过校验的磁盘快照直接应用到缓冲区，不进行第二次读取；替换不同内容会清除旧撤销历史，尽量保留光标位置。外部程序继续写入时，后续刷新仍可能再次产生冲突；此命令不锁定磁盘。

## 自动解除一致冲突

文件变化通知及 CLI 刷新时，使用编辑器当前编码读取磁盘，统一 CRLF/CR/LF 后逐字比较；保留空格、缩进及末尾换行差异。完全一致时清除 conflict，并将当前内容标记为已保存，保留文本、光标和撤销历史。这不会把不同内容强行合并，也不会把无效编码视作一致。文件删除、读取失败或过大时不自动解除。

`unsaved_edits.recoveryHint` 提示先读取并保留编辑，再决定恢复；提示不是自动丢弃授权。AI 不应见到提示就直接强制重载。

## 验证

证据位于 `validation/reload-cli-1.0.29/`，以 `device-result.json` 为最终状态。主机覆盖编码/BOM/换行/空格/截断/大小/缺失文件、CLI 参数映射以及 20 条帮助清单。真机用隔离工程核对默认保护、旧 revision 拒绝、错误读取保护、显式恢复、恢复后的应用内构建及内容一致时解除冲突。

运行包仍为 1.0.21；本次不代表所有引擎与宏包的全量重新验收。会话沿用 1.0.28 的后台操作方式，升级后重新导出连接 JSON。
