/**
 * ChameleonShell: Threat Intel SOC Telemetry Feed & Asciinema Replay Controller
 * Drives automated botnet attack campaign execution and step-by-step session playback.
 */

class SOCSessionReplay {
  constructor() {
    this.campaignListEl = document.getElementById("campaign-select-list");
    this.runCampaignBtn = document.getElementById("run-campaign-btn");
    this.campaignStatusEl = document.getElementById("campaign-run-status");
    this.replayTerminalEl = document.getElementById("replay-terminal-display");
    this.replayPlayBtn = document.getElementById("replay-play-btn");
    this.replayProgress = document.getElementById("replay-progress-fill");

    this.isPlaying = false;
    this.castData = null;
    this.currentFrameIdx = 0;
    this.replayTimer = null;

    this.init();
  }

  async init() {
    this.setupCampaignTriggers();
    this.setupReplayControls();
    await this.loadSampleCast();
  }

  setupCampaignTriggers() {
    if (!this.runCampaignBtn || !this.campaignListEl) return;

    this.runCampaignBtn.addEventListener("click", async () => {
      const selectedKey = this.campaignListEl.value;
      if (!selectedKey) return;

      this.runCampaignBtn.disabled = true;
      if (this.campaignStatusEl) {
        this.campaignStatusEl.innerText = `[RUNNING] Executing ${selectedKey.toUpperCase()}...`;
        this.campaignStatusEl.style.color = "var(--accent-volt)";
      }

      try {
        const res = await fetch(`/api/campaigns/${selectedKey}/run`, { method: "POST" });
        if (!res.ok) throw new Error("Campaign execution failed");
        const data = await res.json();

        if (this.campaignStatusEl) {
          this.campaignStatusEl.innerText = `[COMPLETE] ${data.total_steps} commands executed | Final Risk: ${data.final_risk_score.toFixed(1)}`;
          this.campaignStatusEl.style.color = "var(--accent-emerald)";
        }

        // If interactive lab is present, trigger a full tree refresh
        if (window.interactiveLab) {
          window.interactiveLab.refreshVSTTree();
        }

      } catch (err) {
        if (this.campaignStatusEl) {
          this.campaignStatusEl.innerText = `[ERROR] ${err.message}`;
          this.campaignStatusEl.style.color = "var(--accent-crimson)";
        }
      } finally {
        this.runCampaignBtn.disabled = false;
      }
    });
  }

  async loadSampleCast() {
    try {
      const res = await fetch("/assets/sample-sessions/attack_alpha.cast");
      if (!res.ok) return;
      const text = await res.text();
      const lines = text.trim().split("\n");
      if (lines.length > 1) {
        this.castHeader = JSON.parse(lines[0]);
        this.castEvents = lines.slice(1).map((l) => JSON.parse(l));
      }
    } catch (e) {
      console.warn("Could not load sample cast:", e);
    }
  }

  setupReplayControls() {
    if (!this.replayPlayBtn) return;
    this.replayPlayBtn.addEventListener("click", () => {
      if (this.isPlaying) {
        this.pauseReplay();
      } else {
        this.startReplay();
      }
    });
  }

  async startReplay() {
    if (!this.castEvents || this.castEvents.length === 0) {
      await this.loadSampleCast();
    }
    if (!this.castEvents || this.castEvents.length === 0) {
      if (this.replayTerminalEl) {
        this.replayTerminalEl.innerText = "[INFO] Loading sample session attack replay...";
      }
      return;
    }
    this.isPlaying = true;
    this.replayPlayBtn.innerText = "[PAUSE REPLAY]";

    if (this.currentFrameIdx >= this.castEvents.length) {
      this.currentFrameIdx = 0;
      if (this.replayTerminalEl) this.replayTerminalEl.innerText = "";
    }

    // Immediately render first frame so UI changes on click without delay
    const firstFrame = this.castEvents[this.currentFrameIdx];
    if (firstFrame && this.replayTerminalEl && firstFrame[1] === "o") {
      this.replayTerminalEl.innerText += firstFrame[2];
      this.currentFrameIdx++;
    }

    this.playNextFrame();
  }

  pauseReplay() {
    this.isPlaying = false;
    clearTimeout(this.replayTimer);
    if (this.replayPlayBtn) this.replayPlayBtn.innerText = "[RESUME REPLAY]";
  }

  playNextFrame() {
    if (!this.isPlaying) return;
    if (this.currentFrameIdx >= this.castEvents.length) {
      this.isPlaying = false;
      this.replayPlayBtn.innerText = "[REPLAY AGAIN]";
      return;
    }

    const frame = this.castEvents[this.currentFrameIdx];
    const delay = this.currentFrameIdx === 0 ? 300 : (frame[0] - this.castEvents[this.currentFrameIdx - 1][0]) * 1000;

    this.replayTimer = setTimeout(() => {
      if (this.replayTerminalEl && frame[1] === "o") {
        this.replayTerminalEl.innerText += frame[2];
        this.replayTerminalEl.scrollTop = this.replayTerminalEl.scrollHeight;
      }

      this.currentFrameIdx++;
      if (this.replayProgress) {
        const pct = (this.currentFrameIdx / this.castEvents.length) * 100;
        this.replayProgress.style.width = `${pct}%`;
      }

      this.playNextFrame();
    }, Math.min(Math.max(delay, 100), 1200)); // normalized playback speed
  }
}

window.SOCSessionReplay = SOCSessionReplay;
