#!/usr/bin/env bash
# Full isolated B3.2 runtime; packaging and signing are separate steps.
set -euo pipefail
source /mnt/e/CodeProjects/harmonytexlive/build-support/env.sh
[[ "$PACKAGE_VERSION" == 1.0.18 ]] || { echo 'This runtime is pinned to the 1.0.18 HNP prefix.' >&2; exit 1; }
# Use the reviewed lock, never silently resolve newer CPAN versions.
for script in prepare-biber-remaining.py prepare-biber-xs.py build-biber-native.py prepare-biber-xml.py prepare-biber-bibtex.py configure-biber-remaining-xs.py prepare-biber-encodings.py build-biber-openssl.py prepare-biber-tls.py; do
    python3 "$DELIVERY_ROOT/build-support/$script"
done
out="$DELIVERY_ROOT/validation/biber"
if ! bash "$out/xs-bootstrap/build.sh"; then
    if grep -q 'Your Makefile has been rebuilt' "$out/xs-bootstrap/build.log"; then
        bash "$out/xs-bootstrap/build.sh"
    else
        exit 1
    fi
fi
for script in assemble-biber-runtime.py audit-biber-licenses.py prepare-biber-test-support.py test-biber-dependencies.py test-biber-workflow.py test-biber-remaining-upstream.py test-biber-tls.py test-biber-launchers.py; do
    python3 "$DELIVERY_ROOT/build-support/$script"
done
bash "$DELIVERY_ROOT/build-support/run-biber-perl-qemu.sh" "$out/runtime-data-smoke.pl" > "$out/runtime-data-result.json"
python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["passed"]' "$out/runtime-data-result.json"
