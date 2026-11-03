"""Thumbnail kiểu C từ khung hình thật (cảnh không có motion graphic).
  python tools/xakho/thumbs.py <id video đầy đủ hoặc mã ngắn của đợt 29/10> …
Nội dung lấy từ edl.json "thumb": {"img": "<ảnh nguồn>", "variant": "v1|v2", "tag", "l1" (có thể <br>), "num", "unit", "sub"}."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = {
 'gem-a': ('gem-a-write-result', dict(variant='v1', tag='XẢ KHO', l1='GEMINI PRO<br>18 THÁNG', num='69', unit='CÁ', sub='nâng mail chính chủ')),
 'gem-b': ('gem-b-img-result', dict(variant='v2', tag='THẬT KHÔNG?', l1='GEMINI PRO<br>TẬN 18 THÁNG', num='69', unit='CÁ', sub='vẽ ảnh · làm video · 5TB')),
 'gpt-a': ('gpt-a-img-full', dict(variant='v1', tag='XẢ KHO', l1='CHATGPT PLUS<br>1 THÁNG', num='190', unit='CÁ', sub='tài khoản riêng')),
 'gpt-b': ('gpt-b-prod-edit', dict(variant='v2', tag='VIỆC NGẬP ĐẦU?', l1='TRỢ LÝ<br>CHATGPT PLUS', num='190', unit='CÁ', sub='email · tạo ảnh · viết bài')),
 'claude-a': ('claude-code-page', dict(variant='v1', tag='DÂN CODE ƠI!', l1='CLAUDE<br>MAX X5', num='1850', unit='CÁ', sub='Claude Code cả ngày')),
 'claude-b': ('claude-b-artifact', dict(variant='v2', tag='HẾT LƯỢT HOÀI?', l1='LÊN CLAUDE<br>MAX X5', num='1850', unit='CÁ', sub='5× hạn mức Pro')),
}
for k in sys.argv[1:] or T:
    vid = k if k[:4].isdigit() else f'2026-10-29-xakho-{k}'
    V = os.path.join(ROOT, 'public', 'videos', vid)
    m = json.load(open(os.path.join(V, 'render-manifest.json'), encoding='utf-8'))
    th = json.load(open(os.path.join(V, 'edl.json'), encoding='utf-8')).get('thumb')
    img, d = (th['img'], {x: y for x, y in th.items() if x != 'img'}) if th else T[vid.replace('2026-10-29-xakho-', '')]
    ch = json.load(open(os.path.join(V, 'edl.json'), encoding='utf-8')).get('channel', 'k1')
    d['html'] = json.load(open(os.path.join(ROOT, 'tools', 'xakho', 'channels.json'), encoding='utf-8'))[ch]['thumb']
    shots = [s for s in m['shots'] if s['img'] == img and s['line'] == d.get('line', s['line'])]   # "line": chọn đúng cảnh của câu đó
    busy = [(g['t0'] - 0.1, g['t0'] + g['dur'] + 0.1) for g in m['mgs']]
    cands = [s['start'] + f * (s['end'] - s['start']) for s in shots for f in (0.6, 0.4, 0.8, 0.2)]
    t = next((round(x, 2) for x in cands if not any(a <= x <= b for a, b in busy)), None)
    assert t is not None, f'{k}: mọi khung của {img} đều bị motion graphic che'
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'xakho', 'thumb.mjs'), vid, json.dumps({**{x: y for x, y in d.items() if x != 'line'}, 't': t}, ensure_ascii=False)], check=True)
