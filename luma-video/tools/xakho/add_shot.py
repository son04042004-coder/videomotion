"""Lưu ảnh chụp Chrome (claude-in-chrome) vào thư mục nguồn + toạ độ hộp để render.py dùng "box:<tên>".
  python tools/xakho/add_shot.py <tên> <ảnh.jpg> [tên_hộp=x,y,w,h …] [p:<chữ giá>=x,y,w,h …] [--url <url>] [--dir <thư mục ảnh nguồn trong public/videos>]
  p:522.500đ=… → thêm vào "prices" để render.py che bằng nhãn cá (hộp price{i} theo thứ tự)
Ra public/videos/2026-10-29-xakho-shots/<tên>.png + <tên>.json (ghi đè json thì giữ bản cũ trong .backup)."""
import json, os, shutil, sys, time
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name, src, *rest = sys.argv[1:]
OUT = os.path.join(ROOT, 'public', 'videos', rest[rest.index('--dir') + 1] if '--dir' in rest else '2026-10-29-xakho-shots')
url = rest[rest.index('--url') + 1] if '--url' in rest else ''
pairs = [a.split('=', 1) for a in rest if '=' in a and not a.startswith('--')]
boxes = {k: [float(v) for v in val.split(',')] for k, val in pairs if not k.startswith('p:')}
prices = [{'text': k[2:], 'box': [float(v) for v in val.split(',')]} for k, val in pairs if k.startswith('p:')]
os.makedirs(OUT, exist_ok=True)
png, js = os.path.join(OUT, name + '.png'), os.path.join(OUT, name + '.json')
for p in (png, js):
    if os.path.exists(p):
        bk = os.path.join(ROOT, '.backup', 'xa-kho-20261029', 'shots'); os.makedirs(bk, exist_ok=True)
        shutil.copy2(p, os.path.join(bk, f'{int(time.time())}-{os.path.basename(p)}'))
Image.open(src).convert('RGB').save(png)
json.dump({'url': url, 'source': src, 'capturedAt': time.strftime('%Y-%m-%dT%H:%M:%S'), 'boxes': boxes, 'prices': prices}, open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅', name, Image.open(png).size, list(boxes))
