# 本地清理与再次开发

项目所有者要求迁移后本项目本地只保留一个已签名 HAP；共享环境与其他项目不在清理范围。原签名材料明确不保留。

清理条件：源码已经推送并重新 clone 核对；所有 Release 附件远端 SHA256/大小与本地一致；新目录应用源码构建与完整 unsigned HAP 打包恢复完成；全部用户要求文档已在远端。

满足条件后删除原项目、临时发布/核验 checkout、WSL 原构建树与恢复构建树以及本项目专用签名文件。同时按所有者明确授权删除 WSL 专用 SDK ~/ohos-commandline-tools-6.1.1.280；保留 WSL 发行版、其他项目、Windows DevEco Studio 和共享 JDK/Node/Git。

之后开发：从 GitHub clone，按 BUILD.md 重新下载 SDK（或选择已有共享 SDK）并下载恢复附件。想修改引擎或 Qt 时另外下载对应源码附件。旧签名不再可恢复，按 SIGNING.md 申请新签名。

清理结果以仓库后续 LOCAL-CLEANUP-COMPLETED.md 为准；本页只描述范围和条件。
