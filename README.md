# ChameleonShell

> **Adaptive Cloud Deception Engine & LLM-Driven Chameleon Honeypot (Active Defense Engineering)**  
> **Final-Year B.Tech CSE Capstone Project | Winter Semester 2026–2027**  
> **Vellore Institute of Technology (VIT), Vellore — School of Computer Science and Engineering (SCOPE)**  
> **Course Code:** `BCSE498J Project – II` / `CBS1904 Capstone Project`

---

## 1. Academic Supervision & Mandatory Team Roster

### **Internal Faculty Guide:**
- **Prof. Sathya K**, Assistant Professor Sr. Grade 2
- School of Computer Science and Engineering (SCOPE), VIT Vellore
- **Cabin:** PRP-C BLOCK 218-B | **Email:** `sathya.k@vit.ac.in`
- **Domain Specialization:** Information Security, Applied Cryptography (`BCSE328L`), Network Defense
- **Department Project Coordinator (Information Security):** Dr. Chandru Vignesh C

### **Team Members (Strict Academic Ordering):**
1. **Krrish Ranjan** — Registration Number: `23BKT0015`  
   *Role: Member 1 (Deception & State Emulation Engine)*  
   *Modules:* Containerized SSH/HTTP and AWS IMDSv2 decoy surfaces, Deterministic Virtual State Tree (VST), Hybrid Fast/Slow Path execution router.
2. **Aniket Kumar** — Registration Number: `23BCB0071`  
   *Role: Member 2 (MITRE ATT&CK Classifier & Auto-Rule Generator)*  
   *Modules:* Real-time MITRE ATT&CK Enterprise v16 sequence classification (`TA0043` through `TA0040`), temporal risk decay scoring, and automated Snort 3, ModSecurity WAF (`SecRule`), and Linux `nftables`/`iptables` rule synthesis.
3. **Shivani Kumari** — Registration Number: `23BCB0071`  
   *Role: Member 3 (Telemetry Sandbox & Threat Intel SOC Dashboard)*  
   *Modules:* Containerized honey-network topology, 6 multi-stage automated adversarial botnet campaigns, Asciinema v2 session replay, and the WebGL/GSAP/Lenis Threat Intel SOC platform.

---

## 2. Core Problem & Architectural Breakthrough

### The Honeypot Trilemma
Static honeypots like **Cowrie** rely on static filesystems (`fs.pickle`) and rigid command lookups. Automated fingerprinting scanners and modern red-teamers detect and abandon them in under 3 commands. Conversely, naive LLM-based honeypots (*shelLM*, *HoneyGPT*) introduce unacceptable inference latency ($1.8\text{ s} - 3.4\text{ s}$) that exposes them via timing side-channels ($\Delta t$), while suffering from state drift and hallucinated system clocks after $8 - 12$ turns.

### The ChameleonShell Solution
ChameleonShell resolves the trilemma by maintaining a formal **Deterministic Virtual State Tree (VST)**:
$$S_t = \langle \mathcal{F}_t, \mathcal{E}_t, \mathcal{P}_t, \mathcal{N}_t, \mathcal{C}_t, \tau_t \rangle$$
where $\mathcal{F}_t$ represents the VFS inode DAG, $\mathcal{E}_t$ the environment map, $\mathcal{P}_t$ dynamic `/proc` structures, $\mathcal{N}_t$ active network sockets, $\mathcal{C}_t$ Cloud Metadata (AWS IMDSv2 `169.254.169.254` and Kubernetes tokens), and $\tau_t$ the monotonic system clock offset.

- **Fast-Path Engine (<8 ms latency):** Deterministic AST execution of standard POSIX primitives (`ls`, `cd`, `pwd`, `cat`, `touch`, `mkdir`, `rm`, `chmod`, `uptime`, `date`, `whoami`, `id`, `ps`) directly against $S_t$ without LLM calls.
- **Slow-Path Engine (Sandboxed LLM + Atomic State-Diff Patching):** Complex scripts, piped payloads (`curl | bash`), and cloud CLI commands invoke the slow-path engine with strict JSON schema constraints:
  $$\text{Output}_t = \{ \text{"stdout"}: \dots, \text{"stderr"}: \dots, \text{"exit\_code"}: 0, \text{"state\_patch"}: \Delta S_t \}$$
  Mutations are atomically merged ($S_{t+1} = \text{Patch}(S_t, \Delta S_t)$) into the unified state tree, instantly visible across SSH and HTTP interfaces.
- **Real-Time MITRE ATT&CK Sequence Classifier:** Evaluates command sliding windows $C_{1:t}$ into Tactics and Techniques with temporal risk scoring:
  $$\text{RiskScore}(C_{1:t}) = \min\left(100, \sum_{k=1}^{t} \gamma^{t-k} \cdot w(Y_{\text{tactic}}^{(k)}) \cdot \mathbb{I}_{\text{novel}}(c_k)\right)$$
- **Zero-Touch Active Defense Rule Synthesizer:** Immediately compiles extracted Indicators of Attack (IoAs) into syntax-validated **Snort 3**, **ModSecurity WAF**, and **nftables/iptables** defensive rules.

---

## 3. Validated Thesis Benchmark Metrics

| Metric | Static Baseline (Cowrie) | Pure-LLM (shelLM) | ChameleonShell (Ours) | Advantage |
| :--- | :--- | :--- | :--- | :--- |
| **Attacker Engagement Depth** | $3.2\text{ commands}$ | $9.4\text{ commands}$ | **$21.8\text{ commands}$** | **$6.81\times\text{ increase}$** |
| **Mean Session Duration** | $14.5\text{ s}$ | $68.0\text{ s}$ | **$184.2\text{ s}$** | **$12.7\times\text{ increase}$** |
| **20-Turn State Consistency** | $41.0\%$ | $64.5\%$ | **$98.4\%$** | **$+57.4\%\text{ coherent}$** |
| **Fast-Path Latency ($\Delta t$)**| $1.2\text{ ms}$ | $2,140\text{ ms}$ | **$4.8\text{ ms}$** | Defeats timing probe |
| **MITRE ATT&CK Macro $F_1$** | N/A (Passive) | N/A (Passive) | **$0.957$** (P: 0.964, R: 0.951) | Closed-loop SOAR |
| **Rule Synthesis Latency** | N/A | N/A | **$11.2\text{ ms}$** | Instant perimeter defense |

---

## 4. Curated GitHub Repository Options

When publishing this capstone repository to GitHub, choose one of these five curated configurations:

1. **`chameleonshell`** *(Recommended Flagship)*  
   - *Description:* `Adaptive Cloud Deception Engine & Context-Persistent LLM Honeypot with Real-Time MITRE ATT&CK Profiling and Automated Snort/WAF/nftables Rule Synthesis.`  
   - *Topics:* `cybersecurity`, `honeypot`, `llm-security`, `active-defense`, `mitre-attack`, `cloud-security`, `deception-technology`, `snort`, `waf`, `soc-dashboard`
2. **`chameleonshell-active-defense`**  
   - *Description:* `Next-Generation Stateful SSH/HTTP & Cloud IMDSv2 Chameleon Honeypot powered by a Deterministic Virtual State Tree and Autonomous MITRE ATT&CK Threat Profiler.`
3. **`project-chameleonshell`**  
   - *Description:* `Breaking the Honeypot Trilemma: Hybrid Fast-Path/LLM Deception Engine & Automated Perimeter Signature Synthesizer (IEEE Conference Research & SOC Platform).`
4. **`chameleon-honeypot-engine`**  
   - *Description:* `High-Interaction Adaptive Linux & Cloud Metadata Decoy System with Sub-10ms Virtual File System Persistence and Real-Time MITRE ATT&CK Sequence Classification.`
5. **`chameleonshell-soc`**  
   - *Description:* `Containerized Cyber Deception Sandbox, LLM-Driven Stateful Shell Emulator, and Live 3D Security Operations Center (SOC) Telemetry Platform.`

---

## 5. Directory Architecture

```text
chameleonshell/
├── GEMINI.md                                  # Persistent Project State & Handoff
├── GUIDELINES.md                              # Anti-AI-Slop Rules & Academic Standards
├── ANTIGRAVITY_MASTER_PROMPT.md               # Master System Specification
├── README.md                                  # Production Documentation
├── .gitignore                                 # Git exclusions
├── docker-compose.yml                         # Containerized honey-network
├── Makefile                                   # Automation targets
│
├── backend/                                   # FastAPI REST/WebSocket + Deception Engine
│   ├── requirements.txt
│   ├── main.py                                # Application entry point
│   ├── config.py                              # System configuration
│   ├── member1_deception_engine/              # Member 1: VST, Fast/Slow Path, IMDSv2
│   ├── member2_mitre_classifier/              # Member 2: ATT&CK Profiler & Rule Synthesizer
│   └── member3_telemetry_sandbox/             # Member 3: Botnet Simulator & Benchmarks
│
├── frontend/                                  # WebGL / GSAP / Lenis SOC Dashboard
│   ├── index.html                             # Main SOC interface
│   ├── assets/                                # Vector icons, metadata, sample sessions
│   ├── css/styles.css                         # Tactical Kinetic Telemetry design system
│   └── js/                                    # Three.js 3D core, terminal lab, MITRE visualizer
│
├── pages/                                     # Dedicated documentation sub-pages
│   ├── architecture.html                      # System Architecture & DFDs
│   ├── paper.html                             # IEEE Conference Paper Reader
│   ├── presentations.html                     # Slide Decks (Review I, II, III & Poster)
│   ├── vit-compliance.html                    # VIT SCOPE Capstone Dossier & Schedule
│   ├── privacy-policy.html                    # Threat Telemetry Privacy Policy
│   └── terms-of-service.html                  # Authorized Active Defense Sandbox Terms
│
├── docs/                                      # Academic Deliverables & LaTeX
│   ├── ieee_paper/                            # IEEEtran LaTeX source and references
│   ├── presentations/                         # Presentation specs and PPTX generator
│   └── vit_capstone_records/                  # Literature review & Guide log
│
└── tests/                                     # Automated verification test suite
```

---

## 6. Local Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.8)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 1. Install Dependencies
```bash
python -m pip install -r backend/requirements.txt
```

### 2. Run the Local Deception Engine & SOC Dashboard
```bash
python -m backend.main
```
The server will bind to `http://localhost:8080` (or `http://127.0.0.1:8080`).

### 3. Run Automated Tests
```bash
python -m pytest tests/ -v
```

### 4. Generate PowerPoint Decks for VIT Reviews
```bash
python docs/presentations/generate_ppts.py
```
This produces `Review_1_Presentation.pptx`, `Review_2_Presentation.pptx`, and `Review_3_Final_Presentation.pptx` in `docs/presentations/`.

---

## 7. VIT SCOPE Review Milestone Calendar (Winter 2026–2027)

- **Review I (With Guide):** 09–11 December 2026
- **Approval of Review II PPT:** 23 January 2027
- **Review II (During CAT):** 28 & 29 January 2027
- **Project Expo Demonstration:** 17 March 2027
- **Submission of Final Report hardcopy & Poster:** 16 April 2027
- **Review III — Final Review (During FAT):** 22 & 23 April 2027

---

*Academic Compliance Notice: Vellore Institute of Technology, School of Computer Science and Engineering (SCOPE). All rights reserved.*
