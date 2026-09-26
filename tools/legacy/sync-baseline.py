"""WSL: preserve previous files and incrementally sync only reviewed paths."""
import hashlib
import json
import os
import pathlib
import shutil
import datetime

delivery = pathlib.Path(os.environ['DELIVERY_ROOT'])
repo = pathlib.Path(os.environ['BUILD_REPO'])
source = delivery / 'texstudio-harmony'
out = delivery / 'validation/baseline/sync'
out.mkdir(parents=True, exist_ok=True)
paths = ['release.json', 'scripts/release_config.py', 'scripts/common/build_texlive_hnp.sh',
         'scripts/texlive/build_pack_texmf.sh', 'third_party/texstudio/src/harmonyRelease.h',
         'third_party/texstudio/src/utilsSystem.cpp', 'texstudio_harmony/AppScope/app.json5',
         'dependencies.lock.json', 'scripts/verify_archives.py', 'scripts/texlive/download_texlive.sh',
         'scripts/qt/download_qt.sh', 'scripts/texstudio/build_texstudio.sh']
paths += ['scripts/texlive/build_texlive_ohos.sh', 'scripts/texlive/patch_dump_io.py',
          'scripts/texlive/patch_luahbtex_io.py',
          'scripts/texlive/patches/harmony_dump_io.h']
paths += ['third_party/texstudio/src/' + name for name in
          ('CMakeLists.txt', 'texstudio.cpp', 'harmonyresources.h', 'harmonyresources.cpp', 'harmonyresourcesdialog.cpp', 'harmonyuserresourcesdialog.cpp')]
paths += ['third_party/texstudio/src/' + name for name in ('harmonyclipboard.h','harmonymarkdown.h','harmonychinesedict.h','harmonyaitools.h','harmonyaiworkbench.h','harmonyproofpanel.h','spellerutility.cpp','configmanager.cpp','texstudio.h')]
paths += ['third_party/texstudio/utilities/dictionaries/' + name for name in ('zh_CN.aff','zh_CN.dic','LICENSE-jieba.txt','README-zh_CN.md')]
paths += ['third_party/texstudio/src/harmonylightpalette.h', 'third_party/texstudio/src/harmonyfloatingpanel.h', 'third_party/texstudio/images-ng/harmony-orca.svg', 'third_party/texstudio/images-ng/harmony-proof.svg']
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
paths += ['third_party/texstudio/src/quazip/quazip/CMakeLists.txt']
paths += ['third_party/texstudio/src/harmonyautomation.h']
paths += ['third_party/texstudio/src/' + name for name in ('harmonydialoglayout.h', 'configdialog.cpp', 'tabdialog.cpp', 'aichatassistant.cpp')]
paths += ['third_party/texstudio/texstudio.qrc']
paths += ['third_party/texstudio/utilities/dictionaries/' + name for name in ('en_US.aff', 'en_US.dic', 'README_others.txt')]
paths += ['texstudio_harmony/AppScope/resources/base/media/' + name for name in ('icon_background.svg', 'layered_image.json')]
paths += ['third_party/texstudio/src/' + name for name in ('buildmanager.cpp', 'buildmanager.h', 'harmonyprocess.h')]
paths += ['scripts/texlive/latexmk_launcher.c']
paths += ['scripts/texlive/biber_launcher.c', 'scripts/texlive/HarmonyCwd.pm']
paths += ['scripts/texlive/resource-policy.json']
paths += ['third_party/texstudio/translation/texstudio_zh_CN.ts']
paths += ['third_party/texstudio/src/' + name for name in
          ('texstudio.h', 'configmanager.cpp', 'dblclickmenubar.cpp', 'dblclickmenubar.h',
           'editors.cpp', 'structuretreeview.cpp', 'latexeditorview.cpp', 'pdfviewer/PDFDocument.cpp', 'pdfviewer/PDFDocument.h')]
paths += ['third_party/texstudio/src/' + name for name in ('harmonyproject.h', 'harmonyspell.h', 'spellerutility.cpp')]
paths += ['third_party/texstudio/src/qcodeedit/lib/' + name for name in ('qeditor.cpp','qeditor.h','qreliablefilewatch.cpp','qreliablefilewatch.h')]
paths += ['third_party/texstudio/src/harmonyclihelp.h']
paths += ['third_party/texstudio/src/harmonyreload.h']
paths += ['third_party/texstudio/src/' + name for name in ('harmonynetwork.h', 'harmonyproofread.h', 'aichatassistant.h')]
paths += ['third_party/texstudio/CMakeLists.txt', 'third_party/texstudio/utilities/certificates/cacert.pem']
report = []
paths += ['third_party/texstudio/src/updatechecker.cpp']
for relative in paths:
    src, dst = source / relative, repo / relative
    before = hashlib.sha256(dst.read_bytes()).hexdigest() if dst.exists() else None
    after = hashlib.sha256(src.read_bytes()).hexdigest()
    if before != after:
        if dst.exists():
            backup = out / 'previous' / stamp / relative
            if backup.exists():
                raise SystemExit('Previous sync backup exists: ' + relative)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest() == after
    report.append({'path': relative, 'before': before, 'after': after})
(out / ('report-' + stamp + '.json')).write_text(json.dumps(report, indent=2) + '\n')
print('Reviewed source files synchronized:', len(paths))
