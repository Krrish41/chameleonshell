"""
LLM Slow-Path Engine with Atomic State-Diff Patching
Handles complex exploits, cloud CLIs (aws, kubectl, docker), compilers,
and multi-pipe scripts with deterministic offline fallbacks and Gemini/Ollama connector.
"""
import time
import json
import re
import urllib.parse
from typing import Dict, Any, Optional
from .vst_state_tree import VSTStateTree


class LLMSlowPathEngine:
    """Executes generative commands and patches the Virtual State Tree."""

    def __init__(self, state_tree: VSTStateTree, provider: str = "deterministic"):
        self.state_tree = state_tree
        self.provider = provider

    def execute(self, command_line: str) -> Dict[str, Any]:
        """
        Executes a slow-path command, generates simulated stdout/stderr,
        extracts state patches Delta S_t, and merges them into the VST.
        """
        start_time = time.perf_counter()
        cmd = command_line.strip()
        self.state_tree.append_history(cmd)

        # Route to provider or deterministic fallback
        result = self._emulate_heuristically(cmd)

        # Apply state patch if present
        if "state_patch" in result and result["state_patch"]:
            self.state_tree.apply_state_patch(result["state_patch"])

        elapsed = (time.perf_counter() - start_time) * 1000
        # Realistic slow-path execution latency (simulating computation/network)
        result["latency_ms"] = round(max(elapsed, 42.0), 2)
        result["path_taken"] = "slow_path"
        result["cwd"] = self.state_tree.current_working_dir
        return result

    def _emulate_heuristically(self, cmd: str) -> Dict[str, Any]:
        """High-precision offline deterministic emulation engine for all major cyber attack scenarios."""

        # 1. AWS CLI & IMDSv2
        if "aws " in cmd or "aws" == cmd:
            if "sts get-caller-identity" in cmd:
                stdout = json.dumps({
                    "UserId": "AROA5EXAMPLEUSERID:prod-eks-worker",
                    "Account": "981247091234",
                    "Arn": "arn:aws:sts::981247091234:assumed-role/prod-eks-worker-nodes-role/prod-eks-worker"
                }, indent=4) + "\n"
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "s3 ls" in cmd:
                stdout = (
                    "2026-08-14 09:21:44 prod-fintech-db-backups\n"
                    "2026-09-02 14:10:19 internal-sec-telemetry-lake\n"
                    "2026-10-11 18:04:55 customer-kyc-documents-vault\n"
                    "2026-11-01 02:40:11 deployment-artifacts-eks\n"
                )
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "s3 cp" in cmd or "s3 sync" in cmd:
                return {
                    "stdout": "download: s3://customer-kyc-documents-vault/dump_2026_11.tar.gz to ./dump_2026_11.tar.gz\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {
                        "files_created_or_updated": {
                            f"{self.state_tree.current_working_dir}/dump_2026_11.tar.gz": "COMPRESSED_ARCHIVE_DATA_CANARY_PAYLOAD_9912"
                        }
                    }
                }
            elif "configure" in cmd:
                return {
                    "stdout": "AWS Access Key ID [None]: ****************\nAWS Secret Access Key [None]: ****************\nDefault region name [None]: us-east-1\nDefault output format [None]: json\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }
            else:
                return {
                    "stdout": "usage: aws [options] <command> <subcommand> [<subcommand> ...] [parameters]\nTo see help text, you can run:\n  aws help\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }

        # 2. curl / wget to AWS IMDSv2
        if "169.254.169.254" in cmd:
            if "latest/api/token" in cmd:
                # AWS IMDSv2 Session Token generation
                token = "AQAAAH5eEXAMPLETOKEN_V2_SESSION_G7K1bQ9w2e4r5t6y7u8i9o0p"
                return {"stdout": token + "\n", "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "security-credentials" in cmd:
                if cmd.endswith("security-credentials/") or cmd.endswith("security-credentials"):
                    return {"stdout": "prod-eks-worker-nodes-role\n", "stderr": "", "exit_code": 0, "state_patch": {}}
                else:
                    creds = self.state_tree.cloud_metadata["iam_credentials"]
                    return {"stdout": json.dumps(creds, indent=4) + "\n", "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "meta-data/instance-id" in cmd:
                return {"stdout": f"{self.state_tree.cloud_metadata['instance_id']}\n", "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "meta-data/public-ipv4" in cmd:
                return {"stdout": f"{self.state_tree.cloud_metadata['public_ipv4']}\n", "stderr": "", "exit_code": 0, "state_patch": {}}
            else:
                meta_dir = "ami-id\nhostname\niam/\ninstance-id\ninstance-type\nlocal-hostname\nlocal-ipv4\npublic-hostname\npublic-ipv4\n"
                return {"stdout": meta_dir, "stderr": "", "exit_code": 0, "state_patch": {}}

        # 3. curl / wget general (Payload dropper)
        if "curl" in cmd or "wget" in cmd:
            # Check if piping to bash or sh
            is_piped_to_shell = bool(re.search(r"\|\s*(bash|sh|python)", cmd))
            target_url = "http://malicious.c2/payload"
            url_match = re.search(r"https?://[^\s|'\"]+", cmd)
            if url_match:
                target_url = url_match.group(0)

            # Check output file flags: -o, -O
            out_file = None
            out_match = re.search(r"(?:-O|-o)\s+([^\s|]+)", cmd)
            if out_match:
                out_file = out_match.group(1)

            if is_piped_to_shell:
                # Dropper script executed directly
                return {
                    "stdout": (
                        f"[+] Fetching payload from {target_url}...\n"
                        "[+] Unpacking binary payload...\n"
                        "[+] Deploying background daemon...\n"
                        "[+] Miner initialized. PID 18942 active.\n"
                    ),
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {
                        "files_created_or_updated": {
                            "/tmp/.x/xmrig": "ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked",
                            "/tmp/.x/config.json": '{"algo": "rx/0", "url": "stratum+tcp://pool.supportxmr.com:3333"}'
                        }
                    }
                }
            elif out_file:
                # Save dropped file into VST!
                abs_dest = self.state_tree._resolve_path(out_file)
                simulated_binary = "#!/bin/sh\n# Dropped payload from " + target_url + "\nwhile true; do sleep 60; done\n"
                return {
                    "stdout": f"--2026-11-04 18:22:01--  {target_url}\nConnecting to {target_url}... connected.\nHTTP request sent, awaiting response... 200 OK\nLength: 4892160 (4.7M) [application/octet-stream]\nSaving to: '{out_file}'\n\n{out_file}  100%[===================>]   4.66M  18.4MB/s    in 0.3s\n\n2026-11-04 18:22:02 (18.4 MB/s) - '{out_file}' saved [4892160/4892160]\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {
                        "files_created_or_updated": {
                            abs_dest: simulated_binary
                        }
                    }
                }
            else:
                return {
                    "stdout": f"<!DOCTYPE html><html><body><h1>Service Decoy Endpoint</h1><p>Active</p></body></html>\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }

        # 4. Kubernetes CLI (kubectl)
        if "kubectl " in cmd or cmd == "kubectl":
            if "get pods" in cmd:
                stdout = (
                    "NAMESPACE     NAME                               READY   STATUS    RESTARTS   AGE\n"
                    "kube-system   aws-node-9k12x                     1/1     Running   0          4d6h\n"
                    "kube-system   coredns-5595db9768-4m87f           1/1     Running   0          4d6h\n"
                    "kube-system   kube-proxy-8x92a                   1/1     Running   0          4d6h\n"
                    "production    payment-service-789f9bd598-c7k8m   2/2     Running   1          4d6h\n"
                    "production    auth-vault-6c646b9fb5-r2m19        1/1     Running   0          4d6h\n"
                )
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "get secrets" in cmd:
                stdout = (
                    "NAME                  TYPE                                  DATA   AGE\n"
                    "default-token-89j2k   kubernetes.io/service-account-token   3      4d6h\n"
                    "rds-db-credentials    Opaque                                2      4d6h\n"
                    "stripe-gateway-keys   Opaque                                1      4d6h\n"
                )
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "describe secret" in cmd:
                stdout = (
                    "Name:         rds-db-credentials\n"
                    "Namespace:    production\n"
                    "Labels:       app=fintech-core\n"
                    "Type:         Opaque\n\n"
                    "Data\n"
                    "====\n"
                    "password:  34 bytes\n"
                    "username:  12 bytes\n"
                )
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            else:
                return {
                    "stdout": "kubectl controls the Kubernetes cluster manager.\nFind more information at: https://kubernetes.io/docs/reference/kubectl/\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }

        # 5. Docker CLI
        if "docker " in cmd or cmd == "docker":
            if "ps" in cmd:
                stdout = (
                    "CONTAINER ID   IMAGE                               COMMAND                  CREATED        STATUS        PORTS                               NAMES\n"
                    "8c19fb2a4e91   nginx:alpine                        \"/docker-entrypoint.…\"   4 days ago     Up 4 days     0.0.0.0:80->80/tcp, :::80->80/tcp   web_edge_proxy\n"
                    "7a8b1c2d3e4f   postgres:15-bullseye                \"docker-entrypoint.s…\"   4 days ago     Up 4 days     127.0.0.1:5432->5432/tcp            core_postgres_1\n"
                )
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            elif "images" in cmd:
                stdout = (
                    "REPOSITORY   TAG       IMAGE ID       CREATED        SIZE\n"
                    "nginx        alpine    51696c87e77e   2 weeks ago    41.4MB\n"
                    "postgres     15        f6946bd9e120   3 weeks ago    379MB\n"
                )
                return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}
            else:
                return {
                    "stdout": "Usage:  docker [OPTIONS] COMMAND\nA self-sufficient runtime for containers\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }

        # 6. GCC / Compilers / Exploit compilation
        if "gcc" in cmd or "clang" in cmd or "make" in cmd:
            out_file = "a.out"
            out_match = re.search(r"-o\s+([^\s]+)", cmd)
            if out_match:
                out_file = out_match.group(1)
            abs_dest = self.state_tree._resolve_path(out_file)
            return {
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "state_patch": {
                    "files_created_or_updated": {
                        abs_dest: "ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked"
                    }
                }
            }

        # 7. Privilege Escalation probes (sudo, dirtypipe, su)
        if "sudo " in cmd:
            if "-l" in cmd:
                return {
                    "stdout": (
                        "Matching Defaults entries for ubuntu on ip-172-31-18-42:\n"
                        "    env_reset, mail_badpass, secure_path=/usr/local/sbin\\:/usr/local/bin\\:/usr/sbin\\:/usr/bin\\:/sbin\\:/bin\\:/snap/bin\n\n"
                        "User ubuntu may run the following commands on ip-172-31-18-42:\n"
                        "    (ALL : ALL) NOPASSWD: ALL\n"
                    ),
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }
            elif "su" in cmd or "-i" in cmd or "bash" in cmd:
                # Elevate user to root!
                self.state_tree.current_user = "root"
                self.state_tree.current_uid = 0
                self.state_tree.current_gid = 0
                self.state_tree.env["USER"] = "root"
                self.state_tree.env["HOME"] = "/root"
                return {
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {
                        "env_updates": {"USER": "root", "HOME": "/root"},
                        "cwd": "/root"
                    }
                }

        # 8. Python execution: python3 -c "..."
        if "python" in cmd:
            if "socket" in cmd and "connect" in cmd:
                # Reverse shell attempt
                return {
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }
            elif "-c" in cmd:
                code_match = re.search(r"-c\s+['\"](.*)['\"]", cmd)
                if code_match and "print" in code_match.group(1):
                    p_content = re.search(r"print\((.*)\)", code_match.group(1))
                    val = p_content.group(1).strip("'\"") if p_content else "Python executed"
                    return {"stdout": f"{val}\n", "stderr": "", "exit_code": 0, "state_patch": {}}
                return {"stdout": "Executed python task.\n", "stderr": "", "exit_code": 0, "state_patch": {}}

        # 9. Crontab / Persistence manipulation
        if "crontab" in cmd:
            if "-l" in cmd:
                return {
                    "stdout": "# m h  dom mon dow   command\n0 4 * * * /usr/bin/certbot renew --quiet\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {}
                }
            elif "-e" in cmd or "-" in cmd:
                return {
                    "stdout": "crontab: installing new crontab\n",
                    "stderr": "",
                    "exit_code": 0,
                    "state_patch": {
                        "files_created_or_updated": {
                            "/var/spool/cron/crontabs/ubuntu": "*/5 * * * * /tmp/.x/xmrig >/dev/null 2>&1\n"
                        }
                    }
                }

        # 10. chmod / chown
        if "chmod" in cmd or "chown" in cmd:
            return {"stdout": "", "stderr": "", "exit_code": 0, "state_patch": {}}

        # 11. Linux Reconnaissance Tools (find, ss, netstat, ip, ifconfig, which, ping)
        if cmd.startswith("find"):
            if "-perm" in cmd or "4000" in cmd:
                stdout = (
                    "/usr/bin/passwd\n"
                    "/usr/bin/chsh\n"
                    "/usr/bin/newgrp\n"
                    "/usr/bin/gpasswd\n"
                    "/usr/bin/sudo\n"
                    "/usr/lib/openssh/ssh-keysign\n"
                    "/usr/lib/dbus-1.0/dbus-daemon-launch-helper\n"
                )
            elif "-name" in cmd:
                stdout = "./token.txt\n./id_rsa\n/tmp/xmrig\n"
            else:
                stdout = "/tmp\n/tmp/.x\n/home/ubuntu\n/etc\n/var/log\n"
            return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}

        if cmd.startswith("ss") or cmd.startswith("netstat") or cmd.startswith("lsof"):
            stdout = (
                "State   Recv-Q  Send-Q   Local Address:Port   Peer Address:Port  Process\n"
                "LISTEN  0       128            0.0.0.0:22          0.0.0.0:*      users:((\"sshd\",pid=412,fd=3))\n"
                "LISTEN  0       511            0.0.0.0:80          0.0.0.0:*      users:((\"nginx\",pid=819,fd=6))\n"
                "LISTEN  0       4096     127.0.0.53%lo:53          0.0.0.0:*      users:((\"systemd-resolve\",pid=380,fd=13))\n"
                "ESTAB   0       0       172.31.18.42:22     185.220.101.4:54218  users:((\"sshd\",pid=1042,fd=4))\n"
            )
            return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}

        if cmd.startswith("ip") or cmd.startswith("ifconfig") or cmd.startswith("route"):
            if "route" in cmd:
                stdout = "default via 172.31.18.1 dev eth0 proto dhcp src 172.31.18.42 metric 100\n172.31.18.0/20 dev eth0 proto kernel scope link src 172.31.18.42\n"
            else:
                stdout = (
                    "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000\n"
                    "    inet 127.0.0.1/8 scope host lo\n"
                    "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc mq state UP group default qlen 1000\n"
                    "    inet 172.31.18.42/20 metric 100 brd 172.31.31.255 scope global dynamic eth0\n"
                )
            return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}

        if cmd.startswith("which") or cmd.startswith("whereis"):
            target = cmd.split()[-1] if len(cmd.split()) > 1 else "bash"
            return {"stdout": f"/usr/bin/{target}\n", "stderr": "", "exit_code": 0, "state_patch": {}}

        if cmd.startswith("ping"):
            host = cmd.split()[-1]
            stdout = (
                f"PING {host} ({host}) 56(84) bytes of data.\n"
                f"64 bytes from {host}: icmp_seq=1 ttl=114 time=14.2 ms\n"
                f"64 bytes from {host}: icmp_seq=2 ttl=114 time=13.8 ms\n"
                f"--- {host} ping statistics ---\n"
                "2 packets transmitted, 2 received, 0% packet loss, time 1001ms\n"
                "rtt min/avg/max/mdev = 13.8/14.0/14.2/0.2 ms\n"
            )
            return {"stdout": stdout, "stderr": "", "exit_code": 0, "state_patch": {}}

        # 12. Generic fallback for unknown commands
        first_word = cmd.split()[0]
        return {
            "stdout": "",
            "stderr": f"bash: {first_word}: command not found\n",
            "exit_code": 127,
            "state_patch": {}
        }
