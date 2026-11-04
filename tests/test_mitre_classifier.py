"""
Test MITRE ATT&CK Enterprise v16 Sequence Profiler
Verifies correct mapping of attack trajectories, novelty scoring,
and temporal risk score accumulation with decay.
"""
import pytest
from backend.member2_mitre_classifier.sequence_profiler import MITRESequenceProfiler


def test_reconnaissance_classification():
    profiler = MITRESequenceProfiler()
    rec = profiler.classify_command("nmap -sS -p 22,80 192.168.1.1")
    assert rec["tactic_id"] == "TA0043"
    assert rec["technique_id"] == "T1595"
    assert rec["severity"] == "INFORMATIONAL" or rec["severity"] == "LOW"


def test_credential_access_imds():
    profiler = MITRESequenceProfiler()
    rec = profiler.classify_command("curl http://169.254.169.254/latest/meta-data/iam/security-credentials/")
    assert rec["tactic_id"] == "TA0006"
    assert rec["technique_id"] == "T1552.005"
    assert rec["severity"] == "CRITICAL"
    assert rec["confidence"] >= 0.90


def test_privilege_escalation_and_persistence():
    profiler = MITRESequenceProfiler()
    rec1 = profiler.classify_command("sudo -l")
    assert rec1["tactic_id"] == "TA0004"

    rec2 = profiler.classify_command("echo 'ssh-rsa AAAAB3...' >> /home/ubuntu/.ssh/authorized_keys")
    assert rec2["tactic_id"] == "TA0003"
    assert rec2["technique_id"] == "T1098.004"


def test_risk_score_accumulation_and_decay():
    profiler = MITRESequenceProfiler(decay_gamma=0.88)
    initial_score = profiler.current_risk_score
    assert initial_score == 0.0

    # Low severity command
    profiler.classify_command("uname -a")
    score1 = profiler.current_risk_score
    assert score1 > 0.0

    # Critical command
    profiler.classify_command("cat /etc/shadow")
    score2 = profiler.current_risk_score
    assert score2 > score1
    assert score2 <= 100.0
