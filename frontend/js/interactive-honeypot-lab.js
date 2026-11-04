/**
 * ChameleonShell: Interactive Honeypot Lab Controller
 * Drives the live side-by-side terminal comparison (ChameleonShell vs. Cowrie),
 * handles preset scenario triggers, and refreshes the Virtual State Tree (VST) DAG.
 */

class InteractiveHoneypotLab {
  constructor() {
    this.csTerminalBody = document.getElementById("cs-terminal-body");
    this.cowrieTerminalBody = document.getElementById("cowrie-terminal-body");
    this.cmdInput = document.getElementById("terminal-cmd-input");
    this.csPromptLabel = document.getElementById("cs-prompt-label");
    this.vstTreeView = document.getElementById("vst-tree-view");
    this.csLatencyBadge = document.getElementById("cs-latency-badge");
    this.cowrieLatencyBadge = document.getElementById("cowrie-latency-badge");

    this.init();
  }

  init() {
    if (!this.cmdInput) return;

    // Enter key execution
    this.cmdInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const cmd = this.cmdInput.value.trim();
        if (cmd) {
          this.executeCommand(cmd);
          this.cmdInput.value = "";
        }
      }
    });

    // Preset scenario buttons
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const cmd = btn.getAttribute("data-cmd");
        if (cmd) {
          this.executeCommand(cmd);
        }
      });
    });

    // Initial VST tree load
    this.refreshVSTTree();
  }

  async executeCommand(cmd) {
    // 1. Append user input line to both terminals
    this.appendTerminalLine(this.csTerminalBody, `${this.csPromptLabel ? this.csPromptLabel.innerText : "root@ip-172-31-18-42:~# "} ${cmd}`, "cmd-echo");
    this.appendTerminalLine(this.cowrieTerminalBody, `root@svr04:~# ${cmd}`, "cmd-echo");

    try {
      const res = await fetch("/api/terminal/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd, target: "both" })
      });

      if (!res.ok) throw new Error("Server communication fault");
      const data = await res.json();

      // 2. Render ChameleonShell Response
      if (data.chameleonshell) {
        const exec = data.chameleonshell.execution;
        const mitre = data.chameleonshell.mitre;
        const rules = data.chameleonshell.synthesized_rules;

        if (exec.stdout) {
          this.appendTerminalLine(this.csTerminalBody, exec.stdout);
        }
        if (exec.stderr) {
          this.appendTerminalLine(this.csTerminalBody, exec.stderr, "error");
        }

        // Latency and path readout
        const pathLabel = exec.path_taken === "fast_path" ? "Fast-Path (Deterministic VST)" : "Slow-Path (Sandboxed Generative)";
        const latencyText = `${exec.latency_ms} ms [${pathLabel}]`;
        this.appendTerminalLine(this.csTerminalBody, `[TELEMETRY] Delta t = ${latencyText}`, "meta");

        if (this.csLatencyBadge) {
          this.csLatencyBadge.innerText = `${exec.latency_ms} ms`;
        }
        if (this.csPromptLabel && data.chameleonshell.prompt) {
          this.csPromptLabel.innerText = data.chameleonshell.prompt;
        }

        // Notify 3D WebGL core & MITRE visualizer
        if (window.webglCore && mitre) {
          window.webglCore.triggerThreatShift(mitre.severity);
        }
        if (window.mitreVisualizer && mitre) {
          window.mitreVisualizer.updateTelemetry(mitre, rules);
        }
      }

      // 3. Render Cowrie Baseline Response
      if (data.cowrie) {
        const cowrieExec = data.cowrie.execution;
        if (cowrieExec.stdout) {
          this.appendTerminalLine(this.cowrieTerminalBody, cowrieExec.stdout);
        }
        if (cowrieExec.stderr) {
          this.appendTerminalLine(this.cowrieTerminalBody, cowrieExec.stderr, "error");
        }

        const cowrieLatencyText = `${cowrieExec.latency_ms} ms [Static fs.pickle]`;
        this.appendTerminalLine(this.cowrieTerminalBody, `[BASELINE] Delta t = ${cowrieLatencyText}`, "meta");

        if (this.cowrieLatencyBadge) {
          this.cowrieLatencyBadge.innerText = `${cowrieExec.latency_ms} ms`;
        }
      }

      // 4. Refresh VST File Tree DAG
      this.refreshVSTTree();

    } catch (err) {
      this.appendTerminalLine(this.csTerminalBody, `[ERR] Terminal execution communication fault: ${err.message}`, "error");
    }

    // Scroll terminals to bottom
    this.scrollToBottom(this.csTerminalBody);
    this.scrollToBottom(this.cowrieTerminalBody);
  }

  appendTerminalLine(targetEl, text, className = "") {
    if (!targetEl) return;
    const div = document.createElement("div");
    div.className = `term-line-output ${className}`;
    div.innerText = text;
    targetEl.appendChild(div);
  }

  scrollToBottom(el) {
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }

  async refreshVSTTree() {
    if (!this.vstTreeView) return;
    try {
      const res = await fetch("/api/vst/tree");
      if (!res.ok) return;
      const data = await res.json();
      this.renderVSTNodes(data.tree, this.vstTreeView);
    } catch (e) {
      console.warn("VST tree poll error:", e);
    }
  }

  renderVSTNodes(node, container) {
    container.innerHTML = "";
    const list = document.createElement("div");

    function traverse(curr, depth = 0) {
      const indent = "  ".repeat(depth);
      const row = document.createElement("div");
      const icon = curr.is_dir ? "[DIR]" : "[FILE]";
      const perms = curr.permissions || "rw-r--r--";
      const sizeStr = curr.is_dir ? "4096 B" : `${curr.size} B`;
      const hashStr = curr.sha256 ? ` (sha256: ${curr.sha256}...)` : "";

      row.innerText = `${indent}${icon} ${curr.name || "/"}  <${perms}>  [${sizeStr}]${hashStr}`;
      row.style.color = curr.is_dir ? "var(--accent-volt)" : "var(--text-secondary)";
      list.appendChild(row);

      if (curr.is_dir && curr.children) {
        curr.children.forEach((child) => traverse(child, depth + 1));
      }
    }

    traverse(node, 0);
    container.appendChild(list);
  }
}

window.InteractiveHoneypotLab = InteractiveHoneypotLab;
