# 从 GitHub 恢复开发与构建

## 两条路线

日常修改编辑器/UI/CLI/AI 使用“本仓库源码 + Release 冻结依赖”。修改 Qt/TeX/Perl/Biber 时另下载补丁后源码恢复包；历史实现脚本作为参考，不等于已完成通用一键全量重建。

## 环境要求

- Linux x86_64，原移植使用 Ubuntu 24.04 / WSL2；建议 15 GiB 以上空闲用于应用开发，重编全套依赖需要更多。
- HarmonyOS command-line-tools 6.1.1.280（含 OpenHarmony native SDK、OHPM、Hvigor、Node），从华为开发者官方渠道安装。系统镜像/商业 SDK 不随仓库分发。
- JDK 17，Python 3.10+，Git，C/C++ 构建工具、pkg-config。Python 恢复脚本只使用标准库。

```bash
sudo apt update
sudo apt install -y build-essential cmake ninja-build pkg-config python3 git openjdk-17-jdk autoconf automake libtool
export TOOL_HOME=/absolute/path/to/command-line-tools
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
git clone https://github.com/Tiaras2020/harmonyTextools.git
cd harmonyTextools
python3 tools/restore_deps.py
bash tools/build.sh
```

`TOOL_HOME/sdk/default/openharmony/native` 必须存在。不要把 TOOL_HOME 指向 native 本身。恢复脚本按 recovery-assets.json 下载、校验 SHA256、解包并替换依赖 CMake/pkg-config 元数据中的旧路径。

只构建编辑器共享库：`bash tools/build.sh --core-only`。完整构建输出 `dist/TeXstudioHarmony-<version>-arm64-unsigned.hap`，签名另见 SIGNING.md。执行完整构建会安装工程 OHPM 依赖，需联网。

## 版本更新

1. 改 `release.json` 的 version/versionCode。只改 UI 时保持 runtimeVersion=1.0.30。
2. `scripts/release_config.py --write` 更新生成版本文件；tools/build.sh 自动执行此步骤。
3. 修改源码，构建，按变更运行必要测试。升级 HNP/引擎时必须额外验证运行包、格式、字体、宏包与 CLI。
4. 当前输出已存在时 package.py 拒绝覆盖；移动旧包或递增版本，不覆盖已发布资产。
5. 自行签名、安装、记录验收范围，更新 CHANGELOG.md / KNOWN-ISSUES.md，发布新 tag/Release。

## 依赖与离线恢复

- harmony-native-deps-1.0.36.tar.gz：Qt/Poppler 等安装树、头文件和库，日常增量开发使用。
- texlive-1.0.30.hnp：冻结运行包，生成的完整 HAP 会嵌入它。
- harmony-patched-sources-1.0.36.tar.gz：原构建环境中修改过的 Qt、TeX Live、Perl/Biber 相关源码及配置；用于依赖升级与源码对应关系保全。
- 如提供其他 source/recipe 附件，其内容由 recovery-assets.json 和说明标识。

手动下载附件到一个目录后可执行 `python3 tools/restore_deps.py --asset-dir /path/to/assets`；附加 `--sources` 解包改过的依赖源码。解包源码不自动执行历史构建脚本。

## 历史脚本的限制

`tools/legacy/` 和 `docs/porting-history/` 保存了移植过程。原脚本可能引用旧版本、旧目录、validation 输入以及本机签名配置。日常开发只从本页入口开始。历史源码/配方保全不能被称为全套依赖已在任意机器一键重建。

SDK 与 Java/Node 是用户安装的共享工具；清理某个 checkout 时不要连同其他项目使用的共享工具一起删除。
