/* Transfer an opened FILE to zlib without transferring a FILE-owned descriptor.
 * The caller must not use stream after this call, including on failure. */
#ifndef HARMONY_DUMP_IO_H
#define HARMONY_DUMP_IO_H
#include <stdio.h>
#include <unistd.h>
#include <zlib.h>

static gzFile harmony_dump_open(FILE *stream, const char *mode, int writing)
{
    int fd = dup(fileno(stream));
    int closed = fclose(stream);
    gzFile result;
    if (fd < 0) return NULL;
    if (closed != 0) {
        close(fd);
        return NULL;
    }
    result = gzdopen(fd, mode);
    if (!result) {
        close(fd);
        return NULL;
    }
    if (writing && gzsetparams(result, 1, Z_DEFAULT_STRATEGY) != Z_OK) {
        gzclose(result);
        return NULL;
    }
    return result;
}
#endif
