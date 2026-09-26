"""Use Perl's existing emulation when Harmony lacks glibc langinfo extensions."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
root=Path(__file__).resolve().parents[1]
work=Path(sys.argv[1])
with tarfile.open(root/'validation/latexmk/downloads/perl-5.40.3.tar.xz') as archive:
    original=archive.extractfile('perl-5.40.3/perl_langinfo.h').read()
    locale=archive.extractfile('perl-5.40.3/locale.c').read()
source=work/'locale.c'
if '/* Harmony: optional langinfo item */' in source.read_text():
    source.chmod(source.stat().st_mode | 0o200)
    source.write_bytes(locale)
locale_cross=locale.replace(b'#include "config.h"',b'#ifdef USE_CROSS_COMPILE\n#include "xconfig.h"\n#else\n#include "config.h"\n#endif')
locale_cross_official=locale.replace(b'#include "config.h"',b'#ifndef USE_CROSS_COMPILE\n#  include "config.h"\n#else\n#  include "xconfig.h"\n#endif')
assert source.read_bytes() in (locale,locale_cross,locale_cross_official),'Unexpected locale.c changes'
source.chmod(source.stat().st_mode | 0o200)
source.write_bytes(locale_cross)
cross_original=original.replace(b'#include "config.h"',b'#ifdef USE_CROSS_COMPILE\n#include "xconfig.h"\n#else\n#include "config.h"\n#endif')
text=cross_original.decode()
for category in ('ADDRESS','IDENTIFICATION','MEASUREMENT','NAME','PAPER','TELEPHONE'):
    old=f'#if ! defined(HAS_NL_LANGINFO) || ! defined(LC_{category})'
    assert text.count(old)==1
    text=text.replace(old,old+f' || defined(NO_LOCALE_{category})')
target=work/'perl_langinfo.h'
assert target.read_bytes() in (original,cross_original,text.encode()),'Unexpected local header changes'
target.chmod(target.stat().st_mode | 0o200)
target.write_text(text)
(root/'validation/latexmk/locale-patch.json').write_text(json.dumps({'source':'perl_langinfo.h',
    'beforeSha256':hashlib.sha256(original).hexdigest(),'afterSha256':hashlib.sha256(text.encode()).hexdigest(),
    'scope':'Use existing Perl langinfo emulation for six disabled optional locale categories; retain standard locale and Unicode'},indent=2)+'\n')
