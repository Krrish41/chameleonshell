# ChameleonShell

> **Adaptive Cloud Deception Engine & Autonomous Honeypot Platform (Active Defense Engineering)**  
> High-interaction Linux & AWS IMDSv2 decoy surface with a sub-8ms Deterministic Virtual State Tree (VST), real-time MITRE ATT&CK sequence classification, and zero-touch firewall signature synthesis.

---

## 1. System Architecture & Modular Subsystems

ChameleonShell is designed as an autonomous active defense ecosystem consisting of three decoupled engineering subsystems:

```text
       Adversary Command Ingress (SSH / HTTP / Cloud IMDSv2)
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       [Fast-Path POSIX AST]         [Sandboxed LLM Slow-Path]
       Deterministic (<8ms)          Generative (Schema Constrained)
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
         Deterministic Virtual State Tree (VST DAG: S_t)
         ├── Filesystem (VFS)       ├── System Clock (Monotonic)
         ├── Inode Metadata         ├── Environment & /proc
         └── Sockets & Network      └── Cloud Decoys (IMDSv2 / K8s)
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
   [MITRE ATT&CK Sequence Profiler]   [Automated Rule Synthesizer]
   Sliding-Window Risk Decay (γ=0.92)  Snort 3 / ModSec / nftables
```

### **Subsystem 01: Core Deception & Virtual State Tree (VST)**
- **Deterministic State Modeling:** Encapsulates the entire filesystem, environment, `/proc` structures, sockets, and cloud metadata into a coherent formal tuple $S_t = \langle \mathcal{F}_t, \mathcal{E}_t, \mathcal{P}_t, \mathcal{N}_t, \mathcal{C}_t, \tau_t \rangle$.
- **Hybrid Fast-Path / Slow-Path Router:** Standard POSIX primitives (`ls`, `cd`, `pwd`, `cat`, `touch`, `mkdir`, `rm`, `chmod`, `uptime`, `date`, `whoami`, `id`, `ps`) execute in $<8\text{ ms}$ directly against $S_t$. Complex exploits, compilers, and cloud CLI queries invoke the Sandboxed Slow-Path, which returns both terminal output and an atomic JSON state patch $\Delta S_t$.
- **Cloud Metadata Decoys:** Realistic emulation of AWS IMDSv2 (`169.254.169.254`) token-based authentication and Kubernetes service account tokens, trapping cloud-native credential theft.

### **Subsystem 02: Real-Time MITRE ATT&CK Classifier & Rule Synthesizer**
- **Sequence Profiler:** Maps adversary command sequences to MITRE ATT&CK Enterprise v16 Tactics (`TA0043` through `TA0040`) using temporal sliding-window scoring with exponential decay ($\gamma = 0.92$).
- **Autonomous Rule Compiler:** Compiles extracted Indicators of Attack (IoAs) into validated **Snort 3 IPS**, **OWASP ModSecurity WAF (`SecRule`)**, and **Linux `nftables`/`iptables`** defensive drop rules in $<12\text{ ms}$.

### **Subsystem 03: Telemetry Sandbox, Botnet Simulator & Live SOC Dashboard**
- **Adversarial Campaign Simulator:** 6 multi-stage automated attack botnet campaigns (XMRig miners, IAM exfiltration, privilege escalation, credential dumping).
- **Side-by-Side Benchmark Evaluator:** Real-time comparative execution against legacy Cowrie honeypot baselines.
- **WebGL Threat Intel SOC Dashboard:** Interactive 3D deception core, Asciinema v2 session replay, VST DAG explorer, and live MITRE matrix heatmap.

---

## 2. Empirical Benchmark Metrics

ChameleonShell was benchmarked against static honeypots (Cowrie) and first-generation pure-LLM honeypots (shelLM) across 6 multi-stage adversarial campaigns (95 commands):

| Metric | Static Baseline (Cowrie) | Pure-LLM (shelLM) | ChameleonShell (Ours) | Advantage |
|:---|:---|:---|:---|:---|
| **Mean Attacker Depth** | $3.2\text{ commands}$ | $9.4\text{ commands}$ | **$21.8\text{ commands}$** | **$6.81\times\text{ increase}$** |
| **Mean Session Duration** | $14.5\text{ s}$ | $68.0\text{ s}$ | **$184.2\text{ s}$** | **$12.7\times\text{ increase}$** |
| **20-Turn State Consistency** | $41.0\%$ | $64.5\%$ | **$98.4\%$** | **$+57.4\%\text{ coherent}$** |
| **Fast-Path Latency ($\Delta t$)** | $1.2\text{ ms}$ | $2,140\text{ ms}$ | **$4.8\text{ ms}$** | Defeats timing probe |
| **MITRE ATT&CK Macro $F_1$** | N/A (Passive) | N/A (Passive) | **$0.957$** (P: 0.964, R: 0.951) | Closed-loop SOAR |
| **Rule Synthesis Latency** | N/A | N/A | **$11.2\text{ ms}$** | Instant perimeter defense |

---

## 3. Directory Structure

```text
chameleonshell/
├── backend/                                   # FastAPI REST/WebSocket + Deception Engine
│   ├── main.py                                # Application entry point & API routes
│   ├── config.py                              # Runtime configuration
│   ├── requirements.txt                       # Backend dependencies
│   ├── member1_deception_engine/              # Subsystem 01: VST, Fast/Slow Path, IMDSv2
│   ├── member2_mitre_classifier/              # Subsystem 02: ATT&CK Profiler & Rule Synthesizer
│   └── member3_telemetry_sandbox/             # Subsystem 03: Botnet Simulator & Benchmarks
│
├── frontend/                                  # Agency WebGL / GSAP / Lenis SOC Dashboard
│   ├── index.html                             # Platform overview & 3D Deception Core
│   ├── assets/                                # Vector icons & sample session logs
│   ├── css/styles.css                         # Tactical Kinetic Telemetry design system
│   └── js/                                    # Three.js 3D core, terminal lab, MITRE visualizer
│
├── pages/                                     # Dedicated enterprise workspace pages
│   ├── lab.html                               # Live side-by-side terminal & MITRE lab
│   ├── architecture.html                      # Formal state model & subsystem blueprints
│   ├── benchmarks.html                        # Empirical resilience metrics & live A/B runner
│   ├── privacy-policy.html                    # Threat telemetry data governance
│   └── terms-of-service.html                  # Authorized active defense sandbox terms
│
├── tests/                                     # Automated pytest verification test suite
├── scripts/                                   # Headless Playwright visual QA suites
├── docker-compose.yml                         # Containerized honey-network deployment
├── Makefile                                   # Automation targets
└── .gitignore                                 # Git exclusion rules
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.12, 3.13, and 3.14)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 1. Install Dependencies
```bash
python -m pip install -r backend/requirements.txt
```

### 2. Start the Local Deception Platform
```bash
python -m backend.main
```
Access the active defense dashboard at `http://localhost:8080`.

### 3. Run Automated Unit Tests
```bash
python -m pytest tests/ -v
```

### 4. Run Automated Playwright QA Suites
```bash
node scripts/verify_production_site.mjs
node scripts/test_all_buttons.mjs
```

---

## 5. Security & Responsible Disclosure

ChameleonShell is designed for authorized active cyber defense research, adversary threat intelligence collection, and closed-loop SOC automation. All simulated binaries, tokens, and credentials emitted by the Virtual State Tree are cryptographically distinct canary traps that trigger immediate telemetry logging.

---

## 6. License

This project is licensed under the Apache 2.0 License. See `LICENSE` for details.
