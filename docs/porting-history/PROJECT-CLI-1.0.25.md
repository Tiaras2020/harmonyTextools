> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 工程 CLI 与中文拼写适配（1.0.25）

应用运行包保持 1.0.21；本次修改应用侧会话、构建调度和拼写检查。正式验收状态以 `../validation/project-cli-1.0.25/device-result.json` 为准。

2026-09-25：最终签名包已安装；HiShell 调用应用服务的 25 项探针检查全部通过，另完成未保存缓冲区读取、构建拒绝、撤销恢复及关闭会话失效检查。真机编辑器中确认纯中文没有英文误报红线，英文错误仍有提示。

## 使用

在 TeXstudio 打开已保存的工程文件，选择“选项 → CLI 自动化会话”，确认允许访问的工程目录。目录选择窗口中的“授权此目录”是授权边界。导出连接文件到 HiShell 可访问的位置，保持会话面板打开；该面板不会阻挡编辑器。关闭面板后令牌失效，旧连接文件不能连接新会话。

更新 HiShell 中的客户端为本项目 `tools/texstudioctl.py`。例如在工程目录运行：

```sh
python3 texstudioctl.py --session ../texstudio-session.json project.info
python3 texstudioctl.py --session ../texstudio-session.json files.list --path . --limit 100
python3 texstudioctl.py --session ../texstudio-session.json document.read --path chapters/intro.tex --start 1 --count 100
python3 texstudioctl.py --session ../texstudio-session.json document.open --path chapters/intro.tex
python3 texstudioctl.py --session ../texstudio-session.json master.set --path main.tex
python3 texstudioctl.py --session ../texstudio-session.json build --path main.tex --engine xelatex --wait
python3 texstudioctl.py --session ../texstudio-session.json job.logs --job TASK_ID --offset 0 --limit 16384
python3 texstudioctl.py --session ../texstudio-session.json diagnostics --job TASK_ID
python3 texstudioctl.py --session ../texstudio-session.json artifact.info --job TASK_ID
python3 texstudioctl.py --session ../texstudio-session.json cancel --job TASK_ID
```

`capabilities` 返回实际支持的命令，`documents.list` 返回已打开文件的未保存/冲突状态。`document.read` 优先读取编辑缓冲区，返回文本内容摘要 revision 和磁盘 SHA256；未打开文件按 UTF-8 读取，其他编码先在编辑器打开。单文件上限 4 MiB，读取至多 2000 行，响应片段上限 256 KiB；文件列表按目录分页，不一次递归扫描全部工程。打开与主文件切换目前仅允许 `.tex`。

文件接口只接受工程内相对路径，拒绝 `..`、绝对路径、隐藏路径和任一层符号链接，读取限制为 TeX/文献/Lua/常见文本等后缀。没有文件写入、删除或任意 shell 命令接口。**这限制的是 CLI 文件接口，不是 TeX/Lua 引擎的文件系统沙箱**：编译仍按应用现有权限执行工程代码。

任意已打开编辑器存在未保存编辑或外部冲突时，构建返回 `unsaved_edits`，不会自动保存。用户可继续编辑，完成保存后再请求构建。引擎固定为 pdflatex、xelatex、lualatex。CLI 的 latexmk 流程跳过桌面“编译前处理”钩子，避免旧日志驱动默认引擎/BibTeX 重复执行，普通 GUI 构建设置保持原行为。

## 任务、日志与 PDF

每次构建返回独立 job ID；会话内保留最近 20 个任务，关闭后清除，不是跨重启数据库。任务结束时间、引擎、主文件、退出状态分别记录；`--wait` 查询提交的任务，不会误跟随后一个任务。

每个任务保留最多 262144 个 UTF-16 单元的日志尾部；`job.logs` 的 offset/nextOffset 按 UTF-16 单元计数，截断时明确返回 truncated。`logs` 保留旧客户端的最近 65536 字符接口。`diagnostics` 是有限的文件:行号及警告解析，完整信息仍在原始日志中。

`artifact.info` 比较构建前、完成时和查询时的主文件同目录 PDF 摘要，区分“构建成功”“PDF 改变”和“当前 PDF 仍与该任务结束时一致”。失败后留下的旧 PDF 不会被标为成功。增量编译的 PDF 未变化会返回 `unchanged_or_not_proven`，不伪称重新生成。自定义输出目录、页数与视觉正确性尚未由该接口验证；超出 128 MiB 的 PDF 不计算摘要。该命令不会主动打开 PDF 预览。

## 中文红色波浪线

当前上游使用 Hunspell 的词典接口：[TeXstudio 配置说明](https://github.com/texstudio-org/texstudio/blob/master/utilities/manual/source/configuration.md)。本次先解决英文词典对中文的误报：汉字片段不交给英文拼写词典，中文中间的字母词段仍交给现有词典检查。例如“概率空间与测度”不应出现英文拼写红线，“中文mispelll中文”仍能提示英文错误。

支持简体、繁体和扩展汉字。不关闭英文拼写检查，不关闭 TeX 语法错误提示，也没有加入一个虚假的“中文词典”。**这属于中英混排兼容，不具备中文错别字、词义或语法纠错能力。** 真正的中文校对需另接分词与校对引擎，再处理专业术语词表。

## 验证材料

宿主边界与中英文规则：`validation/project-cli-1.0.25/host-tests.log`；真实 Qt TCP 与客户端异常请求检查：`protocol-tests.json`。真机探针在 HiShell 自身 UID 下调用应用服务，编译由应用 BuildManager 执行，结果与候选版差异记录在该目录。没有把宿主检查当成真机验收。

重建入口：`build-support/stage-project-cli-app.sh` → `assemble-project-cli-package.py` → `check-project-cli-package.py` → `sign-with-deveco.py --version 1.0.25`。当前版本文件不可直接覆盖；后续发布递增版本。`prepare-project-cli.py` 为本轮准备脚本，后续开发不应未经核对重放模板覆盖现有改动。
