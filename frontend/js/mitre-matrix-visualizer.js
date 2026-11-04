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
    try {
      const res = await fetch("/api/mitre/tactics");
      if (!res.ok) return;
      const data = await res.json();
      this.renderTacticsGrid(data.tactics, data.techniques);
    } catch (e) {
      console.warn("Error loading MITRE matrix:", e);
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
    try {
      const res = await fetch("/api/rules/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: `simulated-attack-probe --technique ${techId}`, technique_id: techId })
      });
      if (res.ok) {
        const rules = await res.json();
        this.currentRules = rules;
        this.renderCurrentRule();
      }
    } catch (e) {
      console.warn("Rule preview synthesis error:", e);
    }
  }
}

window.MITREMatrixVisualizer = MITREMatrixVisualizer;
