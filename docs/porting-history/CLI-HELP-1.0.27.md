> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# CLI 帮助与自描述连接文件（1.0.27）

已签名安装，完成真机离线帮助、连接文件说明、远程帮助及兼容调用检查；未在本次纯帮助更新中重复全引擎编译验收。

## 不记命令也能使用

只需保留新版 `tools/texstudioctl.py` 一个文件。帮助已内置，无需旁边放额外的 JSON，也不需要应用正在运行。

```sh
python3 texstudioctl.py help
python3 texstudioctl.py help build
python3 texstudioctl.py help build.clean
python3 texstudioctl.py help document.read --json
python3 texstudioctl.py help --json
```

不传参数或使用 `--help` 也能查看说明。执行应用命令仍要传 `--session`。示例中的路径、引擎、任务 ID、行号可以按工程修改。`help --json` 适合直接让本地 AI 读取，输出不含连接令牌。

## 导出的连接 JSON

1.0.27 在原有 `protocol`、`host`、`port`、`token` 之外增加 `appVersion`、`projectRoot` 和 `help`。原有客户端仍可使用它。`help` 包含 19 个命令的用途、参数、可复制的命令行、无令牌的结构化请求示例，以及构建结果含义和推荐流程。

`help` 是说明，不是可执行配置。可以调整示例里的文件路径、引擎和行号，但修改命令名称或说明不会给应用增加新功能；客户端也不会自动运行这些示例。连接字段由应用生成，不应随意修改。连接 JSON 含令牌，关闭会话后失效。

直接使用 TCP 的工具还可以请求 `{"command":"help","token":"当前会话令牌"}` 获取同一清单；`capabilities` 列出的命令才是当前连接应用实际支持的命令。客户端的 `help` 使用内置说明，不读取连接文件。

客户端帮助兼容 1.0.26 的构建/刷新接口；重新导出带说明的连接文件需要 1.0.27。`ok` 仍只表示请求处理成功，任务结果必须看 `terminal`、`buildSucceeded`、`state`。

## 后续维护

编辑 `tools/texstudio-cli-help.json`，运行 `python build-support/generate-cli-help.py`，同步生成独立 Python 客户端内置清单与 `harmonyclihelp.h`。构建入口 `stage-help-cli-app.sh` 自动执行生成。新增接口时仍需同时实现服务端行为；清单不会生成接口实现。

验收证据在 `validation/help-cli-1.0.27/`，最终状态以 `device-result.json` 为准。
