# 1.0.36 移植阶段交付

含 TeXstudio 应用源码、功能/操作/恢复构建说明、更新日志和已修改第三方源码。

**已知问题未修复：** 字体粗细；CLI 多工程显式主文档后关闭文档可能崩溃；改变整体字号后 AI 导航图标不居中。详见仓库 docs/KNOWN-ISSUES.md。

- 应用 1.0.36；冻结运行包 1.0.30。
- 签名 HAP 包含 HNP，原开发签名可能只适用于原测试设备。
- 原签名私钥不保留；后续自行申请签名，可能需卸载重装。
- 日常开发：clone 后安装 SDK，运行 tools/restore_deps.py 和 tools/build.sh。
- 恢复包大小与 SHA256 见 recovery-assets.json / SHA256SUMS.txt。
- 1.0.34–1.0.36 未执行功能回归；迁移恢复构建的范围见 docs/VALIDATION.md。

附件包含预编译依赖及对应补丁后源码。legacy-texstudio-source 是旧独立源码树的保全，不是主开发入口。个人项目、API 密钥、CLI 连接令牌、签名私钥不在发布范围。
