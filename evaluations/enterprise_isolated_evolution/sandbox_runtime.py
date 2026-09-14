"""Public Linux x86-64 process restrictions for a frozen E16 planner.

This is an isolation primitive, not study approval or a scoring implementation.
The trusted launcher must bind this file, all planner files, and inputs before
fresh private curation. Apply ``lock_process`` before consuming any observation.
"""

from __future__ import annotations

import ctypes
import errno
import os
import platform
from pathlib import Path
import stat


# Linux x86-64 syscall numbers. Architecture mismatch fails closed. The x32 ABI
# is rejected separately rather than allowed to bypass these comparisons.
DENIED_SYSCALLS = {
    "socket": 41, "connect": 42, "accept": 43, "sendto": 44,
    "recvfrom": 45, "sendmsg": 46, "recvmsg": 47, "shutdown": 48,
    "bind": 49, "listen": 50, "getsockname": 51, "getpeername": 52,
    "socketpair": 53, "setsockopt": 54, "getsockopt": 55,
    "clone": 56, "fork": 57, "vfork": 58, "execve": 59,
    "ptrace": 101, "pivot_root": 155, "chroot": 161, "mount": 165,
    "umount2": 166, "reboot": 169, "init_module": 175,
    "delete_module": 176, "kexec_load": 246, "add_key": 248,
    "request_key": 249, "keyctl": 250, "unshare": 272, "accept4": 288,
    "perf_event_open": 298, "name_to_handle_at": 303,
    "open_by_handle_at": 304, "setns": 308, "process_vm_readv": 310,
    "process_vm_writev": 311, "kcmp": 312, "finit_module": 313,
    "memfd_create": 319, "kexec_file_load": 320, "bpf": 321,
    "execveat": 322, "userfaultfd": 323, "io_uring_setup": 425,
    "io_uring_enter": 426, "io_uring_register": 427, "clone3": 435,
}


class SockFilter(ctypes.Structure):
    """One classic BPF instruction accepted by Linux seccomp."""

    _fields_ = [("code", ctypes.c_ushort), ("jt", ctypes.c_ubyte),
                ("jf", ctypes.c_ubyte), ("k", ctypes.c_uint32)]


class SockFprog(ctypes.Structure):
    """A bounded classic BPF program for the current thread."""

    _fields_ = [("len", ctypes.c_ushort),
                ("filter", ctypes.POINTER(SockFilter))]


def lock_process() -> dict[str, object]:
    """Irreversibly deny new processes, sockets, and escape-related syscalls.

    Call before starting threads. The frozen planner must be single-threaded;
    clone denial also prevents starting new threads. All descendant execution
    is denied and no privileged control endpoint should be inherited.
    """
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("The reviewed sandbox requires Linux x86_64")
    if os.getuid() != 65534 or os.getgid() != 65534:
        raise RuntimeError("The planner must use the frozen unprivileged UID/GID")
    if len(list(Path("/proc/self/task").iterdir())) != 1:
        raise RuntimeError("The planner must have exactly one thread at lock")
    inherited = []
    for fd in Path("/proc/self/fd").iterdir():
        try:
            value = os.readlink(fd)
        except FileNotFoundError:
            continue  # The directory iterator's own transient descriptor.
        if int(fd.name) > 2:
            inherited.append((fd.name, value))
    if inherited:
        raise RuntimeError("Unexpected inherited file descriptors")
    stdio = {}
    for fd in range(3):
        details = os.fstat(fd)
        if stat.S_ISFIFO(details.st_mode):
            stdio[str(fd)] = "pipe"
        elif stat.S_ISCHR(details.st_mode) and details.st_rdev == os.makedev(1, 3):
            stdio[str(fd)] = "dev-null"
        else:
            raise RuntimeError("Stdio must be ordinary pipes or /dev/null")
    os.umask(0o077)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
        raise OSError(ctypes.get_errno(), "no_new_privs failed")
    # seccomp_data.arch is at byte 4 and .nr at byte 0.
    program = [
        SockFilter(0x20, 0, 0, 4),
        SockFilter(0x15, 1, 0, 0xC000003E),
        SockFilter(0x06, 0, 0, 0x80000000),  # KILL_PROCESS
        SockFilter(0x20, 0, 0, 0),
        SockFilter(0x35, 0, 1, 0x40000000),
        SockFilter(0x06, 0, 0, 0x00050000 | errno.EPERM),
    ]
    for number in sorted(set(DENIED_SYSCALLS.values())):
        program.extend([SockFilter(0x15, 0, 1, number),
                        SockFilter(0x06, 0, 0, 0x00050000 | errno.EPERM)])
    program.append(SockFilter(0x06, 0, 0, 0x7FFF0000))  # ALLOW
    filters = (SockFilter * len(program))(*program)
    descriptor = SockFprog(len(program), filters)
    if libc.prctl(22, 2, ctypes.byref(descriptor), 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "seccomp installation failed")
    status = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key in {"NoNewPrivs", "Seccomp", "Seccomp_filters", "CapEff",
                       "CapPrm", "CapBnd", "CapAmb"}:
                status[key] = value.strip()
    if status.get("NoNewPrivs") != "1" or status.get("Seccomp") != "2":
        raise RuntimeError("Kernel did not report mandatory process restrictions")
    if any(int(status.get(key, "1"), 16) != 0
           for key in ("CapEff", "CapPrm", "CapBnd", "CapAmb")):
        raise RuntimeError("A planner capability set is nonempty")
    return {"uid": os.getuid(), "gid": os.getgid(), "kernel_status": status,
            "blocked_syscall_count": len(DENIED_SYSCALLS), "stdio": stdio}


def container_options() -> list[str]:
    """Return fixed Docker restrictions; caller adds only reviewed RO mounts.

    Do not add sockets, devices, network, privileged flags, host namespaces,
    writable host mounts, volumes-from, inherited environment, or credentials.
    Container image and exact mount/input inventories require independent locks.
    """
    return [
        "--network=none", "--ipc=none", "--cgroupns=private",
        "--user=65534:65534", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges=true", "--pids-limit=32",
        "--memory=256m", "--memory-swap=256m", "--cpus=1",
        "--ulimit=core=0:0", "--ulimit=nofile=128:128", "--log-driver=none",
        "--tmpfs=/tmp:rw,nosuid,nodev,noexec,size=16m,mode=700,uid=65534,gid=65534",
        "--tmpfs=/work:rw,nosuid,nodev,noexec,size=64m,mode=700,uid=65534,gid=65534",
        "--workdir=/work", "--env=HOME=/nonexistent",
        "--entrypoint=/usr/local/bin/python",
    ]
