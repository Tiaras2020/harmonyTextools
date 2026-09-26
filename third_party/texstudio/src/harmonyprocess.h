#ifndef HARMONYPROCESS_H
#define HARMONYPROCESS_H

#include <signal.h>
#include <sys/types.h>
#include <unistd.h>

namespace HarmonyProcess {
// Only kill a group owned by the actual child, never the application's group.
inline bool killChildGroup(pid_t child)
{
    if (child <= 1 || child == getpgrp() || getpgid(child) != child) return false;
    return ::kill(-child, SIGKILL) == 0;
}
}
#endif
