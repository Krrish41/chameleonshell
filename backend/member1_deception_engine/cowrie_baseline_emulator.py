"""
Cowrie Baseline Emulator
Simulates legacy medium-interaction Cowrie honeypot behavior (static fs.pickle,
rigid hardcoded command outputs, zero IMDSv2 support, lack of cross-turn persistence)
for live A/B side-by-side thesis comparison.
"""
import time
from typing import Dict, Any


class CowrieBaselineEmulator:
    """Emulates static Cowrie behavior to demonstrate fingerprinting vulnerability."""

    def __init__(self):
        # Static non-persistent mock filesystem state
        self.cwd = "/root"
        self.history = []

    def execute(self, cmd_line: str) -> Dict[str, Any]:
        start = time.perf_counter()
        cmd = cmd_line.strip()
        self.history.append(cmd)

        stdout = ""
        stderr = ""
        exit_code = 0

        # Static fingerprintable command map (typical Cowrie defaults)
        if cmd == "uname -a":
            stdout = "Linux svr04 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1 x86_64 GNU/Linux\n"
        elif cmd == "uname":
            stdout = "Linux\n"
        elif cmd == "whoami":
            stdout = "root\n"
        elif cmd == "id":
            stdout = "uid=0(root) gid=0(root) groups=0(root)\n"
        elif cmd == "pwd":
            stdout = f"{self.cwd}\n"
        elif cmd == "uptime":
            # Notice static/stale uptime typical of Cowrie
            stdout = " 14:22:01 up 12 days,  3:14,  1 user,  load average: 0.00, 0.01, 0.05\n"
        elif cmd == "date":
            # Often static or unsynced in basic honeypots
            stdout = "Mon Oct 12 14:22:01 UTC 2020\n"
        elif cmd.startswith("ls"):
            # Static file list, never persists created files!
            stdout = "Desktop  Downloads  test.txt\n"
        elif cmd.startswith("cat /proc/cpuinfo"):
            stdout = "processor\t: 0\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 45\nmodel name\t: Intel(R) Xeon(R) CPU E5-2620 0 @ 2.00GHz\n"
        elif cmd.startswith("cat /proc/meminfo"):
            stdout = "MemTotal:        2052444 kB\nMemFree:          124580 kB\nBuffers:           24580 kB\nCached:           845820 kB\n"
        elif "169.254.169.254" in cmd:
            # Cowrie does NOT emulate AWS IMDSv2! Returns connection refused or command not found
            stderr = "curl: (7) Failed to connect to 169.254.169.254 port 80: Connection refused\n"
            exit_code = 7
        elif "aws" in cmd or "kubectl" in cmd or "docker" in cmd:
            stderr = f"bash: {cmd.split()[0]}: command not found\n"
            exit_code = 127
        elif cmd.startswith("touch") or cmd.startswith("mkdir") or ">" in cmd:
            # Cowrie appears to succeed but silently loses state on the next turn!
            stdout = ""
        elif cmd.startswith("cat test.txt"):
            stdout = "Sample test file content in Cowrie.\n"
        elif cmd.startswith("cat"):
            # Created files are missing
            target = cmd.split()[-1]
            stderr = f"cat: {target}: No such file or directory\n"
            exit_code = 1
        elif cmd == "ps" or cmd == "ps aux":
            stdout = (
                "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
                "root         1  0.0  0.1  24128  1892 ?        Ss   Oct12   0:01 /sbin/init\n"
                "root       412  0.0  0.1  45124  2104 ?        Ss   Oct12   0:00 /usr/sbin/sshd -D\n"
            )
        else:
            stderr = f"bash: {cmd.split()[0]}: command not found\n"
            exit_code = 127

        elapsed = (time.perf_counter() - start) * 1000
        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "latency_ms": round(elapsed, 2),
            "state_persisted": False,  # Core Cowrie limitation!
            "path_taken": "cowrie_static_vfs",
            "cwd": self.cwd
        }
