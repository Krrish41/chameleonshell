/**
 * Automated Visual QA & Full-Page Screenshot Verification Suite
 * ChameleonShell Academic Deception Platform
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:8080';
const SCREENSHOTS_DIR = path.resolve('screenshots');

const ROUTES = [
  { path: '/', name: 'home' },
  { path: '/lab', name: 'lab' },
  { path: '/architecture', name: 'architecture' },
  { path: '/paper', name: 'paper' },
  { path: '/reviews', name: 'reviews' },
  { path: '/dossier', name: 'dossier' },
];

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844 },
];

async function runVisualQA() {
  if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
  }

  console.log('='.repeat(90));
  console.log('CHAMELEONSHELL AUTOMATED VISUAL QA & FULL-PAGE SCREENSHOT SUITE');
  console.log(`Connecting to: ${BASE_URL}`);
  console.log('='.repeat(90));

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

      let startTime = Date.now();
      let navigationError = null;

      try {
        await page.goto(`${BASE_URL}${route.path}`, {
          waitUntil: 'networkidle',
          timeout: 15000,
        });

        // Dismiss preloader if present
        await page.evaluate(() => {
          const preloader = document.getElementById('preloader');
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

        // ASSERTION 1: Zero LaTeX leaks in visible DOM text
        const latexLeaks = await page.evaluate(() => {
          const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
              acceptNode(node) {
                const tag = node.parentElement ? node.parentElement.tagName.toLowerCase() : '';
                if (['script', 'style', 'noscript'].includes(tag)) {
                  return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
              }
            }
          );
          const leaks = [];
          const mathPattern = /\$[a-zA-Z0-9_\{\\]+/;
          const texPattern = /\\(mathcal|tau|Delta|rangle|langle|rightarrow|subset|cup|cap)\b/;
          let n;
          while ((n = walker.nextNode())) {
            const txt = n.textContent.trim();
            if (!txt) continue;
            if (mathPattern.test(txt) || texPattern.test(txt)) {
              leaks.push({
                snippet: txt.substring(0, 50),
                tag: n.parentElement ? n.parentElement.tagName : 'UNKNOWN',
              });
            }
          }
          return leaks;
        });

        // ASSERTION 2: No horizontal overflow
        const overflowCheck = await page.evaluate(() => {
          const docWidth = document.documentElement.scrollWidth;
          const winWidth = window.innerWidth;
          return {
            hasOverflow: docWidth > winWidth + 2,
            docWidth,
            winWidth,
          };
        });

        // ASSERTION 3: No navbar text wrapping
        const navbarCheck = await page.evaluate((vpWidth) => {
          if (vpWidth < 768) return { hasWrap: false, items: [] };
          const header = document.querySelector('.site-header');
          if (!header) return { hasWrap: false, items: [] };
          const links = header.querySelectorAll('.nav-link, .btn-launch-nav, .brand-title');
          const issues = [];
          links.forEach((el) => {
            const rect = el.getBoundingClientRect();
            const cs = window.getComputedStyle(el);
            if (cs.whiteSpace !== 'nowrap') {
              issues.push({ text: el.textContent.trim(), issue: 'white-space not nowrap' });
            }
            if (rect.height > 48) {
              issues.push({ text: el.textContent.trim(), issue: `height ${rect.height}px > 48px` });
            }
          });
          return { hasWrap: issues.length > 0, items: issues };
        }, vp.width);

        // ASSERTION 4: Zero sibling card overlaps
        const overlapCheck = await page.evaluate(() => {
          const selectors = [
            '.bento-grid',
            '.trilemma-grid',
            '.module-grid',
            '.metric-strip',
            '.download-card-grid',
            '.section-grid-12',
          ];
          const detected = [];
          selectors.forEach((sel) => {
            const containers = document.querySelectorAll(sel);
            containers.forEach((cont) => {
              const children = Array.from(cont.children).filter((el) => {
                const style = window.getComputedStyle(el);
                return (
                  style.display !== 'none' &&
                  style.visibility !== 'hidden' &&
                  style.position !== 'absolute'
                );
              });
              for (let i = 0; i < children.length; i++) {
                const rA = children[i].getBoundingClientRect();
                if (rA.width === 0 || rA.height === 0) continue;
                for (let j = i + 1; j < children.length; j++) {
                  const rB = children[j].getBoundingClientRect();
                  if (rB.width === 0 || rB.height === 0) continue;
                  const xOverlap = Math.max(0, Math.min(rA.right, rB.right) - Math.max(rA.left, rB.left));
                  const yOverlap = Math.max(0, Math.min(rA.bottom, rB.bottom) - Math.max(rA.top, rB.top));
                  if (xOverlap > 3 && yOverlap > 3) {
                    detected.push({
                      container: sel,
                      childA: children[i].className || children[i].tagName,
                      childB: children[j].className || children[j].tagName,
                      xOverlap,
                      yOverlap,
                    });
                  }
                }
              }
            });
          });
          return { hasOverlap: detected.length > 0, overlaps: detected };
        });

        // ASSERTION 5: Strict 12-column alignment on /architecture
        const gridAlignmentCheck = await page.evaluate(({ isArch, isDesktop }) => {
          if (!isArch || !isDesktop) return { applicable: false, aligned: true, delta: 0 };
          const card1 = document.querySelector('.full-width-grid-card');
          const memberCards = document.querySelectorAll('.terminal-card[style*="span 4"]');
          if (!card1 || memberCards.length < 3) return { applicable: true, aligned: true, delta: 0 };
          const r1 = card1.getBoundingClientRect();
          const rLast = memberCards[2].getBoundingClientRect();
          const delta = Math.abs(r1.right - rLast.right);
          return {
            applicable: true,
            aligned: delta <= 2,
            delta: Math.round(delta * 100) / 100,
          };
        }, { isArch: route.path === '/architecture', isDesktop: vp.name === 'desktop' });

        const isClean =
          latexLeaks.length === 0 &&
          !overflowCheck.hasOverflow &&
          !navbarCheck.hasWrap &&
          !overlapCheck.hasOverlap &&
          gridAlignmentCheck.aligned;

        if (isClean) passedTests++;

        results.push({
          route: route.path,
          viewport: vp.name,
          width: vp.width,
          durationMs: Date.now() - startTime,
          screenshot: screenshotFilename,
          assertions: {
            latexClean: latexLeaks.length === 0,
            latexLeaks,
            noOverflow: !overflowCheck.hasOverflow,
            overflowData: overflowCheck,
            noNavbarWrap: !navbarCheck.hasWrap,
            navbarIssues: navbarCheck.items,
            noCardOverlap: !overlapCheck.hasOverlap,
            overlaps: overlapCheck.overlaps,
            gridAligned: gridAlignmentCheck.aligned,
            gridDelta: gridAlignmentCheck.delta,
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

  // Save JSON report
  const reportPath = path.join(SCREENSHOTS_DIR, 'qa_report.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2), 'utf-8');

  // Print Clean ASCII Results Table
  console.log('\n' + '='.repeat(90));
  console.log(
    'ROUTE'.padEnd(16) +
    'VIEWPORT'.padEnd(12) +
    'LATENCY'.padEnd(10) +
    'NO-LATEX'.padEnd(10) +
    'NO-OVRFLW'.padEnd(11) +
    'NO-WRAP'.padEnd(10) +
    'NO-OVRLP'.padEnd(10) +
    'GRID-ALN'.padEnd(10) +
    'STATUS'
  );
  console.log('-'.repeat(90));

  for (const r of results) {
    if (r.status === 'ERROR') {
      console.log(`${r.route.padEnd(16)}${r.viewport.padEnd(12)}${r.status}: ${r.error}`);
      continue;
    }
    const a = r.assertions;
    const line =
      r.route.padEnd(16) +
      r.viewport.padEnd(12) +
      `${r.durationMs}ms`.padEnd(10) +
      (a.latexClean ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.noOverflow ? '[OK]' : '[FAIL]').padEnd(11) +
      (a.noNavbarWrap ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.noCardOverlap ? '[OK]' : '[FAIL]').padEnd(10) +
      (a.gridAligned ? '[OK]' : '[FAIL]').padEnd(10) +
      `[${r.status}]`;
    console.log(line);
  }

  console.log('='.repeat(90));
  console.log(`SUMMARY: ${passedTests} / ${totalTests} Viewport Tests PASSED.`);
  console.log(`Screenshots and JSON report saved to: ${SCREENSHOTS_DIR}`);
  console.log('='.repeat(90));

  if (passedTests !== totalTests) {
    console.error('\n[!] Visual QA encountered failures. Inspect details in qa_report.json');
    process.exit(1);
  } else {
    console.log('\n[+] All Visual QA Assertions Passed with Zero Violations.');
    process.exit(0);
  }
}

runVisualQA().catch((e) => {
  console.error('[FATAL]', e);
  process.exit(1);
});
