/* Native public HNP entry point; no shell quoting or shebang dependency. */
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
    char **args = calloc((size_t)argc + 4, sizeof(*args));
    if (!path || !args) { perror("latexmk: allocation"); return 127; }
    snprintf(path, length, "%s%s%s", prefix, old_path ? ":" : "", old_path ? old_path : "");
    if (setenv("PATH", path, 1) != 0) { perror("latexmk: PATH"); return 127; }
    /* TeXstudio can stop this group together with all compiler descendants. */
    if (getpgrp() != getpid() && setpgid(0, 0) != 0) {
        perror("latexmk: process group"); return 127;
    }
    /* Nested bibliography tools must remain in the group stopped by TeXstudio. */
    char group[32];
    snprintf(group, sizeof(group), "%ld", (long)getpgrp());
    if (setenv("HARMONY_BUILD_PROCESS_GROUP", group, 1) != 0) {
        perror("latexmk: process group environment"); return 127;
    }
    args[0] = HARMONY_RUNTIME_ROOT "/bin/perl";
    args[1] = "-I" HARMONY_RUNTIME_ROOT "/share/latexmk";
    args[2] = "-MHarmonyCwd";
    args[3] = HARMONY_RUNTIME_ROOT "/share/latexmk/latexmk.pl";
    for (int i = 1; i < argc; ++i) args[i + 3] = argv[i];
    execv(args[0], args);
    int error = errno;
    perror("latexmk: cannot start bundled Perl");
    return error == ENOENT ? 127 : 126;
}
