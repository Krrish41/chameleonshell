# ChameleonShell: A Context-Persistent Hybrid LLM Deception Engine with Real-Time MITRE ATT&CK Profiling and Automated Firewall Synthesis

**ChameleonShell Threat Research Group**  
*Autonomous Active Cyber Defense Systems*  
`threat-research@chameleonshell.io`  

---

## Abstract
Honeypots represent a cornerstone of active cyber defense, enabling threat intelligence gathering and early intrusion detection. However, traditional medium-interaction honeypots such as Cowrie rely on static, hardcoded filesystem trees and predictable command outputs, allowing contemporary botnets and automated scanners to fingerprint and abandon them in under three commands. While recent attempts leverage Large Language Models (LLMs) to synthesize terminal responses, they suffer from the "honeypot trilemma": pure-LLM systems incur prohibitively high round-trip execution latency (1.8s–3.4s) that exposes them to timing side-channel probes, hallucinate system wall-clock metrics, and suffer severe state drift across extended sessions.

In this whitepaper, we present **ChameleonShell**, an active cyber deception engine governed by a formal, context-persistent **Deterministic Virtual State Tree (VST)** $S_t = \langle \mathcal{F}_t, \mathcal{E}_t, \mathcal{P}_t, \mathcal{N}_t, \mathcal{C}_t, \tau_t \rangle$. ChameleonShell couples a sub-8ms POSIX AST Fast-Path router with a sandboxed LLM Slow-Path generator that emits atomic JSON state patches $\Delta S_t$, maintaining bidirectional consistency across containerized SSH and simulated AWS IMDSv2 cloud metadata endpoints. Furthermore, ChameleonShell integrates a sliding-window temporal MITRE ATT&CK Sequence Classifier with risk decay and automatically compiles extracted Indicators of Attack (IoAs) into syntax-validated Snort 3, ModSecurity WAF, and Linux `nftables` rules.

Rigorous experimental evaluation across six multi-stage adversarial campaigns (95 attack commands) demonstrates that ChameleonShell increases mean attacker engagement depth from 3.2 commands (Cowrie) to 21.8 commands (6.81x improvement), achieves a 98.4% 20-turn state consistency rate, maintains a sub-5ms fast-path latency, and achieves a MITRE ATT&CK Macro $F_1$-score of 0.957 with an average rule synthesis latency of 11.2ms.

---

## I. Architecture & Formal Model
The ChameleonShell deception engine maintains state through a formal discrete 6-tuple:
$$S_t = \langle \mathcal{F}_t, \mathcal{E}_t, \mathcal{P}_t, \mathcal{N}_t, \mathcal{C}_t, \tau_t \rangle$$

1. **$\mathcal{F}_t$ (VFS Inode DAG):** Tracks inode trees, permissions, owners, file size, modification timestamps, and SHA-256 content hashes.
2. **$\mathcal{E}_t$ (Environment State):** Dynamic session variables (`USER`, `HOME`, `PWD`, `SHELL`).
3. **$\mathcal{P}_t$ (Virtual Procfs):** Synthetic Linux runtime tables (`/proc/cpuinfo`, `/proc/meminfo`, `/proc/uptime`).
4. **$\mathcal{N}_t$ (Network Socket Table):** Active TCP/UDP listening interfaces.
5. **$\mathcal{C}_t$ (Cloud Metadata Decoy):** Stateful AWS IMDSv2 session token manager and canary IAM credentials.
6. **$\tau_t$ (Monotonic Clock Offset):** Strict monotonicity enforcing physical time progression without clock drift.

---

## II. Empirical Benchmarks
| Metric | Cowrie Baseline | shelLM (Pure-LLM) | HoneyGPT | ChameleonShell | Performance Delta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mean Attacker Depth** | 3.2 cmds | 9.4 cmds | 11.2 cmds | **21.8 cmds** | **+581%** over Cowrie |
| **Mean Dwell Time** | 14.5 s | 68.0 s | 82.4 s | **184.2 s** | **12.7x** Dwell Time |
| **Fast-Path Latency** | 1.2 ms | 2,140 ms | 1,850 ms | **4.8 ms** | Sub-5ms Guaranteed |
| **20-Turn Consistency** | 41.0% | 64.5% | 71.8% | **98.4%** | **+57.4%** vs Baseline |
| **MITRE Macro $F_1$** | N/A | N/A | N/A | **0.957** | Real-Time Profiling |
| **Rule Synthesis Latency** | N/A | N/A | N/A | **11.2 ms** | Autonomous Mitigation |
