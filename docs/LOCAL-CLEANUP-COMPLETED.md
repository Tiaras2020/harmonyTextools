# 本地迁移清理完成

日期：2026-09-26。按项目所有者授权完成。

## 清理前验证

- 应用源码、说明、功能文档、更新日志和历史移植记录已推送；重新 clone 并拉取至提交 a8d9a98。
- 六个 Release 附件全部上传，GitHub 存储 SHA256 和大小与本地逐一一致，详见 release-asset-verification.json；公开 SHA256SUMS.txt 下载已核对。
- 新目录下使用冻结依赖完整编译应用并生成未签名 HAP；4,283 个应用源文件与远端 clone 一致，版本和嵌入 HNP 哈希正确。未运行设备功能回归，未从头重编全部 Qt/TeX 依赖。

## 已完成清理

- Windows 原项目目录及发布、核验 checkout、构建产物、缓存和历史本地文件已删除，只保留下面一个签名 HAP。
- WSL 原构建目录 texstudio-harmony-main-20260915 和恢复验证目录 harmonyTextools-restore-check 已删除。
- 按明确授权删除 WSL 专用 SDK ohos-commandline-tools-6.1.1.280。
- 本项目专用证书、CSR、私钥库和签名 profile 已删除，无私钥备份。后续重新申请签名。
- 保留 Ubuntu-24.04 发行版、其他项目、共享环境和 Windows DevEco Studio。

## 本地唯一保留的交付文件

路径：`E:\CodeProjects\harmonytexlive\TeXstudioHarmony-1.0.36-arm64-device-signed.hap`

大小：1,494,567,624 字节。

SHA256：`51e07585d7a8a038a1cafeede05d1c5e94fb4c8b4de54f3ac459a9642d91083d`。

清理前后哈希一致。以后修改请重新 clone，并从 [BUILD.md](BUILD.md) 开始恢复。三个已知问题仍以 [KNOWN-ISSUES.md](KNOWN-ISSUES.md) 为准。

本次删除了 WSL 文件，没有执行发行版注销或 VHDX 压缩；虚拟磁盘宿主文件不一定立即缩小。
