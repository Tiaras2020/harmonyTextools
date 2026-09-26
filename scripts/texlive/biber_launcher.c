/* Public HNP entry point for the bundled Biber interpreter and modules. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#ifndef HARMONY_RUNTIME_ROOT
#error HARMONY_RUNTIME_ROOT must name the versioned HNP installation
#endif
int main(int argc, char **argv)
{
    const char *old_path = getenv("PATH");
    const char prefix[] = HARMONY_RUNTIME_ROOT "/bin";
    size_t length = sizeof(prefix) + (old_path ? strlen(old_path) + 1 : 0);
    char *path = malloc(length);
    char **args = calloc((size_t)argc + 5, sizeof(*args));
    if (!path || !args) { perror("biber: allocation"); return 127; }
    snprintf(path, length, "%s%s%s", prefix, old_path ? ":" : "", old_path ? old_path : "");
    if (setenv("PATH", path, 1) != 0) { perror("biber: PATH"); return 127; }
    const char *inherited = getenv("HARMONY_BUILD_PROCESS_GROUP");
    char *end = NULL;
    errno = 0;
    long group = inherited ? strtol(inherited, &end, 10) : -1;
    int nested = inherited && *inherited && end && !*end && !errno && group > 1 && group == (long)getpgrp();
    if (!nested && getpgrp() != getpid() && setpgid(0, 0) != 0) {
        perror("biber: process group"); return 127;
    }
    args[0] = HARMONY_RUNTIME_ROOT "/bin/perl";
    args[1] = "-I" HARMONY_RUNTIME_ROOT "/share/latexmk";
    args[2] = "-MHarmonyCwd";
    args[3] = "-I" HARMONY_RUNTIME_ROOT "/share/biber/lib";
    args[4] = HARMONY_RUNTIME_ROOT "/share/biber/bin/biber";
    for (int i = 1; i < argc; ++i) args[i + 4] = argv[i];
    execv(args[0], args);
    int error = errno;
    perror("biber: cannot start bundled Perl");
    return error == ENOENT ? 127 : 126;
}
