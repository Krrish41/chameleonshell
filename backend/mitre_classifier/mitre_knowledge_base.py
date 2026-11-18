"""
MITRE ATT&CK Enterprise v16 Knowledge Base
Defines 12 enterprise tactics, core Linux & Cloud techniques,
severity weights w(Y_tactic), and signature regex patterns.
"""
from typing import Dict, Any, List

MITRE_TACTICS: Dict[str, Dict[str, Any]] = {
    "TA0043": {"name": "Reconnaissance", "weight": 5.0, "color": "#8E96A4"},
    "TA0001": {"name": "Initial Access", "weight": 15.0, "color": "#00E5FF"},
    "TA0002": {"name": "Execution", "weight": 20.0, "color": "#00F59B"},
    "TA0003": {"name": "Persistence", "weight": 25.0, "color": "#FFB800"},
    "TA0004": {"name": "Privilege Escalation", "weight": 35.0, "color": "#FF9100"},
    "TA0005": {"name": "Defense Evasion", "weight": 30.0, "color": "#FF5252"},
    "TA0006": {"name": "Credential Access", "weight": 40.0, "color": "#FF1744"},
    "TA0007": {"name": "Discovery", "weight": 10.0, "color": "#7C4DFF"},
    "TA0008": {"name": "Lateral Movement", "weight": 35.0, "color": "#E040FB"},
    "TA0009": {"name": "Collection", "weight": 20.0, "color": "#FF6E40"},
    "TA0010": {"name": "Exfiltration", "weight": 45.0, "color": "#FF2A54"},
    "TA0040": {"name": "Impact", "weight": 50.0, "color": "#D50000"}
}

MITRE_TECHNIQUES: Dict[str, Dict[str, Any]] = {
    # TA0043: Reconnaissance
    "T1595": {
        "name": "Active Scanning",
        "tactic": "TA0043",
        "patterns": [r"\bnmap\b", r"\bmasscan\b", r"\bzmap\b"],
        "description": "Scanning network ports and listening services."
    },
    "T1592": {
        "name": "Gather Victim Host Information",
        "tactic": "TA0043",
        "patterns": [r"whois\b", r"dig\b", r"nslookup\b", r"host\s+"],
        "description": "Gathering IP and DNS host identity information."
    },

    # TA0001: Initial Access
    "T1190": {
        "name": "Exploit Public-Facing Application",
        "tactic": "TA0001",
        "patterns": [r"\bwp-login\b", r"\bphpMyAdmin\b", r"log4j|jndi:", r"\bCVE-", r"\.\./\.\./"],
        "description": "Exploiting web applications or exposed services."
    },
    "T1078": {
        "name": "Valid Accounts (Brute Force / Abuse)",
        "tactic": "TA0001",
        "patterns": [r"hydra\b", r"medusa\b", r"sshpass\b"],
        "description": "Attempting password spraying or credential stuffing."
    },

    # TA0002: Execution
    "T1059.004": {
        "name": "Command and Scripting Interpreter: Unix Shell",
        "tactic": "TA0002",
        "patterns": [r"\|\s*bash\b", r"\|\s*sh\b", r"/bin/bash\s+-c", r"/bin/sh\s+-c", r"eval\s+"],
        "description": "Execution of arbitrary shell commands or piped scripts."
    },
    "T1059.006": {
        "name": "Command and Scripting Interpreter: Python",
        "tactic": "TA0002",
        "patterns": [r"python[23]?\s+-c", r"perl\s+-e", r"ruby\s+-e"],
        "description": "Execution of inline scripting payloads."
    },
    "T1203": {
        "name": "Exploitation for Client Execution",
        "tactic": "TA0002",
        "patterns": [r"\bgcc\s+.*exploit", r"\bmake\b", r"\b\./exploit\b"],
        "description": "Compiling and executing targeted local exploits."
    },

    # TA0003: Persistence
    "T1053.003": {
        "name": "Scheduled Task/Job: Cron",
        "tactic": "TA0003",
        "patterns": [r"crontab\s+-[e-]", r"/etc/cron", r"/etc/crontab"],
        "description": "Injecting scheduled cron entries to maintain persistence."
    },
    "T1098.004": {
        "name": "Account Manipulation: SSH Authorized Keys",
        "tactic": "TA0003",
        "patterns": [r"authorized_keys", r"\.ssh/id_rsa"],
        "description": "Appending attacker public keys to SSH authorized_keys."
    },
    "T1136.001": {
        "name": "Create Account: Local Account",
        "tactic": "TA0003",
        "patterns": [r"useradd\b", r"adduser\b", r"usermod\s+-aG\s+sudo"],
        "description": "Creating rogue administrator user accounts."
    },

    # TA0004: Privilege Escalation
    "T1548.001": {
        "name": "Abuse Elevation Control Mechanism: Setuid and Setgid",
        "tactic": "TA0004",
        "patterns": [r"chmod\s+[u\+]*s", r"find\s+/.*-perm\s+-[24]000"],
        "description": "Configuring or searching for SUID root binaries."
    },
    "T1068": {
        "name": "Exploitation for Privilege Escalation",
        "tactic": "TA0004",
        "patterns": [r"dirtypipe", r"pwnkit", r"baron\s+samedit", r"sudo\s+-l", r"sudo\s+su", r"sudo\s+-i"],
        "description": "Invoking sudo privileges or kernel privilege escalation flaws."
    },

    # TA0005: Defense Evasion
    "T1070.003": {
        "name": "Indicator Removal: Clear Command History",
        "tactic": "TA0005",
        "patterns": [r"history\s+-c", r"unset\s+HISTFILE", r"HISTSIZE=0", r"rm\s+.*\.bash_history"],
        "description": "Purging shell history to conceal malicious operations."
    },
    "T1564.001": {
        "name": "Hide Artifacts: Hidden Files and Directories",
        "tactic": "TA0005",
        "patterns": [r"/tmp/\.", r"mkdir\s+\.", r"/dev/shm/\."],
        "description": "Creating hidden dot-directories in temporary filesystems."
    },
    "T1027": {
        "name": "Obfuscated Files or Information",
        "tactic": "TA0005",
        "patterns": [r"base64\s+-d", r"openssl\s+enc\s+-d", r"xxd\s+-r"],
        "description": "Deobfuscating base64 or encoded payloads on execution."
    },

    # TA0006: Credential Access
    "T1552.001": {
        "name": "Unsecured Credentials: Credentials In Files",
        "tactic": "TA0006",
        "patterns": [r"/etc/shadow", r"\.aws/credentials", r"\.env", r"wp-config\.php", r"id_rsa"],
        "description": "Harvesting plaintext credentials from filesystem files."
    },
    "T1552.005": {
        "name": "Unsecured Credentials: Cloud Instance Metadata API",
        "tactic": "TA0006",
        "patterns": [r"169\.254\.169\.254", r"latest/meta-data", r"security-credentials"],
        "description": "Harvesting IAM credentials from AWS/GCP Instance Metadata."
    },

    # TA0007: Discovery
    "T1082": {
        "name": "System Information Discovery",
        "tactic": "TA0007",
        "patterns": [r"uname\s+-a", r"/proc/cpuinfo", r"/proc/meminfo", r"lscpu\b", r"hostname\b", r"uptime\b"],
        "description": "Querying operating system, kernel, and hardware metrics."
    },
    "T1083": {
        "name": "File and Directory Discovery",
        "tactic": "TA0007",
        "patterns": [r"\bls\s+-la", r"\bfind\s+/", r"\btree\b", r"\bpwd\b"],
        "description": "Enumerating files, directories, and directory trees."
    },
    "T1049": {
        "name": "System Network Connections Discovery",
        "tactic": "TA0007",
        "patterns": [r"\bnetstat\b", r"(?:^|[|\s;])ss\s+-[a-zA-Z]+", r"\bip\s+a\b", r"\bifconfig\b", r"\barp\s+-a\b"],
        "description": "Enumerating active listening sockets and ARP tables."
    },

    # TA0008: Lateral Movement
    "T1021.004": {
        "name": "Remote Services: SSH",
        "tactic": "TA0008",
        "patterns": [r"ssh\s+.*@10\.", r"ssh\s+.*@172\.", r"ssh\s+.*@192\.168\."],
        "description": "Pivoting via SSH to internal VPC subnet hosts."
    },
    "T1550.001": {
        "name": "Use Alternate Authentication Material: Application Access Token",
        "tactic": "TA0008",
        "patterns": [r"kubectl\s+.*--token", r"aws\s+sts\s+assume-role"],
        "description": "Reusing stolen Kubernetes or AWS tokens to access cluster APIs."
    },

    # TA0009: Collection
    "T1560.001": {
        "name": "Archive Collected Data: Archive via Utility",
        "tactic": "TA0009",
        "patterns": [r"tar\s+-czf", r"zip\s+-r", r"gzip\b"],
        "description": "Compressing stolen files into an archive prior to exfiltration."
    },

    # TA0010: Exfiltration
    "T1048.003": {
        "name": "Exfiltration Over Unencrypted/Non-C2 Protocol",
        "tactic": "TA0010",
        "patterns": [r"curl\s+.*-X\s*POST.*-d\s*@", r"curl\s+.*--upload-file", r"scp\s+.*@"],
        "description": "Transmitting compressed database dumps or stolen secrets outward."
    },

    # TA0040: Impact
    "T1496": {
        "name": "Resource Hijacking: Cryptomining",
        "tactic": "TA0040",
        "patterns": [r"xmrig", r"stratum\+tcp://", r"minergate", r"cryptonight"],
        "description": "Deploying cryptocurrency miners to consume compute resources."
    },
    "T1486": {
        "name": "Data Encrypted for Impact",
        "tactic": "TA0040",
        "patterns": [r"gpg\s+-c.*--batch", r"openssl\s+enc\s+-aes-256-cbc", r"ransom"],
        "description": "Encrypting critical system databases or archives."
    }
}

def get_technique_info(tech_id: str) -> Dict[str, Any]:
    info = MITRE_TECHNIQUES.get(tech_id, {})
    if info:
        tactic_id = info["tactic"]
        tactic_info = MITRE_TACTICS.get(tactic_id, {})
        return {
            "technique_id": tech_id,
            "technique_name": info["name"],
            "tactic_id": tactic_id,
            "tactic_name": tactic_info.get("name", "Unknown"),
            "weight": tactic_info.get("weight", 10.0),
            "color": tactic_info.get("color", "#8E96A4"),
            "description": info["description"]
        }
    return {
        "technique_id": "T1059.004",
        "technique_name": "Unix Shell",
        "tactic_id": "TA0002",
        "tactic_name": "Execution",
        "weight": 20.0,
        "color": "#00F59B",
        "description": "Standard Unix shell interaction."
    }
