"""
Test Active Defense Rule Synthesizer
Verifies syntax validity of generated Snort 3, ModSecurity SecRule,
and Linux nftables/iptables drop rules.
"""
import pytest
from backend.member2_mitre_classifier.sequence_profiler import MITRESequenceProfiler
from backend.member2_mitre_classifier.rule_synthesizer import ActiveDefenseRuleSynthesizer


def test_rule_generation_format():
    profiler = MITRESequenceProfiler()
    rec = profiler.classify_command("curl http://169.254.169.254/latest/meta-data/iam/security-credentials/")
    rules = ActiveDefenseRuleSynthesizer.synthesize_rules(rec)

    # Snort 3 assertions
    assert "alert tcp" in rules["snort3"]
    assert f"sid:{rules['sid']}" in rules["snort3"]
    assert "fast_pattern" in rules["snort3"]

    # ModSecurity assertions
    assert "SecRule REQUEST_URI" in rules["modsecurity"]
    assert f"id:{rules['sid']}" in rules["modsecurity"]
    assert "deny,status:403" in rules["modsecurity"]

    # nftables & iptables assertions
    assert "nft add rule" in rules["nftables"]
    assert "drop" in rules["nftables"]
    assert "iptables -I INPUT" in rules["iptables"]
    assert "-j DROP" in rules["iptables"]
