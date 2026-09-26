#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${TOOL_HOME:?Set TOOL_HOME to the HarmonyOS command-line-tools directory}"
export OHOS_SDK="$TOOL_HOME/sdk/default/openharmony"
export NATIVE_OHOS_SDK="$OHOS_SDK/native"
export PATH="$TOOL_HOME/bin:$TOOL_HOME/tool/node/bin:$NATIVE_OHOS_SDK/build-tools/cmake/bin:$PATH"
export OHOS_TARGET_ARCH=arm64-v8a
export JOBS="${JOBS:-4}"
python3 "$ROOT/scripts/release_config.py" --write
bash "$ROOT/scripts/texstudio/build_texstudio.sh"
if [[ "${1:-}" == --core-only ]]; then exit 0; fi
bash "$ROOT/scripts/common/copy_libs_entry.sh"
cp "$NATIVE_OHOS_SDK/llvm/lib/aarch64-linux-ohos/libc++_shared.so" "$ROOT/texstudio_harmony/entry/libs/arm64-v8a/"
cd "$ROOT/texstudio_harmony"
ohpm install
hvigorw --mode module -p module=entry@default -p product=default -p requiredDeviceType=2in1 assembleHap --no-daemon
python3 "$ROOT/tools/package.py"
