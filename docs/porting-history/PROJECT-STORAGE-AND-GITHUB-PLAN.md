> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.

# 项目整理、GitHub 迁移与 WSL 退役评估

盘点日期：2026-09-25。当前交付为 1.0.20。本轮仅生成盘点和方案，没有删除、移动构建目录，没有上传 GitHub，也没有导出或注销 WSL。按用户安排，先调整界面和操作手感，再上传。

## 结论与执行顺序

当前不满足“只保留 GitHub 源码即可完全清除 WSL”的条件。Windows 与 WSL 是独立源码副本；WSL 主构建副本没有 `.git`；现有脚本依赖历史组装目录、版本专用分支和生成在 validation 下的脚本。现有源码快照是阶段性文件集合，不是完整恢复备份。

本次应用/脚本源码范围逐文件对比完成：**11,266 项一致，24 项不同或仅单侧存在，读取错误 0**。差异主要为 IDE/机器配置、子模块 `.git` 指针、翻译生成文件；`scripts/texlive/full_resources.py` 仅在 Windows 有，必须保留。WSL 独有的 `.build-tools/python`、`local.properties` 要记录恢复方式；签名配置两侧不同，不能互相覆盖。此结论明确排除了 `build/`、依赖安装库等目录，**没有证明 build/src 内补丁已全部保存在 Windows**。完整路径与哈希见 `source-comparison.json`。

建议顺序：

1. 以本报告和机器可读清单圈定保留项，先处理可核验的重复产物；不要为省空间重建全部依赖。
2. 保留 Qt/Poppler 安装目录、TeXstudio 增量构建、SDK 和当前运行时，完成界面与操作体验调整。
3. 收敛源码差异，整理可发布仓库，改造下一版本的运行时打包入口，建立私有签名材料备份。
4. 生成恢复包，在新的构建位置完成一次源码构建、打包和必要真机回归，再发布 GitHub。
5. 恢复验收通过后，才决定压缩、迁移或完全注销旧 WSL。完整注销将删除该发行版内其他项目和用户配置，范围大于清理本项目。

如果 C 盘空间已影响工作，优先评估把现有发行版迁往非系统盘，保留当前增量开发环境；不要手工拖动 AppData 中的 VHDX。当前 E 盘剩余约 83 GiB，而 VHDX 约 71 GiB，完整复制会让 E 盘也接近满载，不能同时堆放整盘导出和多个恢复副本。

## 空间盘点

| 位置 | 本次测量 | 含义 |
|---|---:|---|
| C 盘剩余 | 5.70 GiB | Windows 可用空间 |
| E 盘剩余 | 83.09 GiB | Windows 可用空间 |
| WSL ext4.vhdx | 71.02 GiB | 文件逻辑长度，不等于可立即回收的物理空间 |
| WSL `/` | 约 70 GiB 已用 | `df` 显示；虚拟盘上限约 1 TB 不代表 C 盘有这些空间 |
| WSL 当前项目 `build` | 约 55 GiB | `du` 已分目录记录 |
| WSL OHOS 命令行工具及 SDK | 约 6.5 GiB | 不在 Windows 项目目录内 |
| Windows `artifacts/` | 9.93 GiB | 当前和历史交付包 |
| Windows `validation/` | 8.28 GiB | 包含大体积失败/中间包，并非全是小日志 |
| Windows `texstudio-harmony/` | 0.74 GiB | 源码、Git 对象和部分生成文件 |
| Windows `build-support/` | 0.10 GiB | 主要体积来自约 105 MiB 的源码 bundle |

Windows 总逻辑文件体积约 19.08 GiB；盘点未跟随目录符号链接。`validation/baseline/harmony-release-dlahjypu` 访问被拒绝，因此总量存在未计部分，不能据此自动删除该目录。

Windows 已列出 **7.83 GiB 中间二进制候选**：`validation/luahbtex/pre-audit-draft`、`validation/latexmk/incomplete-1.0.16`、`validation/latexmk/repack-1.0.17`、`validation/biber/polish-1.0.19/pre-final-app` 内的指定 HAP/HNP。清单精确到文件，保留相邻日志和 JSON；这部分释放的是 E 盘空间，不能直接缓解 C 盘压力。最终签名包和当前 HNP 不在此候选中。

WSL 虚拟盘位置：`C:\Users\1\AppData\Local\wsl\{6aea3f4d-a2cd-4775-a078-8e2c8488f7b7}\ext4.vhdx`。在 Linux 内删除文件不保证该 VHDX 马上缩小；应分别核验 Linux 可用空间和 Windows C 盘实际回收量。

## Windows 文件分工

| 目录/文件 | 定位 | 后续处理 |
|---|---|---|
| `texstudio-harmony/` | 主源码仓库，内含 TeXstudio/Poppler 子模块 | 保留，收敛修改后作为 GitHub 主仓库基础 |
| `build-support/` | 本次移植的真实构建、修复、打包、验证脚本 | 筛选后并入主仓库；不是全部可以原样当 CI 使用 |
| 根目录阶段文档 | 移植记录、使用说明和已知边界 | 主仓库 `docs/`；保留历史标识，README 只链接当前入口 |
| `artifacts/` | 安装包、HNP 和离线资源 ZIP | GitHub Releases 或本地/外置归档，不放普通 Git 历史 |
| `validation/` | 测试证据、依赖锁、下载归档、源码快照和失败产物混合 | 分成测试代码、精简证据、恢复依赖、大文件归档；不能整目录删除 |
| `logs/`、`environment-check/` | 构建和环境历史 | 保留必要失败/成功记录，排查本机路径和敏感值后发布摘要 |
| `handoff/` | 历史交接辅助文件 | 保留并检查是否被现行脚本引用 |
| `.hvigor/`、`__pycache__/`、崩溃转储 | 生成缓存/诊断 | 不发布，按需清理；崩溃转储不作为源码 |
| `DELIVERY-MANIFEST.json` | 包含历史产物名称 | 不能当实际存在文件清单；本次 inventory 为存在性证据 |

## WSL 保留与清理分级

下列相对路径均位于 `/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915/build/`。

### 界面调整期间必须保留

- `build-texstudio-ohos`（约 357 MiB）：编辑器增量构建。
- `build-qt-ohos-install`（约 233 MiB）、`build-poppler-ohos-install`（约 23 MiB）：构建和打包依赖；Qt 插件也在其中。
- `build-qt-ohos`（约 2.1 GiB）、`build-poppler-ohos`（约 72 MiB）：界面/平台相关问题仍可能需要重编，暂不为了小幅节省而删除。
- `resource-release-1.0.20`（约 2.8 GiB）：已验收的当前组装运行时。
- `resource-release-1.0.19`、`full-runtime-v2`、`build-texlive-ohos-dist`：当前脚本仍有直接依赖，不是看到有新版就可删。
- `biber-perl-1.0.19`、`biber-perl-1.0.20`、`biber-runtime-1.0.19`：前缀重建与 Biber 组装依据。
- `.build-tools`（位于项目根）、`build-hpkbuilds-ohos-install`、OHOS SDK：编译工具与依赖。

### 优先候选，但需执行前确认

- `resource-release-1.0.20-stage-failed`（约 2.8 GiB）：失败暂存副本；当前正式 1.0.20 运行时和交付包核验后可删除。
- `build-texlive-ohos-hnp`（约 2.8 GiB）：打包暂存副本；确认无构建正在使用、内容可从保留运行时再生后可删。
- `full-import-test-store`、`common-import-test-store`（各约 2.1 GiB）：导入测试库；保存测试输入、脚本、结果后可重建。
- `resource-release-1.0.6` 至 `1.0.18`：历史运行时副本；需要逐项排查脚本引用，保留恢复所需基线后删除。不要包含仍被当前流程引用的 1.0.19。
- `full-runtime-v1`、`full-resources-stage-v1`、旧验证构建：先核对 v2 是否覆盖其内容与来源记录，再决定归档或删除。

前四类候选按本次精确 `du -B1` 为 9.49 GiB；这不是 C 盘即时回收量，也不是已经授权执行的删除列表。详细字节数和更多候选见盘点目录。

### 完全清除前必须补齐恢复保全

- `build/src`（约 2.6 GiB）：含 Qt、TeX Live 等展开源码，可能含就地补丁；保存“上游精确版本/归档 SHA + 完整补丁”，或保存可校验源码归档。不能一概当下载缓存。
- `texstudio-git`（约 580 MiB）：独立源码/历史树，需检查是否有主 Windows 仓库未包含的提交或修改。
- `biber-*`、`perl-*`、`luahbtex-*`：手工配置、跨平台补丁、生成构建脚本与链接环境要可从保留材料重建。
- `build-texlive-ohos-dist`、`full-runtime-v2`、`resource-release-1.0.20`：分别承担冻结基线、资源组装基线、当前交付角色。HNP 只解决运行时恢复，不能替代编译开发包、头文件和修改后的源码。
- 发行版还有 `dev/TexHarmony`、`VSCODEFILE`、用户配置等非当前项目内容；完整清除前单独确认，不纳入本项目垃圾清理。
- 签名材料：保存实际证书、私钥/密钥库、profile、口令及关联信息到受控私有备份；不要把明文密码打入公开源码归档。只备份 build-profile 路径不足以恢复签名。

## GitHub 迁移方案

以现有 `texstudio-harmony` 为仓库基础，不在整个工作根目录直接 `git add .`。建议未来布局（本轮没有搬动现行路径）：

```text
README.md                    当前能力、安装和开发入口
LICENSE / THIRD_PARTY_NOTICES 上游及各依赖许可
release.json / dependencies.lock.json
scripts/                     可重放的构建、资源组装、打包入口
tools/                       迁入并整理的 build-support 脚本
docs/                        使用、架构、移植历史、恢复说明
tests/                       小型可分发样例、验证脚本
texstudio_harmony/           应用工程，无私有签名材料
third_party/                 锁定提交的子模块或受维护补丁
.github/workflows/           先做静态检查，再逐步接入构建
```

已发现的发布阻塞：

1. 主仓库有未提交修改；TeXstudio 子模块也有修改和未跟踪的新文件。只提交父仓库子模块指针不会保存这些修改。需要独立发布可访问的子模块提交，或审慎选择带许可的源码归并方式。
2. `texstudio_harmony/build-profile.json5` 已被跟踪且有签名密码字段。先改为无秘密模板 + 本地注入，并检查待发布历史；新增 `.gitignore` 不能消除已跟踪内容或历史中的秘密。本轮只检查字段名称，没有输出密码，也未完成全历史秘密扫描。
3. `package-resource-release.sh` 对 `1.0.20` 专用分支加入 Lua；1.0.18/19 专用分支加入 Biber。直接改成 1.0.21 会走不同分支，不能保证完整运行时。发布前应改为显式运行时配方或带校验的独立 runtime 版本，并测试新版本打包。
4. `stage-luahbtex-release.py` 克隆 1.0.19；`prepare-lua-release-perl.py` 从旧 Perl 树及 `validation/biber/polish-1.0.19/build.sh` 派生。需去除这些隐含历史状态依赖或将必要输入正式归档。
5. `env.sh` 和其他脚本固定用户目录、盘符和 SDK 路径。需要模板化/参数化，在非原路径进行一次恢复试验。
6. 父仓库 MIT 许可证不覆盖 TeXstudio、Qt、Poppler、Perl、TeX 包及字体各自的许可。保留各组件许可证、来源与修改信息，发布二进制时核对对应源码和再分发条件。当前不是完整许可审计。

普通 GitHub 仓库阻止大于 100 MiB 的单文件；HAP/HNP 应放 Releases。当前签名 HAP 约 1.36 GiB、HNP 约 1.29 GiB，均低于 Release 单文件 2 GiB 上限。源码 bundle 约 105 MiB 也不应直接提交普通 Git。

本机测试签名 HAP 可能受设备 profile 限制，不能把“真机能安装”直接当成“所有用户可安装”。对外发布前区分源码、通用构建说明、开发者自签步骤和适用设备的安装包。

## WSL 退役验收条件

全部完成后再安排清除：

- 两端源码差异已逐项归类，并保留 Windows 和 WSL 独有修改；完整补丁、子模块提交及来源可追溯。
- 已验收运行时、最终 HAP/HNP、校验和、资源依赖锁和必要测试证据有一份不在该 WSL 内的校验备份。
- 签名与其他项目资料已私有备份；没有仅存在于待注销发行版内的必要文件。
- 新环境从保留材料构建界面、组装当前运行时、生成下一版本 HAP，并完成验签及必要真机回归。
- 实测恢复成功后，将本文件的“未具备清除条件”改为带证据的已通过状态。

WSL 官方支持 export/import；unregister 会永久移除发行版内数据。暂不提供自动清除脚本，避免把待核验条件误当执行授权。本轮没有恢复演练，因此不能声称 WSL 已可安全清空。

## 证据与官方依据

- 本地盘点：`validation/storage-audit-2026-09-25/`，含 Windows 文件体积、大文件清单、Git 状态、WSL 分目录占用和源码对比。
- [GitHub 大文件规则](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
- [GitHub Releases 大小限制](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [WSL 导出、导入与注销](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)
- [WSL 磁盘空间管理](https://learn.microsoft.com/en-us/windows/wsl/disk-space)
