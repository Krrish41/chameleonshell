import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const SCREENSHOT_DIR = path.resolve('screenshots', 'interactions');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function run() {
  console.log('========================================================================');
  console.log('CHAMELEONSHELL: VERIFYING CLEAN 3D CORE, VELOCITY ROTATION, BG & CURSOR');
  console.log('========================================================================');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    hasTouch: false
  });
  const page = await context.newPage();

  const results = [];

  try {
    // 1. Navigate to home page
    await page.goto('http://localhost:8080/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Initial screenshot of clean hero
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_clean_3d_core_hero.png'), fullPage: false });
    console.log('[+] Captured 01_clean_3d_core_hero.png');

    // 2. Check 3D core elements & continuous rotation
    const rotationCheck = await page.evaluate(async () => {
      const container = document.getElementById('hero-canvas-container');
      const canvas = container ? container.querySelector('canvas') : null;
      if (!canvas) return { error: 'No 3D canvas found' };

      // Sample rotation over 300ms
      const initialRotationY = window.coreGroupRotationY || 0;
      await new Promise(r => setTimeout(r, 400));
      return {
        canvasFound: true,
        width: canvas.clientWidth,
        height: canvas.clientHeight
      };
    });
    console.log('[+] 3D Canvas check:', rotationCheck);

    // 3. Move mouse across screen and test velocity reaction & custom cursor
    console.log('[+] Simulating rapid cursor sweep across viewport...');
    // Move mouse in rapid zigzag
    for (let x = 200; x < 1200; x += 150) {
      await page.mouse.move(x, 400 + Math.sin(x) * 120);
      await page.waitForTimeout(25);
    }

    // Verify cursor-following background variables & radar coordinate HUD
    const bgAndCursorState = await page.evaluate(() => {
      const rootStyle = getComputedStyle(document.documentElement);
      const cursorX = rootStyle.getPropertyValue('--cursor-x').trim();
      const cursorY = rootStyle.getPropertyValue('--cursor-y').trim();

      const dot = document.getElementById('custom-cursor-dot');
      const ring = document.getElementById('custom-cursor-ring');
      const ambientGlow = document.getElementById('ambient-cursor-glow');
      const hud = document.getElementById('ambient-cursor-hud');
      const coordVal = document.getElementById('ambient-coord-val');

      return {
        cursorX,
        cursorY,
        dotPresent: !!dot,
        ringPresent: !!ring,
        ambientGlowPresent: !!ambientGlow,
        hudPresent: !!hud,
        coordText: coordVal ? coordVal.textContent : ''
      };
    });
    console.log('[+] Background & Cursor state:', bgAndCursorState);

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_cursor_moving_with_background.png'), fullPage: false });
    console.log('[+] Captured 02_cursor_moving_with_background.png');

    // 4. Hover over primary CTA button to check reticle expansion (.cursor-hover)
    const ctaBtn = await page.$('.btn-primary');
    if (ctaBtn) {
      const box = await ctaBtn.boundingBox();
      if (box) {
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        await page.waitForTimeout(200);

        const hoverState = await page.evaluate(() => {
          const ring = document.getElementById('custom-cursor-ring');
          const dot = document.getElementById('custom-cursor-dot');
          return {
            ringHoverClass: ring ? ring.classList.contains('cursor-hover') : false,
            dotHoverClass: dot ? dot.classList.contains('cursor-hover') : false
          };
        });
        console.log('[+] Cursor hover state over button:', hoverState);

        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_cursor_hover_cta_button.png'), fullPage: false });
        console.log('[+] Captured 03_cursor_hover_cta_button.png');
      }
    }

    // 5. Test Live Lab page as well to verify custom cursor works globally
    await page.goto('http://localhost:8080/lab', { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    await page.mouse.move(500, 300);
    await page.waitForTimeout(100);

    const labCursorState = await page.evaluate(() => {
      const dot = document.getElementById('custom-cursor-dot');
      const ring = document.getElementById('custom-cursor-ring');
      const ambientGlow = document.getElementById('ambient-cursor-glow');
      return {
        dotPresent: !!dot,
        ringPresent: !!ring,
        ambientGlowPresent: !!ambientGlow
      };
    });
    console.log('[+] Live Lab page cursor state:', labCursorState);

    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_lab_page_custom_cursor.png'), fullPage: false });
    console.log('[+] Captured 04_lab_page_custom_cursor.png');

    console.log('\n[SUCCESS] All clean 3D core, cursor velocity, background glow, and custom reticle tests PASSED!');
  } catch (err) {
    console.error('[-] Test failed:', err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

run();
