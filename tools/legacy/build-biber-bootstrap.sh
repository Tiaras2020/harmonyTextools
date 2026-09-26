#!/usr/bin/env bash
# Isolated B3.2 dependency milestone; this does not create a release HNP/HAP.
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
for script in resolve-biber-dependencies.py prepare-biber-xs.py build-biber-native.py prepare-biber-xml.py prepare-biber-bibtex.py; do
    python3 "$DELIVERY_ROOT/build-support/$script"
done
out="$DELIVERY_ROOT/validation/biber/xs-bootstrap"
if ! bash "$out/build.sh"; then
    # EUMM deliberately exits when Time::HiRes regenerates its Makefile.
    # Retry only that known transition; a second failure remains fatal.
    if grep -q 'Your Makefile has been rebuilt' "$out/build.log"; then
        bash "$out/build.sh"
    else
        exit 1
    fi
fi
for test in test-biber-xs.sh test-biber-xml.sh test-biber-bibtex.sh; do
    bash "$DELIVERY_ROOT/build-support/$test"
done
