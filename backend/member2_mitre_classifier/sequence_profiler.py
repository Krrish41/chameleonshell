"""
Temporal MITRE ATT&CK Sequence Classifier & Threat Profiler
Evaluates the sliding window of attacker command trajectories C_{1:t},
classifies tactics & techniques, computes novelty, and applies temporal risk decay.
"""
import re
import time
from typing import Dict, Any, List, Tuple
from .mitre_knowledge_base import MITRE_TACTICS, MITRE_TECHNIQUES, get_technique_info


class MITRESequenceProfiler:
    """Classifies commands into ATT&CK Tactics/Techniques and maintains session risk state."""

    def __init__(self, decay_gamma: float = 0.88):
        self.gamma = decay_gamma
        self.history_records: List[Dict[str, Any]] = []
        self.seen_signatures = set()
        self.current_risk_score: float = 0.0

    def classify_command(self, cmd_line: str, attacker_ip: str = "185.220.101.4") -> Dict[str, Any]:
        """
        Classifies incoming command into MITRE ATT&CK tactic/technique,
        calculates novelty, updates decaying risk score, and returns event record.
        """
        cmd = cmd_line.strip()
        matched_tech_id = "T1059.004"  # Default generic shell execution
        matched_tactic_id = "TA0002"
        highest_weight = 0.0
        confidence = 0.70

        # Scan all MITRE technique regex patterns
        for tech_id, data in MITRE_TECHNIQUES.items():
            for pat in data["patterns"]:
                if re.search(pat, cmd, re.IGNORECASE):
                    tactic_id = data["tactic"]
                    weight = MITRE_TACTICS[tactic_id]["weight"]
                    if weight > highest_weight:
                        highest_weight = weight
                        matched_tech_id = tech_id
                        matched_tactic_id = tactic_id
                        confidence = 0.96
                    break

        tech_meta = get_technique_info(matched_tech_id)

        # Novelty indicator: I_novel(c_k)
        sig = f"{matched_tech_id}:{cmd[:30]}"
        is_novel = sig not in self.seen_signatures
        self.seen_signatures.add(sig)

        novelty_mult = 1.0 if is_novel else 0.35

        # Compute severity
        weight = tech_meta["weight"]
        if weight >= 40:
            severity = "CRITICAL"
        elif weight >= 30:
            severity = "HIGH"
        elif weight >= 20:
            severity = "MEDIUM"
        elif weight >= 10:
            severity = "LOW"
        else:
            severity = "INFORMATIONAL"

        record = {
            "step": len(self.history_records) + 1,
            "timestamp": time.time(),
            "command": cmd,
            "attacker_ip": attacker_ip,
            "tactic_id": matched_tactic_id,
            "tactic_name": tech_meta["tactic_name"],
            "technique_id": matched_tech_id,
            "technique_name": tech_meta["technique_name"],
            "confidence": confidence,
            "severity": severity,
            "weight": weight,
            "is_novel": is_novel
        }

        self.history_records.append(record)
        self.current_risk_score = self._compute_decayed_risk()
        record["cumulative_risk_score"] = round(self.current_risk_score, 1)

        return record

    def _compute_decayed_risk(self) -> float:
        """
        RiskScore(C_{1:t}) = min(100, sum_{k=1}^t gamma^{t-k} * w(Y^{(k)}) * I_novel(c_k))
        """
        t = len(self.history_records)
        if t == 0:
            return 0.0

        total_risk = 0.0
        for idx, rec in enumerate(self.history_records):
            k = idx + 1
            decay = self.gamma ** (t - k)
            novel_factor = 1.0 if rec["is_novel"] else 0.35
            total_risk += decay * rec["weight"] * novel_factor

        return min(100.0, total_risk)

    def get_tactics_distribution(self) -> Dict[str, int]:
        dist = {k: 0 for k in MITRE_TACTICS.keys()}
        for r in self.history_records:
            dist[r["tactic_id"]] = dist.get(r["tactic_id"], 0) + 1
        return dist

    def get_session_summary(self) -> Dict[str, Any]:
        tactics_hit = len(set(r["tactic_id"] for r in self.history_records))
        kill_chain_progression = round((tactics_hit / len(MITRE_TACTICS)) * 100, 1)
        return {
            "total_commands": len(self.history_records),
            "current_risk_score": round(self.current_risk_score, 1),
            "tactics_detected": tactics_hit,
            "kill_chain_progression_pct": kill_chain_progression,
            "top_techniques": list(set(r["technique_id"] for r in self.history_records[-5:])),
            "history": self.history_records
        }
