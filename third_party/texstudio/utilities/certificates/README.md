# HTTPS trust anchors

`cacert.pem` is the Mozilla CA extract distributed by curl at https://curl.se/ca/cacert.pem.
Downloaded 2026-09-26 (device local date); SHA-256 verified against https://curl.se/ca/cacert.pem.sha256:

`a41b5d356aea97a529fe27e0f7316d2f9d946d75927476cf9cf1b90637d00505`

The PEM header retains its upstream source and extraction date. The source is Mozilla NSS's `certdata.txt`, linked in that header; source licensing information is available at https://www.mozilla.org/MPL/2.0/. This bundle is used as an additional public trust store for the HarmonyOS Qt build, where system certificate directories may not be accessible. Peer and hostname verification remain enabled. Future releases should refresh the bundle from the same source, record the new digest, and rerun trusted/untrusted certificate tests.
