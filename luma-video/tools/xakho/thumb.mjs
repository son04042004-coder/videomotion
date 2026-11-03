// Thumbnail TikTok cho video xả kho: node tools/xakho/thumb.mjs <id> '<json dữ liệu>'
// Lấy khung hình thật từ final.mp4 (giây `t`), ra thumbnail.jpg + thumbnail-grid.jpg (xem trước lưới 3:4, 360px).
import { chromium } from 'playwright-core';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const [id, json] = process.argv.slice(2);
const d = JSON.parse(json);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const V = path.join(ROOT, 'public', 'videos', id);
const frame = path.join(V, 'ad', 'thumb-frame.jpg');
// khung trình duyệt (y 392–1392) của video thật làm ảnh minh hoạ
execFileSync('ffmpeg', ['-y', '-v', 'error', '-ss', String(d.t), '-i', path.join(V, 'final.mp4'), '-frames:v', '1',
  '-vf', 'crop=1080:1000:0:392', '-q:v', '2', frame]);
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto(pathToFileURL(path.join(ROOT, 'tools', 'xakho', d.html || 'thumb.html')).href);   // thumb.html (kênh 1) | thumb-k2.html (kênh 2)
await page.evaluate((x) => window.setup(x), { ...d, img: pathToFileURL(frame).href });
const out = path.join(V, 'thumbnail.jpg');
await page.screenshot({ path: out, type: 'jpeg', quality: 92 });
await browser.close();
execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', out, '-vf', 'crop=1080:1440:0:240,scale=360:480', path.join(V, 'thumbnail-grid.jpg')]);
console.log('✅', out);
