import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function buildPdf() {
  const htmlPath = path.resolve('_academic_offline', 'academic_pages', 'paper.html');
  const destPdf = path.resolve('_academic_submissions', 'ieee_paper', 'ChameleonShell_IEEE_Conference_Paper.pdf');

  if (!fs.existsSync(htmlPath)) {
    console.error('Source HTML not found:', htmlPath);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Load the paper HTML directly via file URL
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Render to IEEE Conference Paper PDF (Letter size, two-column feel)
  await page.pdf({
    path: destPdf,
    format: 'Letter',
    printBackground: true,
    margin: {
      top: '0.6in',
      bottom: '0.6in',
      left: '0.6in',
      right: '0.6in'
    }
  });

  console.log(`[+] Successfully generated IEEE Conference Paper PDF: ${destPdf}`);
  await browser.close();
}

buildPdf().catch(err => {
  console.error('PDF generation failed:', err);
  process.exit(1);
});
