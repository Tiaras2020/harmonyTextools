#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export TOOL_HOME=/home/tiarasubuntu2404/ohos-commandline-tools-6.1.1.280/command-line-tools
export OHOS_SDK="$TOOL_HOME/sdk/default/openharmony"
export NATIVE_OHOS_SDK="$OHOS_SDK/native"
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$TOOL_HOME/bin:$TOOL_HOME/tool/node/bin:$NATIVE_OHOS_SDK/build-tools/cmake/bin:$JAVA_HOME/bin:$PATH"
export JOBS=6
export OHOS_TARGET_ARCH=arm64-v8a
export BUILD_REPO=/home/tiarasubuntu2404/dev/texstudio-harmony-main-20260915
export DELIVERY_ROOT=/mnt/e/CodeProjects/harmonytexlive
PACKAGE_VERSION="$(python3 "$DELIVERY_ROOT/build-support/release_config.py")"
export PACKAGE_VERSION
export PATH="$BUILD_REPO/.build-tools:$PATH"
