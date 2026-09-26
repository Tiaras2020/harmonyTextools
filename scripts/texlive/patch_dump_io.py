"""Idempotent, exact-context patch for TeX Live 2025 compressed dump ownership."""
import pathlib
import shutil
import sys

source = pathlib.Path(sys.argv[1])
path = source / 'texk/web2c/texmfmp.h'
text = path.read_text()
start = text.index('/* f is declared as gzFile, but we temporarily use it for a FILE *') if 'harmony_dump_io.h' not in text else None
if start is not None:
    end = text.index('#define wclose(f)', start)
    original = text[start:end]
    if original.count('gzdopen(fileno((FILE*)f)') != 2:
        raise SystemExit('Unexpected dump macros; refusing to patch')
    replacement = '''/* open_input/output provide FILE ownership; duplicate before giving to zlib. */
#include "harmony_dump_io.h"
#define wopenin(f) (open_input ((FILE**)&(f), DUMP_FORMAT, FOPEN_RBIN_MODE) \\
                    && (f = harmony_dump_open((FILE*)f, FOPEN_RBIN_MODE, 0)))
#define wopenout(f) (open_output ((FILE**)&(f), FOPEN_WBIN_MODE) \\
                     && (f = harmony_dump_open((FILE*)f, FOPEN_WBIN_MODE, 1)))
'''
    backup = path.with_suffix('.h.before-dump-ownership')
    if backup.exists():
        raise SystemExit('Backup already exists; inspect before retrying')
    shutil.copy2(path, backup)
    path.write_text(text[:start] + replacement + text[end:])
shutil.copy2(pathlib.Path(__file__).parent / 'patches/harmony_dump_io.h', source / 'texk/web2c/harmony_dump_io.h')
print('Compressed dump ownership patch ready')
