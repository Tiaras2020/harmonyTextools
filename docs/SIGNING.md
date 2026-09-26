# 签名与安装

Release 中的 1.0.36 HAP 是原测试设备开发签名包；源码及恢复附件不包含私钥、密钥库、profile 或密码。原签名材料按项目所有者要求不保留。

后续开发需在自己的 DevEco Studio / 华为开发者账号为目标设备重新申请开发签名，在本地配置 signingConfigs 和 product signingConfig。仓库 build-profile.json5 是无签名模板。不要把生成密钥与口令提交到公开仓库。

推荐流程：先生成完整 unsigned HAP（tools/build.sh），再使用 DevEco 所带 hap-sign-tool 按官方开发签名流程签署这个完整包。不要只签不含 HNP 的 entry core，再向已签名包追加文件。

获取正确设备 profile 后可用 HDC 安装：

```bash
hdc list targets
hdc -t DEVICE_ID install -r /absolute/path/to/signed.hap
```

新证书与原应用签名不一致时可能拒绝覆盖安装。先备份用户项目/用户资源及可导出的设置，再按设备提示处理卸载重装。卸载会清除应用私有数据；GitHub 源码不包含用户私有对话或项目。

具体签名工具参数随 SDK 版本而异，以安装 SDK 的帮助为准。这里不提供旧账户私钥的恢复方法，因为它未备份。
