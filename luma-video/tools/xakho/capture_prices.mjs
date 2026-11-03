// Chụp trang shop (2×) giống tools/screenad/capture.mjs, kèm toạ độ MỌI chữ giá "123.000đ" để mask.py che bằng nhãn cá.
//   node tools/xakho/capture_prices.mjs <out-dir> <name> <url> [--w 1440] [--map] [--hide "chữ trong popup"] [--noads] [--vh 1000] [--find "chữ" …]   (--map → <name>.map.json: hộp mọi khối chữ)
// Ra <name>.png + <name>.json { boxes: { "<chữ>": [x,y,w,h] }, prices: [{ text, box }] } (px ảnh).
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

const [outDir, name, url, ...rest] = process.argv.slice(2);
const opt = (k, d) => (rest.includes(k) ? rest[rest.indexOf(k) + 1] : d);
const finds = (() => { const i = rest.indexOf('--find'); if (i < 0) return []; const o = []; for (let k = i + 1; k < rest.length && !rest[k].startsWith('--'); k++) o.push(rest[k]); return o; })();
const W = Number(opt('--w', 1440)), DSF = 2, VH = Number(opt('--vh', 1000));   // --vh: khung nhìn cao để chụp trọn trang cuộn trong khung riêng (docs) / nội dung hiện dần
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const UA = rest.includes('--ua') ? 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' : undefined;   // --ua: trang chặn trình duyệt chạy ngầm (bearblog trả "Not found")
const page = await browser.newPage({ viewport: { width: W, height: VH }, deviceScaleFactor: DSF, locale: 'vi-VN', userAgent: UA });
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60_000 });
await page.waitForLoadState('load', { timeout: 15_000 }).catch(() => {});
await page.waitForTimeout(3500);
await page.keyboard.press('Escape').catch(() => {});
// --noads: ẩn quảng cáo (iframe, ins, khung position fixed/sticky) để không che bài khi chụp cả trang; chạy lại sau khi cuộn vì quảng cáo tải lười
const noAds = () => rest.includes('--noads') && page.evaluate(() => {
  for (const e of document.querySelectorAll('iframe, ins')) e.style.setProperty('display', 'none', 'important');
  for (const e of document.querySelectorAll('body *')) if (['fixed', 'sticky'].includes(getComputedStyle(e).position)) e.style.setProperty('display', 'none', 'important');
});
await noAds();
await page.evaluate(async () => {
  for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 120)); }
  window.scrollTo(0, 0);
});
await page.waitForTimeout(1200);
await noAds();
// --hide "chữ": ẩn popup/toast nổi (phần tử fixed/sticky gần nhất chứa chữ đó) để không đè lên nội dung khi chụp cả trang
const hides = (() => { const i = rest.indexOf('--hide'); return i < 0 ? [] : [rest[i + 1]]; })();
for (const h of hides) await page.evaluate((h) => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode());) if (n.textContent.includes(h)) {
    let e = n.parentElement; while (e && e !== document.body && !['fixed', 'sticky'].includes(getComputedStyle(e).position)) e = e.parentElement;
    if (e && e !== document.body) e.style.display = 'none';
  }
}, h);
const MAP = rest.includes('--map');
const data = await page.evaluate(([finds, MAP]) => {
  const rect = (r) => [r.left + scrollX, r.top + scrollY, r.width, r.height];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const prices = [], boxes = {};
  for (let n; (n = walker.nextNode());) {
    const t = n.textContent;
    for (const m of t.matchAll(/(Từ\s*)?₫\s?\d{1,3}(\.\d{3})+|(Từ\s*)?\d{1,3}(\.\d{3})+\s*(đ|₫|VND)|\$\d+(\.\d+)?/g)) {
      const r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
      const b = r.getBoundingClientRect(); if (b.width > 0) prices.push({ text: m[0].trim(), box: rect(b) });
    }
    for (const f of finds) {
      const i = t.indexOf(f); if (i < 0) continue;
      const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + f.length);
      const b = r.getBoundingClientRect(); if (!b.width) continue;
      let k = f, j = 2; while (boxes[k]) k = `${f}#${j++}`; boxes[k] = rect(b);
    }
  }
  const map = [];   // --map: mọi khối chữ (tiêu đề, đoạn, mục, code, ô bảng) kèm hộp để chọn khung khoanh sau
  if (MAP) for (const e of document.querySelectorAll('h1,h2,h3,h4,p,li,pre,td,th,summary,button,a[role=button]')) {
    const r = e.getBoundingClientRect(), tx = e.innerText?.trim().replace(/\s+/g, ' ');
    if (r.width > 0 && r.height > 0 && tx) map.push({ tag: e.tagName.toLowerCase(), text: tx.slice(0, 110), box: rect(r) });
  }
  return { prices, boxes, map, title: document.title, size: [document.documentElement.scrollWidth, document.documentElement.scrollHeight] };
}, [finds, MAP]);
const S = (a) => a.map((v) => v * DSF);
data.prices.forEach((p) => (p.box = S(p.box)));
for (const k of Object.keys(data.boxes)) data.boxes[k] = S(data.boxes[k]);
if (MAP) { fs.writeFileSync(path.join(outDir, `${name}.map.json`), JSON.stringify(data.map.map((m) => ({ ...m, box: S(m.box).map(Math.round) })), null, 0)); }
delete data.map;
await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: true });
fs.writeFileSync(path.join(outDir, `${name}.json`), JSON.stringify({ url, capturedAt: new Date().toISOString(), ...data }, null, 1));
console.log(`✅ ${name}: ${data.prices.length} chữ giá, ${Object.keys(data.boxes).length} hộp`);
await browser.close();
