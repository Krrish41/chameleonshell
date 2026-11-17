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

    const basePath = window.__BASE_PATH__ || (window.location.pathname.startsWith("/chameleonshell") ? "/chameleonshell" : "");
    try {
      const res = await fetch(`${basePath}/api/terminal/execute`, {
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
      // Offline / Static GitHub Pages Emulation Fallback
      this.handleOfflineExecution(cmd);
    }

    // Scroll terminals to bottom
    this.scrollToBottom(this.csTerminalBody);
    this.scrollToBottom(this.cowrieTerminalBody);
  }

  handleOfflineExecution(cmd) {
    const isShadow = cmd.includes("shadow");
    const isPasswd = cmd.includes("passwd");
    const isCloud = cmd.includes("169.254.169.254");
    const isSuid = cmd.includes("perm") || cmd.includes("suid");
    const isUname = cmd.includes("uname");
    const isWhoami = cmd.includes("whoami");
    const isId = cmd.trim() === "id";
    const isUptime = cmd.includes("uptime");
    const isLs = cmd.startsWith("ls");
    const isPwd = cmd.trim() === "pwd";

    let csStdout = "";
    let csStderr = "";
    let cowrieStdout = "";
    let cowrieStderr = "";
    let latencyMs = 4.8;
    let pathLabel = "Fast-Path (Deterministic VST)";
    let mitre = { tactic_id: "TA0007", tactic_name: "Discovery", technique_id: "T1059.004", severity: "LOW" };
    let rules = {
      nftables: `# Autonomous nftables Rule (Simulated)\ntable inet filter {\n    chain input { type filter hook input priority 0; drop; }\n}`,
      snort3: `drop tcp any any -> any any (msg:"[ChameleonShell Trapped]"; sid:100001; rev:1;)`,
      modsecurity: `SecRule REQUEST_URI "@contains /" "id:10001,phase:1,deny,status:403"`
    };

    if (isShadow) {
      csStdout = "root:$6$K7xG4J3q$m5...:19245:0:99999:7:::\ndaemon:*:19000:0:99999:7:::\nwww-data:*:19000:0:99999:7:::";
      cowrieStderr = "cat: /etc/shadow: Permission denied";
      latencyMs = 4.2;
      mitre = { tactic_id: "TA0006", tactic_name: "Credential Access", technique_id: "T1003.008", severity: "HIGH" };
      rules.nftables = `table inet filter {\n    chain input {\n        ip saddr 185.220.101.4 drop comment "[T1003.008] /etc/shadow credential harvest"\n    }\n}`;
    } else if (isCloud) {
      csStdout = "ami-id\ninstance-type\niam/\nsecurity-credentials/production-cluster-node-role";
      cowrieStderr = "curl: (7) Failed to connect to 169.254.169.254 port 80: Connection timed out";
      latencyMs = 18.2;
      pathLabel = "Slow-Path (Sandboxed Generative)";
      mitre = { tactic_id: "TA0007", tactic_name: "Discovery", technique_id: "T1580", severity: "HIGH" };
      rules.modsecurity = `SecRule REQUEST_URI "@contains 169.254.169.254" "id:1002,phase:1,deny,status:403,msg:'AWS IMDS Decoy Intercept'"`;
    } else if (isSuid) {
      csStdout = "/usr/bin/sudo\n/usr/bin/pkexec\n/usr/bin/passwd\n/usr/bin/gpasswd\n/usr/bin/chsh";
      cowrieStdout = "/bin/su";
      latencyMs = 5.1;
      mitre = { tactic_id: "TA0004", tactic_name: "Privilege Escalation", technique_id: "T1548.001", severity: "MEDIUM" };
    } else if (isUname) {
      csStdout = "Linux ip-172-31-18-42 5.15.0-1031-aws #35-Ubuntu SMP Fri Feb 11 02:08:44 UTC 2022 x86_64 GNU/Linux";
      cowrieStdout = "Linux svr04 3.2.0-4-amd64 #1 SMP Debian 3.2.51-1 x86_64 GNU/Linux";
      latencyMs = 3.9;
    } else if (isWhoami) {
      csStdout = "root";
      cowrieStdout = "root";
      latencyMs = 3.6;
    } else if (isId) {
      csStdout = "uid=0(root) gid=0(root) groups=0(root)";
      cowrieStdout = "uid=0(root) gid=0(root) groups=0(root)";
      latencyMs = 3.8;
    } else if (isUptime) {
      csStdout = " 07:22:19 up 14 days,  3:18,  1 user,  load average: 0.08, 0.03, 0.01";
      cowrieStdout = " 07:22:19 up 10 min,  1 user,  load average: 0.00, 0.00, 0.00";
      latencyMs = 3.9;
    } else if (isLs) {
      csStdout = "total 28\ndrwx------ 4 root root 4096 Nov 5 00:00 .\ndrwxr-xr-x 23 root root 4096 Nov 5 00:00 ..\n-rw------- 1 root root  420 Nov 5 00:00 .bash_history\n-rw-r--r-- 1 root root 3106 Nov 5 00:00 .bashrc\ndrwx------ 2 root root 4096 Nov 5 00:00 .ssh\n-rw-r--r-- 1 root root  161 Nov 5 00:00 .profile\n-rw-r--r-- 1 root root  820 Nov 5 00:00 deploy_credentials.env";
      cowrieStdout = "deploy_credentials.env";
      latencyMs = 4.4;
    } else if (isPwd) {
      csStdout = "/root";
      cowrieStdout = "/root";
      latencyMs = 3.5;
    } else {
      csStdout = `[SIMULATED POSIX AST] ${cmd}: command executed successfully (VST state persistent).`;
      cowrieStderr = `bash: ${cmd.split(" ")[0]}: command not found`;
      latencyMs = 4.8;
    }

    if (csStdout) this.appendTerminalLine(this.csTerminalBody, csStdout);
    if (csStderr) this.appendTerminalLine(this.csTerminalBody, csStderr, "error");
    this.appendTerminalLine(this.csTerminalBody, `[TELEMETRY] Delta t = ${latencyMs} ms [${pathLabel}]`, "meta");

    if (cowrieStdout) this.appendTerminalLine(this.cowrieTerminalBody, cowrieStdout);
    if (cowrieStderr) this.appendTerminalLine(this.cowrieTerminalBody, cowrieStderr, "error");
    this.appendTerminalLine(this.cowrieTerminalBody, `[BASELINE] Delta t = 14.5 ms [Static fs.pickle]`, "meta");

    if (this.csLatencyBadge) this.csLatencyBadge.innerText = `${latencyMs} ms`;
    if (this.cowrieLatencyBadge) this.cowrieLatencyBadge.innerText = "14.5 ms";

    if (window.webglCore) window.webglCore.triggerThreatShift(mitre.severity);
    if (window.mitreVisualizer) window.mitreVisualizer.updateTelemetry(mitre, rules);
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
    const basePath = window.__BASE_PATH__ || (window.location.pathname.startsWith("/chameleonshell") ? "/chameleonshell" : "");
    try {
      let res = await fetch(`${basePath}/api/vst/tree`);
      if (!res.ok) res = await fetch(`${basePath}/api/vst/tree.json`);
      if (!res.ok) throw new Error("VST fetch failed");
      const data = await res.json();
      this.renderVSTNodes(data.tree, this.vstTreeView);
    } catch (e) {
      // Fallback static tree for GitHub Pages
      const fallbackTree = {
        name: "/",
        is_dir: true,
        permissions: "rwxr-xr-x",
        children: [
          {
            name: "root",
            is_dir: true,
            permissions: "rwx------",
            children: [
              { name: ".bashrc", is_dir: false, permissions: "rw-r--r--", size: 3106, sha256: "b94d27b9" },
              { name: "deploy_credentials.env", is_dir: false, permissions: "rw-r--r--", size: 820, sha256: "7a8f9c11" },
              { name: ".ssh", is_dir: true, permissions: "rwx------", children: [
                { name: "authorized_keys", is_dir: false, permissions: "rw-------", size: 564, sha256: "c3d4e5f6" }
              ]}
            ]
          },
          {
            name: "etc",
            is_dir: true,
            permissions: "rwxr-xr-x",
            children: [
              { name: "shadow", is_dir: false, permissions: "rw-------", size: 1240, sha256: "98fa10bc" },
              { name: "passwd", is_dir: false, permissions: "rw-r--r--", size: 2190, sha256: "e4f5a6b7" },
              { name: "hostname", is_dir: false, permissions: "rw-r--r--", size: 16, sha256: "11223344" }
            ]
          },
          {
            name: "var",
            is_dir: true,
            permissions: "rwxr-xr-x",
            children: [
              { name: "log", is_dir: true, permissions: "rwxr-xr-x", children: [
                { name: "auth.log", is_dir: false, permissions: "rw-r-----", size: 40960, sha256: "d5e6f7a8" }
              ]}
            ]
          }
        ]
      };
      this.renderVSTNodes(fallbackTree, this.vstTreeView);
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
