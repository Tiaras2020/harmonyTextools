> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 新增崩溃报告的独立核对

本次从用户指定的设备 `~/.dsh/work/crash-evidence/` 复制了 9 个文件（含 README），保存至 `validation/crash-audit-1.0.30/`。原始文件保持原样；其中 README 是待核对的报告，并非已确认结论。本次没有重新运行故意触发中止的实验，也没有发布新版本。

## 两个 Python 中止来自预期失败对照

两份转储均明确记录：

| 时间（设备本地） | PID | 描述符对应文件 | FILE 地址 |
| --- | --- | --- | --- |
| 2026-09-26 00:43:26.426 | 25757 | `4 -> /storage/Users/currentUser/Download/ProjectCli30/legacy-dump.gz` | `0x5adf2426c8` |
| 2026-09-26 00:46:39.757 | 27347 | 同上 | `0x61942426c8` |

这是上一轮由本项目测试脚本 `build-support/device-fdsan-ownership.py` 主动制造的失败：Python ctypes 调用 libc/zlib，在独立子进程设置 FDSAN fatal，将仍归 FILE 所有的描述符传给 gzdopen，再调用 gzclose。该脚本执行过两次，因此产生两次预期 SIGABRT。

第二次转储的所有权标签 `0x01000061942426c8`，与 `validation/crash-fix-1.0.30/fdsan-device.json` 的十进制 `72058013135152840` 完全一致。两份转储中的实际错误均为 fd **4**，报告套用旧 XeTeX 的 fd 3 不准确。文件路径、所有权标签和调用栈共同确认了来源，并非仅凭时间猜测。

修复交接方式的工作进程在同一 zlib 上完成 20 轮、退出码 0。这些转储证明旧交接方式会触发所有权检查；**不能证明新版 TeX 引擎修复无效，也不能证明普通 Python 使用遭到波及**。此前交付说明虽记载了 SIGABRT 对照，没有清楚列出其会留下的系统崩溃记录，造成误解，应由本项目说明清楚。

zlib 出现在关闭栈中，不等于缺陷属于 zlib。当前已证实的问题是调用方把仍属于 FILE 的描述符交给会 close 它的 gzip 流；修复在 TeX 调用方完成。单次错误所有权关闭也足以触发 FDSAN，不能直接称为已经发生两次关闭。

## 1.0.30 已有应用内编译验收

`validation/crash-fix-1.0.30/cli-device.json` 记录应用版本 1.0.30，以下三个清理重编任务均为 `state=succeeded / buildSucceeded=true / exitCode=0`：

- pdfLaTeX：设备本地 00:43:06.696—00:43:07.396。
- XeLaTeX：00:43:07.531—00:43:08.641。
- LuaLaTeX：00:43:08.853—00:43:10.358。

时间由记录中的 UTC 加 8 小时换算。它们早于两个 Python 对照转储。因此“1.0.30 尚未跑构建”与现有记录不符。这些限定成功用例不代表长期稳定性或所有工程均已验证。

## 关闭文件崩溃确实存在，但根因措辞须收窄

新取得的 `texstudio-1.0.29-fileClose-001816.log` 确认 00:18:16.401、版本 1.0.29、QtMainThread、SIGSEGV@0x28。与 1.0.25 一样落在 `fileClose -> isHidden -> QList::contains -> QListData::begin`。这支持同一故障路径持续存在，不能仅凭栈认定一定是重入，也不能从故障地址直接还原所有对象状态。

报告强调的 `QMetaObject::activate` 偏移相同，两次属于同一个 Qt5Core 构建；这种相同本身不能定位应用根因。

1.0.30 已移除 `getListOfDocs()` 的裸指针列表缓存，改为从当前注册文档遍历，并为 `isHidden()` 增加所有者为空的检查。宿主回归确实证明旧缓存会返回已移出注册表的文档地址。**这修复了一个确定的生命周期缺陷，但没有原进程对象现场，不能断言完全解释两次原崩溃。** 新提供的 00:18 转储版本仍为 1.0.29，不是修复版再次崩溃的证据。

用户补充的“第一次关闭图标恢复、第二次关闭崩溃”应单独纳入回归。上轮真机测试是关闭子文档再关闭主文档，不等同于完整复现这一操作。当前不能宣称这个精确序列已经通过新版测试。

图标也不宜凭昵称确定含义：标签页通过 `isContentModified()` 显示 modified 图标；结构树另有 masterdoc 主文档图标。没有崩溃前画面，不能把“爆炸图标”直接认定为冲突或主文档。下一次验收应记录图标所在位置、首次关闭的提示和所选动作、当前版本，以及第二次关闭操作。

## 其他不成立的推断

- 原 XeTeX 崩溃地址的匹配二进制反汇编是 `openfmtfile -> loadfmtfile -> gzclose`，属于读取格式文件后的关闭；调用栈底部出现 libc 启动函数不能证明发生在进程退出阶段。
- HiShell 21 次未复现只是条件差异线索，不能据此证明应用继承了错误的日志管道描述符。当前证据已在引擎内部格式流交接处定位所有权问题。

后续优先补测 1.0.30 中用户描述的完整两次关闭序列，并明确区分实际使用崩溃与故意制造的失败对照；不要因这两份 Python 转储重复修改 zlib 或关闭 FDSAN。
