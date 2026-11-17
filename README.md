# ChameleonShell Core Platform & Engine

> **Adaptive Cloud Deception Engine & LLM-Driven Autonomous Honeypot**  
> High-interaction Linux & AWS IMDSv2 decoy surface with a sub-8ms Deterministic Virtual State Tree (VST), real-time MITRE ATT&CK sequence classification, and zero-touch firewall signature synthesis.

---

## Architecture & Subsystems

1. **`backend/` (FastAPI REST & WebSocket Server):**
   - **`member1_deception_engine/`:** Virtual State Tree (VST), POSIX AST Fast-Path router, Sandboxed LLM Slow-Path, AWS IMDSv2 decoy interface.
   - **`member2_mitre_classifier/`:** Real-time sequence classification against MITRE ATT&CK Enterprise v16, sliding-window temporal risk decay ($\gamma=0.92$), autonomous rule compiler (Snort 3, ModSecurity WAF `SecRule`, Linux `nftables`/`iptables`).
   - **`member3_telemetry_sandbox/`:** Containerized honey-network, 6 multi-stage automated botnet campaigns, Asciinema v2 live session recorder, and benchmark evaluator.

2. **`frontend/` (WebGL / Three.js Telemetry SOC Platform):**
   - Interactive 3D Chameleon Deception Core with kinetic velocity impulse dynamics.
   - Tactical custom cursor with hardware-accelerated fluid spring tracking.
   - Trilemma Bento comparison and 5-step live attacker kill-chain preview.

3. **`pages/` (Enterprise Workspaces):**
   - `lab.html`: Live side-by-side terminal, Inode DAG explorer, MITRE heatmap, botnet simulator.
   - `architecture.html`: Formal state model, DAG router pulse, Honey-Net topology.
   - `benchmarks.html`: Quantitative evaluation matrix, SVG trajectory sparklines, Dual-Terminal Live Trial Station.
   - `privacy-policy.html`: Telemetry anonymization boundaries and GDPR compliance.
   - `terms-of-service.html`: Authorized active defense research terms.

---

## Local Execution

### 1. Python Environment Setup
```bash
pip install -r backend/requirements.txt
```

### 2. Launch Local Server
From workspace root:
```bash
python -m chameleonshell.backend.main
```
Or from inside `chameleonshell/`:
```bash
python -m backend.main
```
Then navigate to `http://localhost:8080`.

### 3. Containerized Deployment
```bash
docker-compose up -d
```
