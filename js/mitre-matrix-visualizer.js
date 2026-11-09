/**
 * ChameleonShell: MITRE ATT&CK Matrix Visualizer & Auto-Rule Synthesizer UI
 * Dynamically highlights active techniques across the Enterprise v16 matrix,
 * updates temporal risk decay score, and displays compiled Snort 3, ModSec, and nftables rules.
 */

class MITREMatrixVisualizer {
  constructor() {
    this.tacticsContainer = document.getElementById("mitre-tactics-grid");
    this.riskScoreVal = document.getElementById("mitre-risk-score-val");
    this.riskScoreBar = document.getElementById("mitre-risk-score-bar");
    this.ruleDisplayBox = document.getElementById("rule-display-box");
    this.copyRuleBtn = document.getElementById("copy-rule-btn");
    this.currentRules = null;
    this.activeRuleFormat = "snort3"; // "snort3" | "modsecurity" | "nftables"

    this.init();
  }

  async init() {
    this.setupRuleTabs();
    this.setupCopyButton();
    await this.loadMatrix();
  }

  async loadMatrix() {
    if (!this.tacticsContainer) return;
    const basePath = window.__BASE_PATH__ || (window.location.pathname.startsWith("/chameleonshell") ? "/chameleonshell" : "");
    try {
      let res = await fetch(`${basePath}/api/mitre/tactics`);
      if (!res.ok) res = await fetch(`${basePath}/api/mitre/tactics.json`);
      if (!res.ok) throw new Error("Matrix fetch failed");
      const data = await res.json();
      this.renderTacticsGrid(data.tactics, data.techniques);
    } catch (e) {
      // Fallback matrix data for offline static showcase
      const fallbackTactics = {
        "TA0043": { name: "Reconnaissance" },
        "TA0001": { name: "Initial Access" },
        "TA0002": { name: "Execution" },
        "TA0003": { name: "Persistence" },
        "TA0004": { name: "Privilege Escalation" },
        "TA0005": { name: "Defense Evasion" },
        "TA0006": { name: "Credential Access" },
        "TA0007": { name: "Discovery" },
        "TA0008": { name: "Lateral Movement" },
        "TA0009": { name: "Collection" },
        "TA0011": { name: "Command and Control" },
        "TA0010": { name: "Exfiltration" }
      };
      const fallbackTechniques = {
        "T1595.002": { name: "Vulnerability Scanning", tactic: "TA0043", description: "Scanning target for known vulnerabilities" },
        "T1190": { name: "Exploit Public-Facing Application", tactic: "TA0001", description: "Exploiting web/SSH endpoints" },
        "T1059.004": { name: "Unix Shell", tactic: "TA0002", description: "Interacting via bash or sh CLI" },
        "T1053.003": { name: "Cron Scheduled Tasks", tactic: "TA0003", description: "Creating persistence via cron" },
        "T1548.001": { name: "SetUID and SetGID", tactic: "TA0004", description: "Abusing SUID binaries for root elevation" },
        "T1070.004": { name: "File Deletion", tactic: "TA0005", description: "Deleting logs and command history" },
        "T1003.008": { name: "/etc/passwd and /etc/shadow", tactic: "TA0006", description: "Dumping Linux credential hashes" },
        "T1580": { name: "Cloud Infrastructure Discovery", tactic: "TA0007", description: "Querying AWS IMDSv2 metadata" },
        "T1046": { name: "Network Service Discovery", tactic: "TA0007", description: "Scanning local subnet ports" },
        "T1021.004": { name: "SSH Lateral Movement", tactic: "TA0008", description: "Tunneling SSH keys across hosts" },
        "T1560": { name: "Archive Collected Data", tactic: "TA0009", description: "Tar/gzip data staging" },
        "T1071.001": { name: "Web Protocols (HTTP/S C2)", tactic: "TA0011", description: "Egress telemetry over port 443" }
      };
      this.renderTacticsGrid(fallbackTactics, fallbackTechniques);
    }
  }

  renderTacticsGrid(tactics, techniques) {
    this.tacticsContainer.innerHTML = "";

    // Group techniques by tactic
    const tacticTechMap = {};
    for (const [techId, techData] of Object.entries(techniques)) {
      const tacId = techData.tactic;
      if (!tacticTechMap[tacId]) tacticTechMap[tacId] = [];
      tacticTechMap[tacId].push({ id: techId, ...techData });
    }

    // Render columns for each tactic
    for (const [tacId, tacMeta] of Object.entries(tactics)) {
      const col = document.createElement("div");
      col.className = "tactic-column";
      col.setAttribute("data-tactic-id", tacId);

      const header = document.createElement("div");
      header.className = "tactic-header";
      header.innerText = `${tacId}\n${tacMeta.name}`;
      col.appendChild(header);

      const techs = tacticTechMap[tacId] || [];
      techs.forEach((t) => {
        const chip = document.createElement("div");
        chip.className = "technique-chip";
        chip.id = `tech-chip-${t.id.replace(".", "-")}`;
        chip.setAttribute("data-tech-id", t.id);
        chip.title = `${t.name}: ${t.description}`;
        chip.innerText = `${t.id} ${t.name}`;
        
        chip.addEventListener("click", () => {
          this.previewTechniqueRule(t.id, t.name);
        });

        col.appendChild(chip);
      });

      this.tacticsContainer.appendChild(col);
    }
  }

  setupRuleTabs() {
    const tabs = document.querySelectorAll(".rule-tab-btn");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        this.activeRuleFormat = tab.getAttribute("data-format");
        this.renderCurrentRule();
      });
    });
  }

  setupCopyButton() {
    if (!this.copyRuleBtn) return;
    this.copyRuleBtn.addEventListener("click", () => {
      if (this.ruleDisplayBox && this.ruleDisplayBox.innerText) {
        navigator.clipboard.writeText(this.ruleDisplayBox.innerText);
        const originalText = this.copyRuleBtn.innerText;
        this.copyRuleBtn.innerText = "[COPIED TO CLIPBOARD]";
        setTimeout(() => {
          this.copyRuleBtn.innerText = originalText;
        }, 1800);
      }
    });
  }

  updateTelemetry(mitreRecord, rules) {
    if (!mitreRecord) return;

    // 1. Update dynamic Risk Score
    const score = mitreRecord.cumulative_risk_score || 0;
    if (this.riskScoreVal) {
      this.riskScoreVal.innerText = `${score.toFixed(1)} / 100`;
    }
    if (this.riskScoreBar) {
      this.riskScoreBar.style.width = `${Math.min(100, score)}%`;
      if (score >= 70) {
        this.riskScoreBar.style.background = "var(--accent-crimson)";
      } else if (score >= 40) {
        this.riskScoreBar.style.background = "var(--accent-amber)";
      } else {
        this.riskScoreBar.style.background = "var(--accent-volt)";
      }
    }

    // 2. Highlight technique chip in matrix
    const cleanId = mitreRecord.technique_id.replace(".", "-");
    const chip = document.getElementById(`tech-chip-${cleanId}`);
    if (chip) {
      chip.classList.add("active-trigger");
      chip.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
      setTimeout(() => {
        chip.classList.remove("active-trigger");
      }, 4000);
    }

    // 3. Update active defense rules
    if (rules) {
      this.currentRules = rules;
      this.renderCurrentRule();
    }
  }

  renderCurrentRule() {
    if (!this.ruleDisplayBox) return;
    if (!this.currentRules) {
      this.ruleDisplayBox.innerText = "# Awaiting incoming intrusion telemetry to synthesize defensive rules...";
      return;
    }

    let text = "";
    if (this.activeRuleFormat === "snort3") {
      text = `# Snort 3 Network Flow Signature (SID ${this.currentRules.sid})\n# Generated: ${this.currentRules.timestamp}\n\n${this.currentRules.snort3}`;
    } else if (this.activeRuleFormat === "modsecurity") {
      text = `# ModSecurity OWASP CRS SecRule Directive (Rule ID ${this.currentRules.sid})\n# Generated: ${this.currentRules.timestamp}\n\n${this.currentRules.modsecurity}`;
    } else if (this.activeRuleFormat === "nftables") {
      text = `# Linux nftables & iptables Perimeter Drop Rules\n# Target Attacker IP: ${this.currentRules.attacker_ip}\n\n${this.currentRules.nftables}\n\n${this.currentRules.iptables}`;
    }

    this.ruleDisplayBox.innerText = text;
  }

  async previewTechniqueRule(techId, techName) {
    const basePath = window.__BASE_PATH__ || (window.location.pathname.startsWith("/chameleonshell") ? "/chameleonshell" : "");
    let rules = null;
    try {
      const res = await fetch(`${basePath}/api/rules/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: `simulated-attack-probe --technique ${techId}`, technique_id: techId })
      });
      if (res.ok) {
        rules = await res.json();
      }
    } catch (e) {
      // Fallback
    }

    if (!rules) {
      rules = {
        sid: Math.floor(100000 + Math.random() * 900000),
        timestamp: new Date().toISOString(),
        attacker_ip: "185.220.101.4",
        snort3: `drop tcp any any -> any any (msg:"[ChameleonShell Trapped] Attack Sequence ${techId}: ${techName}"; sid:100042; rev:1;)`,
        modsecurity: `SecRule REQUEST_URI "@contains ${techId}" "id:100042,phase:1,deny,status:403,msg:'MITRE ${techId} Blocked'"`,
        nftables: `table inet filter {\n    chain input {\n        ip saddr 185.220.101.4 drop comment "MITRE ${techId} (${techName}) Trapped"\n    }\n}`,
        iptables: `iptables -A INPUT -s 185.220.101.4 -m comment --comment "MITRE ${techId}" -j DROP`
      };
    }

    this.currentRules = rules;
    this.renderCurrentRule();
  }
}

window.MITREMatrixVisualizer = MITREMatrixVisualizer;
