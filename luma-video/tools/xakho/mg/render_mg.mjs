// Render motion graphic (anim.html) ra chuỗi PNG trong suốt 30fps để render.py ghép lên video.
//   node tools/xakho/mg/render_mg.mjs <jobs.json> <out-dir> [anim.html | anim-k2.html]   (file HTML theo kênh, xem tools/xakho/channels.json)
// jobs.json: [{ "id": "mg1", "type": "slam", "dur": 2.6, "data": {…} }, …] → <out-dir>/<id>/f0000.png …
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const [jobsFile, outDir, animFile = 'anim.html'] = process.argv.slice(2);
const jobs = JSON.parse(fs.readFileSync(jobsFile, 'utf8'));
const html = pathToFileURL(path.join(path.dirname(fileURLToPath(import.meta.url)), animFile)).href;
const FPS = 30;
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto(html);
for (const job of jobs) {
  const dir = path.join(outDir, job.id);
  fs.mkdirSync(dir, { recursive: true });              // render lại thì ghi đè; meta.json giữ đúng số khung
  await page.evaluate((cfg) => window.setup(cfg), job);
  const n = Math.round(job.dur * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate((t) => window.seek(t), i / FPS);
    await page.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`), omitBackground: true });
  }
  fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify({ frames: n, fps: FPS, type: job.type }));
  console.log(`✅ ${job.id} (${job.type}) ${n} khung`);
}
await browser.close();
