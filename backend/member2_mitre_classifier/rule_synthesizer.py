"""
Autonomous Active Defense Rule Synthesizer
Compiles Indicators of Attack (IoAs) into syntax-validated:
1. Snort 3 Network Signatures
2. ModSecurity OWASP CRS SecRule WAF Directives
3. Linux nftables & iptables Firewall Drop Rules
"""
import time
import re
from typing import Dict, Any, List


class ActiveDefenseRuleSynthesizer:
    """Compiles detected intrusion trajectories into deployable defensive signatures."""

    BASE_SID = 9400100

    @classmethod
    def synthesize_rules(cls, mitre_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes Snort 3, ModSecurity, and nftables rules for a classified event record.
        """
        step = mitre_record.get("step", 1)
        sid = cls.BASE_SID + step
        tech_id = mitre_record.get("technique_id", "T1059.004")
        tech_name = mitre_record.get("technique_name", "Unix Shell")
        cmd = mitre_record.get("command", "")
        ip = mitre_record.get("attacker_ip", "185.220.101.4")
        iso_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(mitre_record.get("timestamp", time.time())))

        # Extract specific pattern tokens for Snort & WAF matching
        extracted_token = cls._extract_signature_token(cmd, tech_id)

        # 1. Snort 3 Signature
        snort_rule = cls._generate_snort3_rule(sid, tech_id, tech_name, extracted_token)

        # 2. ModSecurity SecRule WAF Directive
        modsec_rule = cls._generate_modsec_rule(sid, tech_id, tech_name, extracted_token)

        # 3. Linux nftables & iptables Rules
        nft_rule = f"nft add rule inet filter input ip saddr {ip} tcp dport {{ 22, 80, 443 }} counter drop comment \"ChameleonShell-AutoBlock-{tech_id}-{sid}\""
        iptables_rule = f"iptables -I INPUT -s {ip} -p tcp -m multiport --dports 22,80,443 -m comment --comment \"ChameleonShell-AutoBlock-{tech_id}-{sid}\" -j DROP"

        return {
            "sid": sid,
            "technique_id": tech_id,
            "technique_name": tech_name,
            "attacker_ip": ip,
            "timestamp": iso_time,
            "snort3": snort_rule,
            "modsecurity": modsec_rule,
            "nftables": nft_rule,
            "iptables": iptables_rule,
            "extracted_token": extracted_token
        }

    @staticmethod
    def _extract_signature_token(cmd: str, tech_id: str) -> str:
        """Extracts key malicious substring to generate granular payload filters."""
        if "169.254.169.254" in cmd:
            return "169.254.169.254/latest"
        elif "shadow" in cmd:
            return "/etc/shadow"
        elif ".aws/credentials" in cmd:
            return ".aws/credentials"
        elif ".env" in cmd:
            return ".env"
        elif "xmrig" in cmd:
            return "xmrig"
        elif "crontab" in cmd:
            return "crontab"
        elif "kubectl" in cmd:
            return "kubectl"
        elif "base64" in cmd:
            return "base64 -d"
        elif "chmod" in cmd and "s" in cmd:
            return "chmod +s"
        else:
            # Fallback to binary token
            return cmd.split()[0] if cmd else "malicious_payload"

    @staticmethod
    def _generate_snort3_rule(sid: int, tech_id: str, tech_name: str, token: str) -> str:
        clean_token = token.replace('"', '\\"')
        return (
            f'alert tcp $EXTERNAL_NET any -> $HOME_NET [22,80,443] '
            f'(msg:"[ChameleonShell-AutoDef] MITRE {tech_id} ({tech_name}) Malicious Signature Detected"; '
            f'flow:to_server,established; content:"{clean_token}"; fast_pattern; '
            f'classtype:attempted-admin; sid:{sid}; rev:1;)'
        )

    @staticmethod
    def _generate_modsec_rule(sid: int, tech_id: str, tech_name: str, token: str) -> str:
        escaped_rx = re.escape(token).replace('/', '\\/')
        return (
            f'SecRule REQUEST_URI|ARGS|REQUEST_BODY "@rx (?i:{escaped_rx})" '
            f'"id:{sid},phase:2,deny,status:403,log,msg:\'[ChameleonShell-AutoDef] MITRE {tech_id} '
            f'Blocked: {tech_name}\',tag:\'mitre-{tech_id.lower()}\',severity:\'CRITICAL\'"'
        )
