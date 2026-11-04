"""
Deterministic Virtual State Tree (VST)
Maintains S_t = < F_t, E_t, P_t, N_t, C_t, tau_t >
Represents a realistic Ubuntu 22.04.5 LTS AWS Cloud Instance with in-memory DAG persistence.
"""
import time
import hashlib
import random
from typing import Dict, Any, Optional, List, Tuple


class VNode:
    """Represents a Virtual File System Inode (Directory or File)."""
    def __init__(
        self,
        name: str,
        is_dir: bool = False,
        content: str = "",
        permissions: str = "rw-r--r--",
        owner: str = "ubuntu",
        group: str = "ubuntu",
        uid: int = 1000,
        gid: int = 1000
    ):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.uid = uid
        self.gid = gid
        self.children: Dict[str, "VNode"] = {} if is_dir else None
        self.mtime = time.time()
        self.size = len(content.encode("utf-8")) if not is_dir else 4096
        self.sha256 = self._compute_sha256()

    def _compute_sha256(self) -> str:
        if self.is_dir:
            return ""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    def update_content(self, new_content: str):
        self.content = new_content
        self.size = len(new_content.encode("utf-8"))
        self.mtime = time.time()
        self.sha256 = self._compute_sha256()

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "is_dir": self.is_dir,
            "permissions": self.permissions,
            "owner": self.owner,
            "group": self.group,
            "size": self.size,
            "mtime": self.mtime,
            "sha256": self.sha256
        }
        if self.is_dir:
            data["children"] = [child.to_dict() for child in self.children.values()]
        return data


class VSTStateTree:
    """
    Virtual State Tree containing:
    - F_t: Inode DAG filesystem
    - E_t: Session environment variables
    - P_t: Virtual /proc generator
    - N_t: Network sockets table
    - C_t: Fake Cloud Metadata state
    - tau_t: Monotonic system clock offset
    """
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.boot_time = time.time() - 86400 * 4.25  # Simulated 4 days 6 hours uptime
        self.current_user = "ubuntu"
        self.current_uid = 1000
        self.current_gid = 1000
        self.current_working_dir = "/home/ubuntu"
        self.hostname = "ip-172-31-18-42"
        self.kernel = "6.8.0-1015-aws"
        self.os_release = "Ubuntu 22.04.5 LTS"
        
        # E_t: Environment Variables
        self.env: Dict[str, str] = {
            "USER": "ubuntu",
            "HOME": "/home/ubuntu",
            "SHELL": "/bin/bash",
            "LOGNAME": "ubuntu",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin",
            "LANG": "en_US.UTF-8",
            "TERM": "xterm-256color",
            "PWD": "/home/ubuntu",
            "AWS_DEFAULT_REGION": "us-east-1",
            "HOSTNAME": self.hostname
        }

        # N_t: Simulated Network Sockets
        self.sockets: List[Dict[str, Any]] = [
            {"proto": "tcp", "local_addr": "0.0.0.0:22", "remote_addr": "0.0.0.0:*", "state": "LISTEN", "pid": 724, "program": "sshd"},
            {"proto": "tcp", "local_addr": "0.0.0.0:80", "remote_addr": "0.0.0.0:*", "state": "LISTEN", "pid": 892, "program": "nginx: master"},
            {"proto": "tcp", "local_addr": "127.0.0.1:5432", "remote_addr": "0.0.0.0:*", "state": "LISTEN", "pid": 915, "program": "postgres"},
            {"proto": "tcp", "local_addr": "172.31.18.42:22", "remote_addr": "185.220.101.4:49812", "state": "ESTABLISHED", "pid": 14201, "program": "sshd: ubuntu"}
        ]

        # C_t: Cloud Metadata (AWS IMDSv2 + K8s)
        self.cloud_metadata: Dict[str, Any] = {
            "ami_id": "ami-0c7217cdde317cfec",
            "instance_id": "i-09f182bc879a11ef4",
            "instance_type": "c6a.2xlarge",
            "local_ipv4": "172.31.18.42",
            "public_ipv4": "54.210.88.194",
            "iam_role": "prod-eks-worker-nodes-role",
            "iam_credentials": {
                "Code": "Success",
                "LastUpdated": "2026-11-04T12:00:00Z",
                "Type": "AWS-HMAC",
                "AccessKeyId": "ASIAV7EXAMPLEKEYHONEY",
                "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "Token": "IQoJb3JpZ2luX2VjEOr//////////wEaCXVzLWVhc3QtMSJHMEUCIQChAMEEXAMPLETOKEN_CHAMELEONSHELL_CANARY",
                "Expiration": "2026-11-05T06:00:00Z"
            }
        }

        # Command History
        self.history: List[str] = [
            "sudo apt-get update && sudo apt-get upgrade -y",
            "git clone https://github.com/internal-corp/k8s-infra.git",
            "cd k8s-infra && ./deploy_k8s.sh",
            "aws sts get-caller-identity",
            "docker ps -a",
            "systemctl status nginx"
        ]

        # F_t: Root Inode DAG
        self.root = VNode(name="", is_dir=True, permissions="rwxr-xr-x", owner="root", group="root", uid=0, gid=0)
        self._initialize_fs()

    def _initialize_fs(self):
        """Constructs canonical Linux directories and realistic files."""
        dirs = [
            "/bin", "/boot", "/dev", "/etc", "/etc/ssh", "/etc/cron.d",
            "/home", "/home/ubuntu", "/home/ubuntu/.ssh", "/home/ubuntu/.aws",
            "/lib", "/lib64", "/media", "/mnt", "/opt", "/proc",
            "/root", "/run", "/sbin", "/srv", "/sys", "/tmp",
            "/usr", "/usr/bin", "/usr/sbin", "/usr/local/bin",
            "/var", "/var/log", "/var/run", "/var/www", "/var/www/html",
            "/var/run/secrets/kubernetes.io/serviceaccount"
        ]
        for d in dirs:
            self._mkdir_recursive(d)

        # /etc/passwd
        passwd_content = (
            "root:x:0:0:root:/root:/bin/bash\n"
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
            "bin:x:2:2:bin:/bin:/usr/sbin/nologin\n"
            "sys:x:3:3:sys:/dev:/usr/sbin/nologin\n"
            "sync:x:4:65534:sync:/bin:/bin/sync\n"
            "sshd:x:109:65534::/run/sshd:/usr/sbin/nologin\n"
            "postgres:x:114:120:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash\n"
            "ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n"
        )
        self._add_file("/etc/passwd", passwd_content, "rw-r--r--", "root", "root", 0, 0)

        # /etc/shadow (Restricted: rw-r----- root:shadow)
        shadow_content = (
            "root:$6$v8kXy/6u$mX49uJ1O0KqY13b4tW/Rz1oF8kL2sT5uN8pQ7mX49uJ1O0KqY13b4tW:19680:0:99999:7:::\n"
            "sshd:*:19680:0:99999:7:::\n"
            "postgres:*:19680:0:99999:7:::\n"
            "ubuntu:$6$qP9kL2sT$8kL2sT5uN8pQ7mX49uJ1O0KqY13b4tW/Rz1oFmX49uJ1O0KqY13b4tW:19680:0:99999:7:::\n"
        )
        self._add_file("/etc/shadow", shadow_content, "rw-r-----", "root", "shadow", 0, 42)

        # /etc/hosts
        hosts_content = (
            "127.0.0.1 localhost\n"
            "127.0.1.1 ip-172-31-18-42.ec2.internal ip-172-31-18-42\n"
            "# The following lines are desirable for IPv6 capable hosts\n"
            "::1 ip6-localhost ip6-loopback\n"
            "fe00::0 ip6-localnet\n"
            "ff00::0 ip6-mcastprefix\n"
            "ff02::1 ip6-allnodes\n"
            "ff02::2 ip6-allrouters\n"
        )
        self._add_file("/etc/hosts", hosts_content, "rw-r--r--", "root", "root", 0, 0)

        # /etc/os-release
        os_release = (
            'NAME="Ubuntu"\n'
            'VERSION="22.04.5 LTS (Jammy Jellyfish)"\n'
            'ID=ubuntu\n'
            'ID_LIKE=debian\n'
            'PRETTY_NAME="Ubuntu 22.04.5 LTS"\n'
            'VERSION_ID="22.04"\n'
            'HOME_URL="https://www.ubuntu.com/"\n'
            'SUPPORT_URL="https://help.ubuntu.com/"\n'
            'BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"\n'
            'PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"\n'
            'UBUNTU_CODENAME=jammy\n'
        )
        self._add_file("/etc/os-release", os_release, "rw-r--r--", "root", "root", 0, 0)

        # /home/ubuntu/.ssh/authorized_keys
        auth_keys = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICyG2qE4jR5xJpZ9uQw8bT1oVm6yL3sF0nK8pP2mX49u dev-lead@cloud-sec-corp.internal\n"
        self._add_file("/home/ubuntu/.ssh/authorized_keys", auth_keys, "rw-------", "ubuntu", "ubuntu", 1000, 1000)

        # /home/ubuntu/.bash_history
        self._refresh_bash_history_file()

        # /home/ubuntu/.aws/credentials (Honeytoken Canary Credentials)
        aws_creds = (
            "[default]\n"
            "aws_access_key_id = AKIAIOSFODNN7EXAMPLE\n"
            "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n"
            "region = us-east-1\n"
        )
        self._add_file("/home/ubuntu/.aws/credentials", aws_creds, "rw-------", "ubuntu", "ubuntu", 1000, 1000)

        # /home/ubuntu/deploy_k8s.sh
        deploy_sh = (
            "#!/usr/bin/env bash\n"
            "# Production Cluster Manifest Apply Script\n"
            "set -euo pipefail\n"
            "echo '[+] Authenticating with AWS EKS cluster prod-useast1-cluster...'\n"
            "aws eks update-kubeconfig --name prod-useast1-cluster --region us-east-1\n"
            "kubectl apply -f ./manifests/\n"
            "echo '[OK] Deployment pipeline synchronized.'\n"
        )
        self._add_file("/home/ubuntu/deploy_k8s.sh", deploy_sh, "rwxr-xr-x", "ubuntu", "ubuntu", 1000, 1000)

        # /var/www/html/.env (Canary Environment Secrets)
        env_content = (
            "APP_ENV=production\n"
            "APP_DEBUG=false\n"
            "DB_CONNECTION=pgsql\n"
            "DB_HOST=prod-aurora-pg.cluster-c9x18y.us-east-1.rds.amazonaws.com\n"
            "DB_PORT=5432\n"
            "DB_DATABASE=fintech_core_prod\n"
            "DB_USERNAME=pgadmin_app\n"
            "DB_PASSWORD=Vault$Token_9921_CanaryPwn\n"
            "STRIPE_SECRET_KEY=canary_dummy_stripe_key_mock_9918237192\n"
            "JWT_SIGNING_KEY=d7a9b1c2e4f6a8c0d2e4f6a8b0c2d4e6f8a0b2c4\n"
        )
        self._add_file("/var/www/html/.env", env_content, "rw-r--r--", "www-data", "www-data", 33, 33)

        # /var/log/auth.log
        auth_log = (
            "Nov  4 10:14:02 ip-172-31-18-42 sshd[13890]: Accepted publickey for ubuntu from 192.168.1.104 port 51234 ssh2\n"
            "Nov  4 10:14:02 ip-172-31-18-42 systemd-logind[612]: New session 42 of user ubuntu.\n"
            "Nov  4 11:20:19 ip-172-31-18-42 sudo:   ubuntu : TTY=pts/0 ; PWD=/home/ubuntu ; USER=root ; COMMAND=/usr/bin/apt-get update\n"
        )
        self._add_file("/var/log/auth.log", auth_log, "rw-r-----", "syslog", "adm", 104, 4)

        # Kubernetes Service Account Token (Canary Decoy)
        k8s_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkNoYW1lbGVvblNoZWxsX0VLU19Ub2tlbiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6cHJvZC1kZXBsb3llciJ9.CANARY_K8S_SIGNATURE_99201"
        self._add_file("/var/run/secrets/kubernetes.io/serviceaccount/token", k8s_token, "r--r--r--", "root", "root", 0, 0)

    def _refresh_bash_history_file(self):
        content = "\n".join(self.history) + "\n"
        self._add_file("/home/ubuntu/.bash_history", content, "rw-------", "ubuntu", "ubuntu", 1000, 1000)

    def append_history(self, cmd: str):
        self.history.append(cmd)
        self._refresh_bash_history_file()

    def _resolve_path(self, path: str) -> str:
        """Converts relative path to canonical absolute path."""
        if not path:
            return self.current_working_dir
        if not path.startswith("/"):
            path = f"{self.current_working_dir}/{path}"
        parts = [p for p in path.split("/") if p and p != "."]
        stack: List[str] = []
        for p in parts:
            if p == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(p)
        return "/" + "/".join(stack)

    def _get_node(self, abs_path: str) -> Optional[VNode]:
        """Traverses the DAG to find the target VNode."""
        if abs_path == "/" or abs_path == "":
            return self.root
        parts = [p for p in abs_path.split("/") if p]
        curr = self.root
        for part in parts:
            if not curr.is_dir or part not in curr.children:
                return None
            curr = curr.children[part]
        return curr

    def _mkdir_recursive(self, abs_path: str, permissions="rwxr-xr-x", owner="root", group="root", uid=0, gid=0) -> VNode:
        parts = [p for p in abs_path.split("/") if p]
        curr = self.root
        for part in parts:
            if part not in curr.children:
                curr.children[part] = VNode(part, is_dir=True, permissions=permissions, owner=owner, group=group, uid=uid, gid=gid)
            curr = curr.children[part]
        return curr

    def _add_file(self, abs_path: str, content: str, permissions="rw-r--r--", owner="root", group="root", uid=0, gid=0) -> VNode:
        parts = [p for p in abs_path.split("/") if p]
        if not parts:
            return self.root
        dir_path = "/" + "/".join(parts[:-1])
        file_name = parts[-1]
        parent = self._mkdir_recursive(dir_path)
        node = VNode(file_name, is_dir=False, content=content, permissions=permissions, owner=owner, group=group, uid=uid, gid=gid)
        parent.children[file_name] = node
        return node

    # Public State Mutation Methods
    def write_file(self, path: str, content: str, append: bool = False, owner: Optional[str] = None) -> Tuple[bool, str]:
        abs_path = self._resolve_path(path)
        parts = [p for p in abs_path.split("/") if p]
        if not parts:
            return False, "Cannot write to root directory"
        dir_path = "/" + "/".join(parts[:-1])
        file_name = parts[-1]
        parent = self._get_node(dir_path)
        if not parent or not parent.is_dir:
            parent = self._mkdir_recursive(dir_path, owner=self.current_user)

        user = owner or self.current_user
        if file_name in parent.children:
            existing = parent.children[file_name]
            if existing.is_dir:
                return False, f"{path}: Is a directory"
            # Permission check for /etc/shadow
            if abs_path == "/etc/shadow" and self.current_user != "root":
                return False, f"bash: {path}: Permission denied"
            new_val = existing.content + content if append else content
            existing.update_content(new_val)
            return True, ""
        else:
            if abs_path.startswith("/etc/") and self.current_user != "root":
                return False, f"bash: {path}: Permission denied"
            self._add_file(abs_path, content, "rw-r--r--", user, user, self.current_uid, self.current_gid)
            return True, ""

    def read_file(self, path: str) -> Tuple[bool, str]:
        abs_path = self._resolve_path(path)
        # Handle virtual /proc files dynamically
        if abs_path.startswith("/proc/"):
            return self._handle_proc_read(abs_path)

        node = self._get_node(abs_path)
        if not node:
            return False, f"cat: {path}: No such file or directory"
        if node.is_dir:
            return False, f"cat: {path}: Is a directory"
        # Permission check
        if abs_path == "/etc/shadow" and self.current_user != "root":
            return False, f"cat: {path}: Permission denied"
        return True, node.content

    def list_dir(self, path: str = "", show_all: bool = False, long_format: bool = False) -> Tuple[bool, str]:
        abs_path = self._resolve_path(path)
        node = self._get_node(abs_path)
        if not node:
            return False, f"ls: cannot access '{path}': No such file or directory"
        if not node.is_dir:
            if long_format:
                line = f"{node.permissions} 1 {node.owner} {node.group} {node.size:>6} {time.strftime('%b %d %H:%M', time.localtime(node.mtime))} {node.name}"
                return True, line
            return True, node.name

        entries = sorted(node.children.keys())
        if not show_all:
            entries = [e for e in entries if not e.startswith(".")]

        if not long_format:
            return True, "  ".join(entries)

        lines = [f"total {len(entries) * 4}"]
        for e in entries:
            child = node.children[e]
            prefix = "d" if child.is_dir else "-"
            perms = f"{prefix}{child.permissions}"
            mtime_str = time.strftime('%b %d %H:%M', time.localtime(child.mtime))
            lines.append(f"{perms} 1 {child.owner:<8} {child.group:<8} {child.size:>6} {mtime_str} {child.name}")
        return True, "\n".join(lines)

    def change_dir(self, path: str) -> Tuple[bool, str]:
        if not path or path == "~":
            target = f"/home/{self.current_user}"
        else:
            target = self._resolve_path(path)
        node = self._get_node(target)
        if not node:
            return False, f"bash: cd: {path}: No such file or directory"
        if not node.is_dir:
            return False, f"bash: cd: {path}: Not a directory"
        self.current_working_dir = target
        self.env["PWD"] = target
        return True, ""

    def make_dir(self, path: str, parents: bool = False) -> Tuple[bool, str]:
        abs_path = self._resolve_path(path)
        node = self._get_node(abs_path)
        if node:
            return False, f"mkdir: cannot create directory '{path}': File exists"
        parts = [p for p in abs_path.split("/") if p]
        if not parts:
            return False, "mkdir: missing operand"
        parent_path = "/" + "/".join(parts[:-1])
        parent_node = self._get_node(parent_path)
        if not parent_node:
            if not parents:
                return False, f"mkdir: cannot create directory '{path}': No such file or directory"
            self._mkdir_recursive(abs_path, owner=self.current_user)
            return True, ""
        dir_name = parts[-1]
        parent_node.children[dir_name] = VNode(
            dir_name, is_dir=True, permissions="rwxr-xr-x",
            owner=self.current_user, group=self.current_user,
            uid=self.current_uid, gid=self.current_gid
        )
        return True, ""

    def remove(self, path: str, recursive: bool = False) -> Tuple[bool, str]:
        abs_path = self._resolve_path(path)
        if abs_path in ["/", "/bin", "/etc", "/lib", "/usr", "/var"]:
            return False, f"rm: it is dangerous to operate recursively on '{path}'"
        parts = [p for p in abs_path.split("/") if p]
        if not parts:
            return False, "rm: missing operand"
        parent_path = "/" + "/".join(parts[:-1])
        target_name = parts[-1]
        parent_node = self._get_node(parent_path)
        if not parent_node or target_name not in parent_node.children:
            return False, f"rm: cannot remove '{path}': No such file or directory"
        target_node = parent_node.children[target_name]
        if target_node.is_dir and not recursive:
            return False, f"rm: cannot remove '{path}': Is a directory"
        del parent_node.children[target_name]
        return True, ""

    def _handle_proc_read(self, abs_path: str) -> Tuple[bool, str]:
        """Dynamically generates /proc content tied to real monotonic clocks."""
        uptime_secs = time.time() - self.boot_time
        if abs_path == "/proc/uptime":
            # Realistic Linux uptime output: <uptime_seconds> <idle_seconds>
            return True, f"{uptime_secs:.2f} {uptime_secs * 7.82:.2f}\n"

        if abs_path == "/proc/cpuinfo":
            # Realistic 8-core AMD EPYC 7R13 Cloud Instance
            cores = []
            for i in range(8):
                cores.append(
                    f"processor\t: {i}\n"
                    f"vendor_id\t: AuthenticAMD\n"
                    f"cpu family\t: 25\n"
                    f"model\t\t: 1\n"
                    f"model name\t: AMD EPYC 7R13 48-Core Processor\n"
                    f"stepping\t: 1\n"
                    f"cpu MHz\t\t: 2649.998\n"
                    f"cache size\t: 512 KB\n"
                    f"flags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl nonstop_tsc cpuid extd_apicid aperfmperf rapl pni pclmulqdq monitor ssse3 fma cx16 pcid sse4_1 sse4_2 movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm cmp_legacy svm cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw topoext invpcid_single vmmcall fsgsbase bmi1 avx2 smep bmi2 erms invpcid rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xgetbv1 xsaves clzero xsaveerptr rdpru wbnoinvd arat\n"
                    f"bogomips\t: 5299.99\n"
                )
            return True, "\n".join(cores) + "\n"

        if abs_path == "/proc/meminfo":
            # 32 GB RAM with subtle realistic jitter (+/- 0.05%)
            jitter = random.randint(-400, 400)
            mem_total = 32880128
            mem_free = 21450210 + jitter
            mem_available = 26900140 + jitter
            buffers = 345012 + random.randint(-10, 10)
            cached = 5820412 + random.randint(-20, 20)
            return True, (
                f"MemTotal:       {mem_total} kB\n"
                f"MemFree:        {mem_free} kB\n"
                f"MemAvailable:   {mem_available} kB\n"
                f"Buffers:          {buffers} kB\n"
                f"Cached:          {cached} kB\n"
                f"SwapCached:            0 kB\n"
                f"Active:          7120300 kB\n"
                f"Inactive:        3120100 kB\n"
                f"SwapTotal:             0 kB\n"
                f"SwapFree:              0 kB\n"
            )

        if abs_path == "/proc/version":
            return True, f"Linux version 6.8.0-1015-aws (buildd@lcy02-amd64-001) (x86_64-linux-gnu-gcc-12 (Ubuntu 12.3.0-1ubuntu1~22.04) 12.3.0, GNU ld (GNU Binutils for Ubuntu) 2.38) #15-Ubuntu SMP PREEMPT_DYNAMIC Wed Oct  2 14:22:18 UTC 2026\n"

        if abs_path == "/proc/loadavg":
            return True, "0.14 0.08 0.03 1/312 18942\n"

        return False, f"cat: {abs_path}: No such file or directory"

    def get_full_tree_summary(self) -> Dict[str, Any]:
        """Provides the JSON tree structure for the web UI file explorer."""
        def serialize_node(node: VNode) -> Dict[str, Any]:
            item = {
                "name": node.name or "/",
                "is_dir": node.is_dir,
                "permissions": node.permissions,
                "owner": node.owner,
                "size": node.size,
                "mtime": node.mtime,
                "sha256": node.sha256[:12] if node.sha256 else ""
            }
            if node.is_dir:
                item["children"] = [serialize_node(c) for c in node.children.values()]
            return item
        return serialize_node(self.root)

    def apply_state_patch(self, patch: Dict[str, Any]) -> bool:
        """
        Applies an atomic Delta S_t patch emitted by the Slow-Path LLM:
        patch = {
            "files_created_or_updated": {"/path/to/file": "content"},
            "files_deleted": ["/path/to/file"],
            "env_updates": {"KEY": "VAL"},
            "cwd": "/optional/new/cwd"
        }
        """
        try:
            for path, content in patch.get("files_created_or_updated", {}).items():
                self.write_file(path, content)
            for path in patch.get("files_deleted", []):
                self.remove(path, recursive=True)
            for k, v in patch.get("env_updates", {}).items():
                self.env[k] = v
            if "cwd" in patch and patch["cwd"]:
                self.change_dir(patch["cwd"])
            return True
        except Exception:
            return False
