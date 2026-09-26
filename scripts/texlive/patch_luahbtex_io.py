"""Keep libc FILE ownership separate from zlib's descriptor on OHOS."""
from pathlib import Path
import sys

source = Path(sys.argv[1]) / 'texk/web2c/luatexdir/tex/texfileio.c'
text = source.read_text()
marker = '/* HarmonyOS: zlib owns only a duplicate, libc owns the FILE. */'
if marker not in text:
    anchor = '#define COMPRESSION "R3"'
    assert text.count(anchor) == 1
    helper = '''
#include <unistd.h>
/* HarmonyOS: zlib owns only a duplicate, libc owns the FILE. */
static gzFile harmony_gzdopen(FILE **stream, const char *mode)
{
    int fd = dup(fileno(*stream));
    gzFile result = fd < 0 ? NULL : gzdopen(fd, mode);
    if (result == NULL) {
        if (fd >= 0) close(fd);
        fclose(*stream);
        *stream = NULL;
    }
    return result;
}
'''
    text = text.replace(anchor, anchor + '\n' + helper)
    for mode in ('rb', 'wb'):
        old = f'gz_fmtfile = gzdopen(fileno(*f), "{mode}" COMPRESSION);'
        assert text.count(old) == 1
        text = text.replace(old, f'gz_fmtfile = harmony_gzdopen(f, "{mode}" COMPRESSION);\n        if (gz_fmtfile == NULL) return 0;')
    old = '    (void) f;\n    gzclose(gz_fmtfile);'
    assert text.count(old) == 1
    text = text.replace(old, '    int result = gzclose(gz_fmtfile);\n    gz_fmtfile = NULL;\n    if (fclose(f) != 0 || result != Z_OK) {\n        fprintf(stderr, "Failed to close LuaTeX format file.\\n");\n        uexit(1);\n    }')
    source.write_text(text)
print('LuaHBTeX format descriptor ownership patch applied:', source)
