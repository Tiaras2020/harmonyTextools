# 第三方来源和许可

此仓库基于 https://github.com/baitianyu-kun/texstudio-harmony ，继续进行了 HarmonyOS 移植和产品功能开发。来源提交见 docs/UPSTREAM-SOURCES.json；上游说明保留在 docs/upstream/README.md。

- TeXstudio：https://github.com/texstudio-org/texstudio ，以 third_party/texstudio 的 COPYING/许可证为准（GPL）。本仓库直接提供修改后的源码。
- Poppler：原适配分支 https://github.com/baitianyu-kun/poppler ，许可见 third_party/poppler/COPYING（GPL）。本仓库直接提供修改后的源码。
- Qt HarmonyOS 5.12.12：源码及修改后的工作树随 Release 的 patched-sources 附件保留，具体 LGPL/GPL/第三方许可见 qtbase/LICENSE* 与各模块说明。
- TeX Live / pdfTeX / XeTeX / LuaHBTeX：项目冻结来源和归档哈希见 dependencies.lock.json，补丁后 TeX Live 源码在 Release 附件；包、字体与工具采用各自许可。
- Perl、Biber、OpenSSL、libxml2、libxslt、FreeType、HarfBuzz 等：对应源码、COPYING/LICENSE 与移植配方在源码恢复包或 scripts/、tools/legacy/ 中。
- 中文词典与英文词典：保留 third_party/texstudio/utilities/dictionaries 中许可证与说明。

根目录 MIT LICENSE 不会把第三方重新许可为 MIT。恢复二进制依赖的配套来源保留在 Release 附件；这份索引不是完整法律审计。商业分发或修改再发布前需按各组件实际许可证履行源码、告知及其他要求。
