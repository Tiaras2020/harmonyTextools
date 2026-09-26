> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 1.0.30 文档生命周期与格式文件所有权修复

应用和 HNP 均为 **1.0.30**，已签名安装到当前 MatePad，并完成下述限定验收。宏包、字体和格式文件沿用 1.0.21 资源；pdfTeX/XeTeX 重新编译，不再使用未包含描述符修复的旧引擎。Lua 引擎不变。

## 报告核对与处理

### 重载与关闭崩溃

原始 1.0.29 栈崩在 `userCommandList()` 复制整个 QHash 时，尚未遍历键，不能单凭这一帧断言是具体某个 `QDocumentLineHandle` 已释放。`updateCompleter()` 与 1.0.25 的 `fileClose()` 都消费 `getListOfDocs()` 返回的文档列表。

发现确定的生命周期缺陷：共享解析器缓存 `QList<LatexDocument*>`，删除/隐藏文档等路径未完整失效缓存。抽取**实际函数实现**的宿主回归中，删除子文档后，旧实现仍返回该地址；修复实现通过。此回归使用简化所有者图，并非完整编辑器测试。

- `getListOfDocs()` 改为遍历当前文档注册表，不再读取/写入裸指针缓存；向上遍历主文档前检查它是否仍在注册表中。
- `isHidden()` 兼容尚未绑定所有者的文档；重载槽检查信号发送者。
- 磁盘与缓冲区内容相等时，只清除冲突和已修改状态，保留撤销历史，不再错误发出 `fileReloaded()` 并重建结构。

这些改动修复了可复现的失效文档缓存和多余重载路径；没有原崩溃进程的对象现场，不能宣称所有偶发崩溃只有这一种根因。

### FDSAN

旧 XeTeX 二进制 `0x432f0` 的反汇编明确是：`openfmtfile → loadfmtfile → gzclose`。这是**读取格式文件后的关闭**，不是报告推测的进程退出阶段；已有 PDF 也不能证明发生中止的那一次编译成功。

旧路径把 `fileno(FILE*)` 原样交给 `gzdopen()`，zlib 随后使用 `close()` 关闭仍有 FILE 所有权的描述符。已有源码补丁先 `dup()`，再 `fclose()` 原流，最后让 zlib 管理无标签的副本；此前交付的 pdfTeX/XeTeX 仍为旧二进制，本次将补丁编入并交付这两个引擎及其命令别名。没有关闭 FDSAN，也未把问题归结为未证实的日志管道继承。

新版 HNP 同时重建 Perl 和 latexmk/Biber 启动器的安装前缀。逐项比对旧 HNP，共 15 个条目改变，其余内容保持一致；所有条目均检查不再含旧运行包绝对前缀，ZIP CRC、签名和引擎别名一致性通过。

### CLI 错误码

`document.reload`、`document.read`、`document.open`、`master.set` 现在区分：

| 返回码 | 含义 |
| --- | --- |
| `file_missing` | 工程内路径通过策略检查，但文件已不存在；附恢复磁盘文件的提示 |
| `invalid_text_path` | 非法/越界路径、隐藏路径、符号链接、非文本类型等 |
| `document_not_open` | 文件存在，但尚未打开；用于 `document.reload` |
| `read_failed` | 文件读取失败 |

先校验完整路径，再判断存在性；`missing/../outside.tex`、悬空符号链接和链接父目录仍被拒绝。help、客户端内嵌帮助和新导出的连接 JSON 已同步。升级后请重新授权实际工程并导出连接文件。

## 验证及边界

- 宿主：旧缓存实现回归失败、修复实现通过；路径边界和悬空链接测试通过；压缩流 200 次往返与 dup/fclose/gzdopen/gzsetparams 故障清理通过；20 条命令帮助与客户端参数回归通过。
- 真机 CLI：37 项检查通过，包含 12 轮已打开文件删除→原样恢复、主动刷新、合法缺失与非法路径区分、显式重载、pdfLaTeX/XeLaTeX/LuaLaTeX 应用内清理重编。最终 PDF 提取到 `Test restored.`。
- 真机界面：关闭子文档、再关闭主文档，应用继续响应，授权工程文档列表为空。测试结束恢复自动检测主文档并撤销测试会话。
- 真机 Biber：新版前缀下 `biber --tool` 离线转换成功。
- 真机描述符机制对照：可信 Python 通过 ctypes 调用已安装 libc/zlib，在独立子进程设为 FDSAN fatal。旧交接方式在带非零所有权标签的 `gzclose` 前后以 SIGABRT（-6）终止；复制/关闭原流后标签为 0，20 轮完成。原生错误未写入捕获的 stderr，不把它表述为已取得完整的新 FDSAN faultlog。
- 旧/新完整引擎的强制 FDSAN 对照未完成：未签名旧引擎副本被系统拒绝执行。没有绕过系统策略。应用内新引擎构建验收和上述小型机制实验分别记录。
- 最初一轮测试脚本误把“恢复最初内容”当成“恢复刚删除内容”，因此正确保留了冲突；原结果留作 `cli-initial-fixture-mismatch.json`，修正用例后的完整结果为 `cli-device.json`。

本轮为限定回归，未做长期压力测试、所有外部写入时序或全量 TeX 包验收；不能以未复现宣称偶发崩溃已绝对消失。

## 交付与证据

补充审查见 [CRASH-REPORT-AUDIT-1.0.30.md](CRASH-REPORT-AUDIT-1.0.30.md)：00:43:26 / 00:46:39 的两个 Python 系统崩溃记录已通过 `legacy-dump.gz` 路径及所有权标签确认，来自本轮故意制造的失败对照，不能计作新版引擎自然故障。

- `artifacts/TeXstudioHarmony-1.0.30-arm64-device-signed.hap`
- `artifacts/texlive-1.0.30.hnp`
- `artifacts/package-check-1.0.30.json`、`artifacts/SHA256SUMS-1.0.30.txt`
- `validation/crash-fix-1.0.30/device-result.json`、`cli-device.json`、`final-device.json`、`fdsan-device.json`
- 原始三份日志、旧引擎格式关闭反汇编、源文件快照和构建日志均在 `validation/crash-fix-1.0.30/`。

可复用脚本：`build-crash-engines.sh`、`build-crash-release.sh`、`test-crash-fix.sh`、`build-crash-app.sh`、`export-crash-runtime.py`、`assemble-crash-release.py`。它们针对本版本保留旧交付；后续发布须先改为新版本，不能覆盖既有 HAP/HNP。
