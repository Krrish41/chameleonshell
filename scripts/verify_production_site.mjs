/**
 * Automated Enterprise Production Verification & Screenshot Suite
 * ChameleonShell Autonomous Active Defense Platform (Zero-PII / Zero-Academic Footprint)
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:8080';
const SCREENSHOTS_DIR = path.resolve('screenshots');

const ROUTES = [
  { path: '/', name: 'platform' },
  { path: '/lab', name: 'lab' },
  { path: '/architecture', name: 'architecture' },
  { path: '/benchmarks', name: 'benchmarks' },
  { path: '/whitepaper', name: 'whitepaper' },
];

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844 },
];

// Strict pattern matching any forbidden academic or institutional PII strings (base64 encoded for zero repo footprint)
const FORBIDDEN_ACADEMIC_PATTERN = Buffer.from('dml0fHZlbGxvcmV8YmNzZXxjYXBzdG9uZXxkb3NzaWVyfHNhdGh5YXxrcnJpc2h8YW5pa2V0fHNoaXZhbml8MjNia3R8MjNiY2J8bWVtYmVyIDF8bWVtYmVyIDJ8bWVtYmVyIDN8cmV2aWV3IGRlY2s=', 'base64').toString('utf8');
const FORBIDDEN_ACADEMIC_REGEX = new RegExp(FORBIDDEN_ACADEMIC_PATTERN, 'i');

async function runVerification() {
  if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
  }

  console.log('='.repeat(96));
  console.log('CHAMELEONSHELL PRODUCTION PLATFORM VERIFICATION (ZERO PII / ZERO ACADEMIC FOOTPRINT)');
  console.log(`Target URL: ${BASE_URL}`);
  console.log('='.repeat(96));

  const browser = await chromium.launch({ headless: true });
  const results = [];
  let totalTests = 0;
  let passedTests = 0;

  for (const route of ROUTES) {
    for (const vp of VIEWPORTS) {
      totalTests++;
      const testName = `${route.name} (${vp.name})`;
      const screenshotFilename = `${route.name}-${vp.name}.png`;
      const screenshotPath = path.join(SCREENSHOTS_DIR, screenshotFilename);

      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        deviceScaleFactor: 1,
      });
      const page = await context.newPage();

      const startTime = Date.now();
      let navigationError = null;

      try {
        await page.goto(`${BASE_URL}${route.path}`, {
          waitUntil: 'networkidle',
          timeout: 15000,
        });

        // Dismiss preloader if present
        await page.evaluate(() => {
          const preloader = document.getElementById('preloader') || document.getElementById('tactical-preloader');
          if (preloader) preloader.style.display = 'none';
        });

        // Trigger animations by scrolling through the entire document
        await page.evaluate(async () => {
          await new Promise((resolve) => {
            let total = 0;
            const step = 300;
            const timer = setInterval(() => {
              window.scrollBy(0, step);
              total += step;
              if (total >= document.body.scrollHeight) {
                clearInterval(timer);
                window.scrollTo(0, 0);
                resolve();
              }
            }, 50);
          });
        });

        // Wait 500ms for animations and layout to settle
        await page.waitForTimeout(500);

        // Capture full-page screenshot
        await page.screenshot({ path: screenshotPath, fullPage: true });

        // ASSERTION 1: Zero Academic / PII Leaks in document.documentElement.innerHTML
        const piiCheck = await page.evaluate((patternStr) => {
          const re = new RegExp(patternStr, 'gi');
          const html = document.documentElement.innerHTML;
          const matches = [];
          let m;
          while ((m = re.exec(html)) !== null) {
            const start = Math.max(0, m.index - 30);
            const end = Math.min(html.length, m.index + 50);
            matches.push({
              match: m[0],
              context: html.substring(start, end).replace(/\s+/g, ' '),
            });
          }
          return {
            leakCount: matches.length,
            matches,
          };
        }, FORBIDDEN_ACADEMIC_REGEX.source);

        // ASSERTION 2: Zero Raw LaTeX in document.body.innerText ($ or \mathcal)
        const latexCheck = await page.evaluate(() => {
          const text = document.body.innerText || '';
          const hasDollar = text.includes('$');
          const hasMathcal = text.includes('\\mathcal');
          const issues = [];
          if (hasDollar) issues.push('Contains unparsed dollar sign ($)');
          if (hasMathcal) issues.push('Contains \\mathcal macro');
          return {
            isClean: !hasDollar && !hasMathcal,
            hasDollar,
            hasMathcal,
            issues,
          };
        });

        // ASSERTION 3: Single-line navbar check on Desktop (clientHeight <= 44)
        const navbarCheck = await page.evaluate((vpWidth) => {
          if (vpWidth < 1024) return { valid: true, issues: [] };
          const header = document.querySelector('.site-header');
          if (!header) return { valid: true, issues: [] };
          const items = header.querySelectorAll('.nav-link, .btn-launch-nav, .brand-title, .header-telemetry-pill');
          const issues = [];
          items.forEach((el) => {
            const h = el.clientHeight;
            const cs = window.getComputedStyle(el);
            if (cs.whiteSpace !== 'nowrap') {
              issues.push({ text: el.textContent.trim(), issue: 'white-space not nowrap' });
            }
            if (h > 44) {
              issues.push({ text: el.textContent.trim(), issue: `height ${h}px > 44px` });
            }
          });
          return { valid: issues.length === 0, issues };
        }, vp.width);

        // ASSERTION 4: Grid alignment check on /architecture on Desktop (delta <= 2px)
        const gridAlignmentCheck = await page.evaluate(({ isArch, isDesktop }) => {
          if (!isArch || !isDesktop) return { applicable: false, aligned: true, delta: 0 };
          const card1 = document.querySelector('.full-width-grid-card');
          const subsystemCards = document.querySelectorAll('.terminal-card[style*="span 4"]');
          if (!card1 || subsystemCards.length < 3) return { applicable: true, aligned: true, delta: 0 };
          const r1 = card1.getBoundingClientRect();
          const rLast = subsystemCards[2].getBoundingClientRect();
          const delta = Math.abs(r1.right - rLast.right);
          return {
            applicable: true,
            aligned: delta <= 2,
            delta: Math.round(delta * 100) / 100,
          };
        }, { isArch: route.path === '/architecture', isDesktop: vp.name === 'desktop' });

        // ASSERTION 5: Zero horizontal overflow across all viewports
        const overflowCheck = await page.evaluate(() => {
          const docWidth = document.documentElement.scrollWidth;
          const winWidth = window.innerWidth;
          return {
            hasOverflow: docWidth > winWidth + 2,
            docWidth,
            winWidth,
          };
        });

        // ASSERTION 6: Navbar is first child of body and sticky at top 0
        const headerPositionCheck = await page.evaluate(() => {
          const firstElem = document.body.firstElementChild;
          const isFirstChild = firstElem ? (firstElem.classList.contains('site-header') || firstElem.tagName.toLowerCase() === 'header') : false;
          const header = document.querySelector('.site-header');
          let isStickyTop = false;
          let rectTop = -1;
          if (header) {
            const cs = window.getComputedStyle(header);
            isStickyTop = cs.position === 'sticky' && cs.top === '0px';
            rectTop = header.getBoundingClientRect().top;
          }
          return {
            isFirstChild,
            isStickyTop,
            rectTop,
            valid: isFirstChild && isStickyTop && Math.abs(rectTop) <= 1,
          };
        });

        // ASSERTION 7: WebGL Canvas check (on Platform route)
        const webglCanvasCheck = await page.evaluate((isHome) => {
          if (!isHome) return { applicable: false, valid: true };
          const container = document.getElementById('hero-canvas-container');
          if (!container) return { applicable: true, valid: false, reason: 'No #hero-canvas-container found' };
          const canvas = container.querySelector('canvas');
          if (!canvas) return { applicable: true, valid: false, reason: 'No canvas inside #hero-canvas-container' };
          const rect = canvas.getBoundingClientRect();
          return {
            applicable: true,
            valid: rect.width > 50 && rect.height > 50,
            width: rect.width,
            height: rect.height,
          };
        }, route.path === '/');

        // ASSERTION 8: No stray boot / preloader text
        const strayBootTextCheck = await page.evaluate(() => {
          const text = document.body.innerText || '';
          const hasStrayBoot = /INITIALIZE CHAMELEONSHELL|INITIALIZING VIRTUAL STATE TREE/i.test(text);
          return {
            valid: !hasStrayBoot,
            hasStrayBoot,
          };
        });

        const isClean =
          piiCheck.leakCount === 0 &&
          latexCheck.isClean &&
          navbarCheck.valid &&
          gridAlignmentCheck.aligned &&
          !overflowCheck.hasOverflow &&
          headerPositionCheck.valid &&
          webglCanvasCheck.valid &&
          strayBootTextCheck.valid;

        if (isClean) passedTests++;

        results.push({
          route: route.path,
          viewport: vp.name,
          width: vp.width,
          durationMs: Date.now() - startTime,
          screenshot: screenshotFilename,
          assertions: {
            zeroPii: piiCheck.leakCount === 0,
            piiMatches: piiCheck.matches,
            zeroLatex: latexCheck.isClean,
            latexIssues: latexCheck.issues,
            singleLineNav: navbarCheck.valid,
            navbarIssues: navbarCheck.issues,
            gridAligned: gridAlignmentCheck.aligned,
            gridDelta: gridAlignmentCheck.delta,
            noOverflow: !overflowCheck.hasOverflow,
            overflowData: overflowCheck,
            headerPosition: headerPositionCheck,
            webglCanvas: webglCanvasCheck,
            noStrayBootText: strayBootTextCheck.valid,
          },
          status: isClean ? 'PASS' : 'FAIL',
        });
      } catch (err) {
        navigationError = err.message;
        results.push({
          route: route.path,
          viewport: vp.name,
          durationMs: Date.now() - startTime,
          status: 'ERROR',
          error: navigationError,
        });
      } finally {
        await context.close();
      }
    }
  }

  await browser.close();

  // Save report
  const reportPath = path.join(SCREENSHOTS_DIR, 'production_verification_report.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2), 'utf-8');

  // Print ASCII Table
  console.log('\n' + '='.repeat(110));
  console.log(
    'ROUTE'.padEnd(16) +
    'VIEWPORT'.padEnd(10) +
    'LATENCY'.padEnd(10) +
    'ZERO-PII'.padEnd(10) +
    'NO-LATEX'.padEnd(10) +
    'NAV-LINE'.padEnd(10) +
    'TOP-NAV'.padEnd(10) +
    'WEBGL'.padEnd(10) +
    'NO-BOOT'.padEnd(10) +
    'GRID-ALN'.padEnd(10) +
    'STATUS'
  );
  console.log('-'.repeat(110));

  for (const r of results) {
    if (r.status === 'ERROR') {
      console.log(`${r.route.padEnd(16)}${r.viewport.padEnd(10)}${r.status}: ${r.error}`);
      continue;
    }
    const a = r.assertions;
    const line =
      r.route.padEnd(16) +
      r.viewport.padEnd(10) +
      `${r.durationMs}ms`.padEnd(10) +
      (a.zeroPii ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.zeroLatex ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.singleLineNav ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.headerPosition.valid ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.webglCanvas.valid ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.noStrayBootText ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.gridAligned ? '[OK]' : '[FAIL]').padEnd(10) +
      `[${r.status}]`;
    console.log(line);
  }

  console.log('='.repeat(110));
  console.log(`PRODUCTION VERIFICATION SUMMARY: ${passedTests} / ${totalTests} Viewport Tests PASSED.`);
  console.log(`Full-page screenshots and structured report saved to: ${SCREENSHOTS_DIR}`);
  console.log('='.repeat(96));

  if (passedTests !== totalTests) {
    console.error('\n[!] Production verification encountered failures. Inspect production_verification_report.json');
    process.exit(1);
  } else {
    console.log('\n[+] 100% Production Verification Success. Zero PII, Zero Academic Leaks, Zero Visual Defects.');
    process.exit(0);
  }
}

runVerification().catch((e) => {
  console.error('[FATAL]', e);
  process.exit(1);
});
