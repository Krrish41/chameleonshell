# GUIDELINES.md — Engineering, Anti-AI-Slop & Dual-Zone Architecture Constitution

> **CORE MANDATE:** This document defines the engineering standards, design system rules, dual-zone isolation protocols, and code quality invariants for **ChameleonShell**. Every contributor, subagent, and LLM session must strictly adhere to these rules.

---

## 1. DUAL-ZONE ISOLATION & ZERO-TRACE POLICY (ZONE A VS. ZONE B)

> [!CAUTION]
> **STRICT ZERO-PII / ZERO-ACADEMIC PUBLIC REPO & WEBSITE RULE (ZONE A):**
> The public web platform (`localhost:8080`), public routes, HTML/CSS/JS DOM, API endpoints, `README.md`, and all git-tracked repository files **MUST REMAIN 100% ANONYMIZED WITH ZERO PII AND ZERO ACADEMIC FOOTPRINT**. Never expose student names, registration numbers, course codes, review titles, or faculty details in any git-tracked file or web page.

### Zone Separation Protocols:
- **Zone A (Public GitHub Repository):** Contains production source code, unit tests, WebGL frontend, documentation, and Docker compose files. All authorship is attributed to the *ChameleonShell Threat Research Group*.
- **Zone B (Local Academic Vault `_academic_submissions/`):** Contains the official institutional capstone submission records, the IEEE Conference Paper (`IEEEtran`), presentation slide decks, and guide meeting records. This directory is strictly git-ignored via `.gitignore`.
- For internal university submission requirements and team rosters, refer to `_academic_submissions/ACADEMIC_CONTEXT_PRIVATE.md`.

---

## 3. UNIVERSAL DEVICE COMPATIBILITY & RESPONSIVE ENGINEERING

The web application **must** be 100% functional, responsive, and visually cohesive across all viewports, devices, input methods, and operating systems.

### A. Viewport & Breakpoint Matrix
Enforce `overflow-x: hidden` on the root container. Never allow horizontal layout spillover:
- **Compact Mobile (320px – 480px):** Single-column stacked layouts, condensed metric chips, bottom-sheet / drawer navigation, full-width touch actions.
- **Standard Mobile & Phablets (481px – 767px):** Balanced vertical rhythm, swipeable horizontally-scrolling data tables with subtle gradient indicators.
- **Tablets & Foldables (768px – 1024px):** Adaptive 2-column grid, compact header controls, dual orientation support.
- **Laptops & Desktops (1025px – 1440px):** Full multi-panel workspace, side-by-side terminal comparison view, telemetry HUDs.
- **Ultrawide & 4K Displays (>= 1441px):** Constrained maximum content width (`max-width: 1440px` or `1600px` for terminal lab), centered with balanced whitespace, line lengths strictly <= 75 characters for prose readability.

### B. Touch, Pointer & Input Agnostic Design
- **Touch Target Sizes:** Minimum interactive hit target of `44px x 44px` on coarse pointer devices (`@media (pointer: coarse)`).
- **No Hover-Only Functionality:** Any desktop `:hover` preview or tooltip must have an accessible tap/click/focus equivalent.
- **Virtual Keyboard Resilience:** Form inputs must specify proper HTML5 types (`type="text"`, `inputmode="search"`, etc.) and enforce font size >= 16px on mobile to avoid involuntary iOS Safari zoom.

### C. Fluid Typography & Scalable Media
- Use CSS `clamp()` functions for headlines, subheadings, and section padding.
- All SVG icons, WebGL canvases, charts, and media must specify `max-width: 100%; height: auto;` and adjust dynamically upon window resize.

---

## 4. THE "ANTI-AI-SLOP" DESIGN MANIFESTO

Inspired by high-craft benchmarks (`landonorris.com` by OFF+BRAND, `linear.app`, `palantir.com`, `crowdstrike.com`, `wiz.io`):

### 10 Critical Anti-AI-Slop Rules:
1. **ABSOLUTE ZERO EMOJIS:** Never use emojis in UI buttons, headings, terminal logs, code comments, slide decks, or documentation. Use sharp 1px/1.5px inline SVGs, military crosshairs, or technical badges (`[OK]`, `[WARN]`, `[CRIT]`, `::`, `//`).
2. **NO GENERIC PURPLE/PINK/CYAN MESH GRADIENTS:** Ban standard Tailwind `from-purple-600 via-pink-500` blobs. Use an architectural 4-tier obsidian ladder with deliberate tactical accents.
3. **NO GENERIC UNSTYLED TYPOGRAPHY:** Headings use geometric kinetic typography (`Space Grotesk` or `Syne`); body uses clean technical sans (`Plus Jakarta Sans` or `Inter`); terminal, metrics, and hashes use `JetBrains Mono` with `tabular-nums`.
4. **NO CARD-GRID CLICHES:** Ban repetitive 3-card equal grids with circular icons on top and generic copy. Use asymmetric Bento layouts with live interactive elements.
5. **NO MARKETING FLUFF:** Ban phrases like *"Unleash the power of AI"*, *"Revolutionizing cybersecurity"*, *"Seamless integration"*. Write empirical, precise technical prose formatted like defense research and industrial telemetry.
6. **NO FAKE RANDOM JUMPING CHARTS:** Charts and live readouts must be driven by actual simulated attack telemetry or real engine state.
7. **NO JANKY SCROLLBARS:** Provide custom dark hairline scrollbars and smooth inertial scrolling (**Lenis** + **GSAP ScrollTrigger**).
8. **NO MISSING FAVICON OR DEFAULT LOGOS:** Include bespoke vector SVG chameleon prism favicon with Apple Touch Icon and Web Manifest.
9. **NO UNSTYLED TABLES OR RAW JSON DUMPS:** All tables feature `1px solid rgba(255,255,255,0.07)` hairline dividers, tabular numbers, row hover states, and copy-to-clipboard interactions.
10. **NO DEAD CONTROLS OR BROKEN PLACEHOLDERS:** Every single button, tab, terminal input, scenario preset, filter, and paper download must be functional.

---

## 5. DESIGN SYSTEM TOKENS ("TACTICAL KINETIC TELEMETRY")

```css
:root {
  /* Surfaces */
  --bg-abyss: #060709;
  --bg-carbon: #0D0F12;
  --bg-graphite: #14171C;
  --bg-panel-hover: #1B1F26;
  --bg-glass: rgba(13, 15, 18, 0.85);

  /* Hairlines & Structural Borders */
  --border-hairline: rgba(255, 255, 255, 0.07);
  --border-medium: rgba(255, 255, 255, 0.12);
  --border-active: rgba(210, 255, 0, 0.45);
  --border-crimson: rgba(255, 42, 84, 0.45);

  /* Kinetic Accents */
  --accent-volt: #D2FF00;      /* Primary kinetic signal / CTA */
  --accent-emerald: #00F59B;   /* Fast-Path cache hit / coherent state */
  --accent-amber: #FFB800;     /* Slow-Path LLM generation / medium threat */
  --accent-crimson: #FF2A54;   /* Active intrusion / MITRE high severity / WAF block */
  --accent-cyan: #00E5FF;      /* Network socket & IMDSv2 indicator */

  /* Typography Colors */
  --text-primary: #F4F6F8;
  --text-secondary: #8E96A4;
  --text-muted: #525A65;
  --text-volt: #D2FF00;

  /* Fonts */
  --font-display: 'Space Grotesk', -apple-system, sans-serif;
  --font-body: 'Plus Jakarta Sans', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

---

## 6. ENGINEERING & SECURITY SANDBOXING INVARIANTS

1. **Deterministic Virtual State Tree (VST):**
   - The state $S_t = \langle \mathcal{F}_t, \mathcal{E}_t, \mathcal{P}_t, \mathcal{N}_t, \mathcal{C}_t, \tau_t \rangle$ is strictly maintained in memory/SQLite.
   - Fast-Path commands (`ls`, `cd`, `pwd`, `cat`, `touch`, `mkdir`, `rm`, `date`, `uptime`, `whoami`, `id`, `ps`) must resolve in $< 8\text{ ms}$ without calling external APIs.
   - Dynamic `/proc/uptime` and `/proc/meminfo` match real monotonic offsets to defeat botnet clock-fingerprinting.
2. **Safe LLM Slow-Path Fallback:**
   - When generative commands are executed, the LLM Slow-Path runs with strict JSON schemas and prompt guardrails.
   - Offline fallback heuristics provide realistic command emulation for 100% resilience during live evaluation without relying on external network connectivity.
3. **MITRE ATT&CK Classification:**
   - Sliding-window command sequence classification maps into Enterprise ATT&CK v16 Tactics (`TA0043` through `TA0040`) and Techniques.
   - Severity scoring enforces temporal decay: $\text{RiskScore}(C_{1:t}) = \min(100, \sum_{k=1}^t \gamma^{t-k} w(Y_k) \mathbb{I}(c_k))$.
4. **Synthesized Signatures:**
   - Every detected intrusion generates syntactically valid Snort 3, ModSecurity `SecRule`, and Linux `nftables`/`iptables` rules with valid SIDs and timestamps.

---

## 7. ENTERPRISE INFORMATION ARCHITECTURE & CANONICAL NAVIGATION

The ChameleonShell web platform strictly separates commercial product presentation from operations and deep-dive technical assets across dedicated enterprise routes:

| Route | Canonical Page Title | Purpose & Structural Content |
| :--- | :--- | :--- |
| `/` | Platform (Enterprise Home) | Clean 4-viewport landing: 3D Geodesic Icosahedron Deception Core hero, Trilemma Bento comparison, 5-step live attacker kill-chain preview card, enterprise capabilities grid, legal footer. |
| `/lab` | Live Lab | Dedicated operational SOC workspace: Dual split-pane interactive terminal (ChameleonShell vs Static Cowrie), live Inode DAG tree explorer, real-time MITRE ATT&CK Matrix heatmap, auto-rule synthesis console, multi-stage botnet simulator. |
| `/architecture` | Architecture Blueprint | Formal mathematical tuple definition, strict 12-column CSS Grid alignment where full-width cards match pixel-for-pixel with Subsystems 01, 02, and 03 cards, ASCII sequence flow pipeline. |
| `/benchmarks` | Empirical Benchmarks | Quantitative evaluation matrix (ChameleonShell vs Cowrie vs shelLM vs HoneyGPT) across depth, latency, consistency, and automated defense response. |
| `/whitepaper` | Technical Whitepaper | Technical research whitepaper viewer with semantic Unicode math tokens, print/PDF export, authored strictly by ChameleonShell Threat Research Group. |
| `/privacy` | Privacy Policy | Threat telemetry capture boundaries, SHA-256 IP anonymization, GDPR and data protection compliance. |
| `/terms` | Terms of Service | Authorized enterprise sandbox environment, containment safeguards, and proprietary intellectual property rights. |

### Canonical Header & Strict Single-Line Rules:
- **Height & Positioning:** Fixed `height: 68px; position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(16px); background: rgba(7, 8, 10, 0.88); border-bottom: 1px solid #1A1E26;`.
- **Zero-Wrap Invariant:** Every link, title, button, and telemetry badge in `.site-header` MUST specify `white-space: nowrap`. Height must never exceed 44px on desktop.
- **Header Components (Left to Right):**
  1. Brand: Chameleon prism SVG + `CHAMELEONSHELL` (`Space Grotesk`, `700`, `15px`) + compact pulsing `#00FF9D` 6px online dot.
  2. Center Links (5 items): `Platform` (`/`), `Live Lab` (`/lab`), `Architecture` (`/architecture`), `Benchmarks` (`/benchmarks`), `Whitepaper` (`/whitepaper`).
  3. Right Cluster: Compact `ENGINE: ONLINE · 4.8ms` pill + `LAUNCH LAB` primary CTA (`/lab`) + minimal 2-bar SVG mobile drawer toggle.
- **Mobile Drawer:** For `< 1024px` viewports, the center links collapse into a clean slide-over drawer toggled via `frontend/js/app.js`.

---

## 8. STRICT ZERO RAW LATEX LEAK POLICY & PRODUCTION VERIFICATION SUITE

### A. Zero Raw LaTeX Leak Rules
- **Prohibited:** Never render unparsed raw math delimiters (`$S_t$`, `$t$`, `$m_v$`, `\mathcal{F}`, `\tau`, `\Delta`) as raw strings in headings, prose, or cards.
- **Enforced Typography:**
  - Inline tokens: Render inside `<code class="math-token">...</code>` styled with monospace typography in `#D4FF00` (e.g. `<code class="math-token">S<sub>t</sub></code>`, `<code class="math-token">h<sub>v</sub> = H(c<sub>v</sub>)</code>`).
  - Display equations: Render inside `<pre class="math-block">` using clean Unicode mathematical notation (e.g. `Sₜ = ⟨ Fₜ, Eₜ, Pₜ, Nₜ, Cₜ, τₜ ⟩`).

### B. Automated Production Verification Suite (`scripts/verify_production_site.mjs`)
- All platform builds are verified programmatically via Playwright headless browser automation.
- **Scope:** 5 routes (`/`, `/lab`, `/architecture`, `/benchmarks`, `/whitepaper`) across 3 responsive viewports (`Desktop 1440x900`, `Tablet 768x1024`, `Mobile 390x844`) = 15 test runs.
- **Hard Assertions Enforced (100% Pass Required):**
  1. **Zero PII / Academic Leaks:** Asserts that `document.documentElement.innerHTML` matches 0 occurrences of blacklisted academic, institutional, or personal identifiers.
  2. **Zero Raw LaTeX:** Asserts that `document.body.innerText` contains 0 occurrences of `$` or `\mathcal`.
  3. **Single-Line Navbar:** Asserts that every header link and CTA button has `clientHeight <= 44px` and `white-space: nowrap` on desktop.
  4. **Strict 12-Column Grid Alignment:** On `/architecture` Desktop, asserts that Card 1 and Subsystem 03 right bounding-box edges align (`delta <= 2px`).
  5. **Zero Horizontal Overflow:** Asserts `document.documentElement.scrollWidth <= window.innerWidth` across all viewports.
- **Artifacts Generated:** Full-page stitched screenshots saved in `screenshots/<route>-<viewport>.png` and audit logs saved in `screenshots/production_verification_report.json`.

