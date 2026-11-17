"""
Subsystem 02: MITRE ATT&CK Threat Profiler & Auto-Rule Synthesizer
Provides real-time sequence classification into Enterprise ATT&CK v16 Tactics/Techniques
and zero-touch synthesis of Snort 3, ModSecurity WAF, and nftables rules.
"""
from .mitre_knowledge_base import MITRE_TACTICS, MITRE_TECHNIQUES, get_technique_info
from .sequence_profiler import MITRESequenceProfiler
from .rule_synthesizer import ActiveDefenseRuleSynthesizer

__all__ = [
    "MITRE_TACTICS",
    "MITRE_TECHNIQUES",
    "get_technique_info",
    "MITRESequenceProfiler",
    "ActiveDefenseRuleSynthesizer"
]
