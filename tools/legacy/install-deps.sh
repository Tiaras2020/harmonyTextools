#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/texstudio-harmony-build.sources <<'SOURCES'
Types: deb
URIs: https://mirrors.tuna.tsinghua.edu.cn/ubuntu/
Suites: noble noble-updates noble-backports noble-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
SOURCES
opts=(-o Dir::Etc::sourcelist=/tmp/texstudio-harmony-build.sources -o Dir::Etc::sourceparts=-)
apt-get "${opts[@]}" update
DEBIAN_FRONTEND=noninteractive apt-get "${opts[@]}" install -y zip unzip openjdk-17-jdk-headless cmake ninja-build meson libfontconfig1-dev libfreetype6-dev libx11-dev libxext-dev libxrender-dev libxfixes-dev libxi-dev libxkbcommon-dev libgl1-mesa-dev libglu1-mesa-dev libssl-dev gperf
