"""
Fast-Path Router (<8ms deterministic execution)
Parses standard POSIX operations and executes directly against the Virtual State Tree (VST)
without invoking the LLM, defeating timing side-channel detection.
"""
import time
import shlex
import re
from typing import Dict, Any, Tuple
from .vst_state_tree import VSTStateTree


class FastPathRouter:
    """Executes deterministic shell commands against VSTStateTree in <8ms."""

    SUPPORTED_COMMANDS = {
        "ls", "cd", "pwd", "cat", "touch", "mkdir", "rm", "echo",
        "whoami", "id", "uname", "uptime", "date", "ps", "env",
        "export", "history", "clear", "hostname", "head", "tail", "cp", "mv"
    }

    def __init__(self, state_tree: VSTStateTree):
        self.state_tree = state_tree

    def can_handle(self, command_line: str) -> bool:
        """Determines if the command qualifies for sub-8ms Fast-Path deterministic execution."""
        cleaned = command_line.strip()
        if not cleaned:
            return True
        # If it contains pipes to non-fastpath, background operators, or complex substitutions, use slow path
        if "|" in cleaned or "`" in cleaned or "$(" in cleaned:
            # Simple grep pipe allowed: e.g. "cat /etc/passwd | grep ubuntu"
            if re.search(r"\|\s*grep\b", cleaned):
                return True
            return False

        # Extract primary binary
        first_token = cleaned.split()[0].split("/")[-1]
        return first_token in self.SUPPORTED_COMMANDS

    def execute(self, command_line: str) -> Dict[str, Any]:
        """Executes the command against VST and returns structured execution payload."""
        start_time = time.perf_counter()
        cleaned = command_line.strip()
        
        # Update bash history
        self.state_tree.append_history(cleaned)

        if not cleaned:
            return {
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "path_taken": "fast_path",
                "cwd": self.state_tree.current_working_dir
            }

        # Check for simple grep pipe
        if "|" in cleaned and "grep" in cleaned:
            parts = cleaned.split("|", 1)
            left_res = self._execute_single(parts[0].strip())
            if left_res["exit_code"] != 0:
                elapsed = (time.perf_counter() - start_time) * 1000
                left_res["latency_ms"] = round(elapsed, 2)
                return left_res
            pattern = parts[1].replace("grep", "").strip().strip("'\"")
            filtered = [line for line in left_res["stdout"].split("\n") if pattern in line]
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "stdout": "\n".join(filtered) + ("\n" if filtered else ""),
                "stderr": "",
                "exit_code": 0 if filtered else 1,
                "latency_ms": round(elapsed, 2),
                "path_taken": "fast_path",
                "cwd": self.state_tree.current_working_dir
            }

        res = self._execute_single(cleaned)
        elapsed = (time.perf_counter() - start_time) * 1000
        res["latency_ms"] = round(elapsed, 2)
        res["path_taken"] = "fast_path"
        res["cwd"] = self.state_tree.current_working_dir
        return res

    def _execute_single(self, cmd_str: str) -> Dict[str, Any]:
        try:
            tokens = shlex.split(cmd_str)
        except Exception:
            tokens = cmd_str.split()

        if not tokens:
            return {"stdout": "", "stderr": "", "exit_code": 0}

        # Handle redirection: e.g. echo "xyz" > file.txt or >> file.txt
        redirect_out = None
        append_out = False
        if ">" in tokens or ">>" in tokens:
            new_tokens = []
            idx = 0
            while idx < len(tokens):
                tok = tokens[idx]
                if tok == ">>" and idx + 1 < len(tokens):
                    redirect_out = tokens[idx + 1]
                    append_out = True
                    idx += 2
                    continue
                elif tok == ">" and idx + 1 < len(tokens):
                    redirect_out = tokens[idx + 1]
                    append_out = False
                    idx += 2
                    continue
                elif tok.startswith(">>"):
                    redirect_out = tok[2:]
                    append_out = True
                    idx += 1
                    continue
                elif tok.startswith(">"):
                    redirect_out = tok[1:]
                    append_out = False
                    idx += 1
                    continue
                new_tokens.append(tok)
                idx += 1
            tokens = new_tokens

        cmd = tokens[0].split("/")[-1]
        args = tokens[1:]

        stdout = ""
        stderr = ""
        exit_code = 0

        if cmd == "pwd":
            stdout = f"{self.state_tree.current_working_dir}\n"

        elif cmd == "whoami":
            stdout = f"{self.state_tree.current_user}\n"

        elif cmd == "id":
            u = self.state_tree.current_user
            uid = self.state_tree.current_uid
            gid = self.state_tree.current_gid
            stdout = f"uid={uid}({u}) gid={gid}({u}) groups={gid}({u}),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),120(lxd)\n"

        elif cmd == "uname":
            if "-a" in args:
                stdout = f"Linux {self.state_tree.hostname} {self.state_tree.kernel} #15-Ubuntu SMP PREEMPT_DYNAMIC Wed Oct 2 14:22:18 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux\n"
            elif "-r" in args:
                stdout = f"{self.state_tree.kernel}\n"
            elif "-m" in args:
                stdout = "x86_64\n"
            else:
                stdout = "Linux\n"

        elif cmd == "hostname":
            stdout = f"{self.state_tree.hostname}\n"

        elif cmd == "date":
            # Realistic UTC date string
            stdout = time.strftime("%a %b %d %H:%M:%S UTC %Y\n", time.gmtime())

        elif cmd == "uptime":
            uptime_secs = int(time.time() - self.state_tree.boot_time)
            days = uptime_secs // 86400
            hours = (uptime_secs % 86400) // 3600
            minutes = (uptime_secs % 3600) // 60
            cur_time = time.strftime("%H:%M:%S", time.gmtime())
            stdout = f" {cur_time} up {days} days, {hours:02d}:{minutes:02d},  1 user,  load average: 0.14, 0.08, 0.03\n"

        elif cmd == "cd":
            target = args[0] if args else "/home/ubuntu"
            ok, msg = self.state_tree.change_dir(target)
            if not ok:
                stderr = f"{msg}\n"
                exit_code = 1

        elif cmd == "ls":
            show_all = "-a" in args or "-la" in args or "-al" in args
            long_fmt = "-l" in args or "-la" in args or "-al" in args
            path_args = [a for a in args if not a.startswith("-")]
            target = path_args[0] if path_args else ""
            ok, msg = self.state_tree.list_dir(target, show_all=show_all, long_format=long_fmt)
            if not ok:
                stderr = f"{msg}\n"
                exit_code = 2
            else:
                stdout = f"{msg}\n" if msg else ""

        elif cmd == "cat":
            if not args:
                stderr = "cat: missing file operand\n"
                exit_code = 1
            else:
                for a in args:
                    ok, msg = self.state_tree.read_file(a)
                    if not ok:
                        stderr += f"{msg}\n"
                        exit_code = 1
                    else:
                        stdout += msg if msg.endswith("\n") else msg + "\n"

        elif cmd == "touch":
            if not args:
                stderr = "touch: missing file operand\n"
                exit_code = 1
            else:
                for a in args:
                    ok, _ = self.state_tree.read_file(a)
                    if not ok:
                        self.state_tree.write_file(a, "")

        elif cmd == "mkdir":
            if not args:
                stderr = "mkdir: missing operand\n"
                exit_code = 1
            else:
                parents = "-p" in args
                target_dirs = [a for a in args if not a.startswith("-")]
                for d in target_dirs:
                    ok, msg = self.state_tree.make_dir(d, parents=parents)
                    if not ok:
                        stderr += f"{msg}\n"
                        exit_code = 1

        elif cmd == "rm":
            recursive = "-r" in args or "-rf" in args or "-fr" in args
            targets = [a for a in args if not a.startswith("-")]
            if not targets:
                stderr = "rm: missing operand\n"
                exit_code = 1
            else:
                for t in targets:
                    ok, msg = self.state_tree.remove(t, recursive=recursive)
                    if not ok and "-f" not in args:
                        stderr += f"{msg}\n"
                        exit_code = 1

        elif cmd == "echo":
            content = " ".join(args)
            # Remove bounding quotes if present
            if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
                content = content[1:-1]
            stdout = f"{content}\n"

        elif cmd == "ps":
            stdout = (
                "  PID TTY          TIME CMD\n"
                "  724 ?        00:00:01 sshd\n"
                "  892 ?        00:00:02 nginx\n"
                "  915 ?        00:00:03 postgres\n"
                "14201 pts/0    00:00:00 bash\n"
                "14890 pts/0    00:00:00 ps\n"
            )

        elif cmd == "env":
            lines = [f"{k}={v}" for k, v in sorted(self.state_tree.env.items())]
            stdout = "\n".join(lines) + "\n"

        elif cmd == "export":
            if not args:
                lines = [f"declare -x {k}=\"{v}\"" for k, v in sorted(self.state_tree.env.items())]
                stdout = "\n".join(lines) + "\n"
            else:
                for a in args:
                    if "=" in a:
                        k, v = a.split("=", 1)
                        self.state_tree.env[k] = v.strip("'\"")

        elif cmd == "history":
            lines = [f"{i+1:>5}  {h}" for i, h in enumerate(self.state_tree.history)]
            stdout = "\n".join(lines) + "\n"

        elif cmd == "clear":
            stdout = "\033[2J\033[H"

        else:
            stderr = f"bash: {cmd}: command not found\n"
            exit_code = 127

        # Apply redirection if present
        if redirect_out:
            ok, msg = self.state_tree.write_file(redirect_out, stdout, append=append_out)
            if not ok:
                stderr = f"{msg}\n"
                exit_code = 1
            stdout = ""

        return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code}
