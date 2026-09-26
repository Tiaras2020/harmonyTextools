> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 外部修改刷新与构建反馈（1.0.26）

2026-09-25：签名包已安装；21 项真机探针、未保存冲突测试及 PDF 最新文本检查通过，宿主监听与客户端退出码测试通过。

验收状态以 `../validation/refresh-cli-1.0.26/device-result.json` 为准，文件不存在则尚未完成验收。运行包继续使用 1.0.21。

## 外部修改

鸿蒙版对已打开文件按内容 SHA256 检查变化，每 500 毫秒检查一次，连续两次观察一致后通知编辑器。应用正常运行时通常约 0.5–1 秒刷新；系统挂起应用时不承诺实时。等长修改、保留修改时间的修改、原子替换均不再依赖原有的一秒时间戳过滤。检查仅针对已打开文件，不递归扫描工程。

编辑器没有未保存内容时自动重新加载，并尽量保持光标位置；有未保存内容或已存在冲突时保留缓冲区并标记冲突。文件删除也标记冲突，不自动将缓冲区写回磁盘。重新加载会清除旧撤销历史。不要在编译期间持续改输入文件；本实现不创建整个工程的原子快照。

CLI 的 `document.read`、`document.open`、`documents.list`、`master.set`、构建操作会先主动检查文件变化；新增 `project.refresh` 主动检查授权目录中已打开文件并返回状态。外部 AI 可直接写磁盘文件，随后调用刷新，再构建。未保存内容或冲突仍返回 `unsaved_edits`，不自动保存。

## 成功与失败

**`ok` 仅代表请求处理成功，不代表编译成功。** 为保持协议兼容，查询失败任务仍可以返回 `ok: true`。

- `terminal: false`、`buildSucceeded: null`、`exitCode: null`：正在排队或运行。
- `terminal: true`、`buildSucceeded: true`：构建成功。
- `terminal: true`、`buildSucceeded: false`：失败或取消，结合 `state`、`exitCode` 判断。

更新 `tools/texstudioctl.py` 后，`build --wait` 与 `build.clean --wait` 在任务失败或取消时返回非零进程退出码。单独提交构建返回成功仅表示已排队。

## 最终轮诊断与缓存恢复

构建结束时捕获主文件同目录最终 `.log`，保存到任务记录，后续任务不会覆盖它。`diagnostics` 优先解析这份最终轮日志，避免展示中间轮已解决的重编译警告。`source` 标明来自 `final_engine_log` 还是 `build_output`，完整多轮记录仍在 `job.logs`。未捕获最终日志时回退到最后一个构建规则的输出，解析仍为有限诊断，不保证覆盖所有工具、换行警告和自定义输出目录。

latexmk 因旧失败记录而不重新运行时，返回 `cached_previous_failure` 提示。可执行：

```sh
python3 texstudioctl.py --session ../texstudio-session.json project.refresh
python3 texstudioctl.py --session ../texstudio-session.json build.clean --path main.tex --engine xelatex --wait
```

`build.clean` 只删除指定主文件的 `.fdb_latexmk`，再以 `-g` 强制重编；不使用 `-C` 或 `-gg`，不删除源文件、手写文献文件和原 PDF。失败时原 PDF 可能仍存在，必须检查构建结果。禁止通过符号链接选择待清理缓存。
