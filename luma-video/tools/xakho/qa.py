"""Kiểm tra 6 video xả kho trước khi giao: ffprobe, loudness, chữ tiền trong phụ đề/caption, trùng cảnh A/B, contact sheet.
  python tools/xakho/qa.py [id …]   → public/videos/<id>/qa/sheet.jpg + in bảng kết quả + <id đầu>-qa.json
id: đầy đủ (2026-11-02-vm-gemini-a) hoặc mã ngắn đợt 29/10 (gem-a). Cặp A/B nhóm theo edl.json "product" (mặc định bỏ hậu tố -a/-b)."""
import json, os, re, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VID = os.path.join(ROOT, 'public', 'videos')
IDS = sys.argv[1:] or ['gem-a', 'gem-b', 'gpt-a', 'gpt-b', 'claude-a', 'claude-b']
BAD = re.compile(r'\b(tiền|giá|đồng(?! ý)|đô|usd|mua|bán|thanh toán|chuyển khoản|vnd)\b|\d+k\b|\d+\.000', re.I)


def probe(f):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', f], capture_output=True, text=True).stdout)
    v = next(s for s in j['streams'] if s['codec_type'] == 'video')
    a = [s for s in j['streams'] if s['codec_type'] == 'audio']
    return dict(w=v['width'], h=v['height'], fps=v['r_frame_rate'], dur=round(float(j['format']['duration']), 2), audio=bool(a))


def loud(f):
    err = subprocess.run(['ffmpeg', '-v', 'info', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', err); p = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', err)
    return float(i[-1]) if i else None, float(p[-1]) if p else None


def sheet(V, m):
    ts = sorted({round(t, 2) for t in [0.5] + [s['start'] + 0.7 for s in m['shots'][1:]] + [g['t0'] + min(1.4, g['dur'] - 0.3) for g in m['mgs']] + [m['duration'] - 0.4]})
    os.makedirs(os.path.join(V, 'qa'), exist_ok=True)
    tmp = os.path.join(V, 'qa', '_f.png'); ims = []
    for t in ts:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', os.path.join(V, 'final.mp4'), '-frames:v', '1', '-vf', 'scale=216:384', tmp], check=True)
        ims.append(Image.open(tmp).copy())
    cols = 10; s = Image.new('RGB', (cols * 216, ((len(ims) + cols - 1) // cols) * 384))
    for i, im in enumerate(ims):
        s.paste(im, ((i % cols) * 216, (i // cols) * 384))
    s.save(os.path.join(V, 'qa', 'sheet.jpg'), quality=85)


res = {}
for k in IDS:
    V = os.path.join(VID, k if k[:4].isdigit() else f'2026-10-29-xakho-{k}')
    m = json.load(open(os.path.join(V, 'render-manifest.json'), encoding='utf-8'))
    words = ' '.join(w['text'] for w in json.load(open(os.path.join(V, 'words.json'), encoding='utf-8'))['words'])
    cap = open(os.path.join(V, 'caption.txt'), encoding='utf-8').read()
    r = probe(os.path.join(V, 'final.mp4'))
    r['lufs'], r['peak'] = loud(os.path.join(V, 'final.mp4'))
    r['money_words'] = BAD.findall(words) + BAD.findall(cap)
    r['imgs'] = sorted({s['img'] for s in m['shots']})
    r['thumb'] = os.path.exists(os.path.join(V, 'thumbnail.jpg'))
    sheet(V, m)
    res[k] = r
groups = {}
for k in res:
    V = os.path.join(VID, k if k[:4].isdigit() else f'2026-10-29-xakho-{k}')
    prod = json.load(open(os.path.join(V, 'edl.json'), encoding='utf-8')).get('product') or re.sub(r'-[ab]$', '', k)
    groups.setdefault(prod, []).append(k)
for ks in groups.values():                                   # mỗi video trong cùng sản phẩm không được chung ảnh nguồn
    for i, a in enumerate(ks):
        res[a]['shared_with_b'] = sorted({x for b in ks if b != a for x in set(res[a]['imgs']) & set(res[b]['imgs'])})
for k, r in res.items():
    ok = r['w'] == 1080 and r['h'] == 1920 and r['fps'] == '30/1' and r['audio'] and not r['money_words'] and not r.get('shared_with_b')
    print(f"{'✅' if ok else '❌'} {k}: {r['w']}x{r['h']} {r['fps']} {r['dur']}s audio={r['audio']} {r['lufs']}LUFS peak {r['peak']} "
          f"tiền={r['money_words']} thumb={r['thumb']} chung-ảnh-A/B={r.get('shared_with_b', '-')}")
json.dump(res, open(os.path.join(VID, (IDS[0] if IDS[0][:4].isdigit() else '2026-10-29-xakho') + '-qa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
