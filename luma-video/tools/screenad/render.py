"""Dựng video quảng cáo dạng "quay màn hình" từ ảnh chụp trang web: khung Chrome tối + chuột Windows trượt/bấm
+ camera zoom theo chuột + khung vàng nhấn giá + phụ đề chạy + giọng (voice.py) + nhạc nền & tiếng click.

  <venv-tts>/python tools/screenad/render.py <id>
Đọc public/videos/<id>/shots.json, voice.mp3, words.json. Ra final.mp4 (1080×1920 30fps), thumbnail.jpg, ad/ (ass, stems).

shots.json: { "shots": [ {
   "img": "<png toàn trang, đường dẫn từ thư mục video>",  (cạnh nó là <png>.json của capture.mjs: boxes theo px ảnh)
   "url": "apihub247.com", "tab": "ApiHub247", "tabs": ["Google One", "Gemini"],  (tab phụ cho giống thật)
   "start": 0.0, "end": 6.2, "type_url": true,
   "cam":    [[t, x, y, w], …]          t giây tuyệt đối; x,y tâm khung nhìn (px ảnh) hoặc "box:<chữ>"; w = bề rộng khung nhìn (px ảnh)
   "cursor": [[t, x, y, "click"?], …]   toạ độ px ảnh hoặc "box:<chữ>" (tâm hộp)
   "marks":  [[t0, t1, "box:<chữ>", pad?], …]   khung vàng nhấn mạnh
} ] }
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'lux'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'ads'))
import synth_audio as SA  # noqa: E402
import make_ad as MA       # noqa: E402  (phụ đề ASS dùng chung với video quảng cáo)

Image.MAX_IMAGE_PIXELS = None
W, H, FPS = 1080, 1920, 30
TOP = 250                 # nền khói phía trên (giống video mẫu)
TAB_H, BAR_H = 64, 78     # thanh tab + thanh địa chỉ Chrome
PAGE_Y = TOP + TAB_H + BAR_H
PAGE_H = H - PAGE_Y
ASPECT = W / PAGE_H
HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda s, b=False: ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf', s)
CUR = json.load(open(os.path.join(HERE, 'assets', 'cursors.json')))
CUR_SCALE = 0.58
SFX = os.path.dirname(ROOT) + '/sfx-library/'
CLICK_SFX = SFX + 'mixkit/click/2577-interface-device-click.wav'
TAIL = 0.8


def ease(x):
    x = min(1, max(0, x))
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def interp(keys, t):
    """keys: [(t, v…)] → giá trị nội suy easing theo t."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            k = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(va + (vb - va) * k for va, vb in zip(a[1:], b[1:]))
    return keys[-1][1:]


def smoke():
    rng = np.random.default_rng(7)
    base = np.zeros((TOP + 400, W))
    for s, amp in ((420, 1.0), (180, .45), (80, .18)):
        n = Image.fromarray((rng.random((max(2, (TOP + 400) // s * 4), max(2, W // s * 4))) * 255).astype('uint8'))
        base += np.asarray(n.resize((W, TOP + 400), Image.BICUBIC).filter(ImageFilter.GaussianBlur(s / 3)), float) * amp
    base = (base - base.min()) / (base.max() - base.min())
    v = (55 + 135 * np.abs(np.sin(base * 4.5)) ** 0.8).astype('uint8')   # vân khói mềm như đá cẩm thạch
    return Image.fromarray(v).convert('RGB').filter(ImageFilter.GaussianBlur(5))


def chrome_bar(tab, tabs, url_text, caret):
    im = Image.new('RGB', (W, TAB_H + BAR_H), (32, 33, 36))
    d = ImageDraw.Draw(im)
    x = 18
    for i, t in enumerate([tab] + list(tabs)):
        w = 330 if i == 0 else 250
        if i == 0:
            d.rounded_rectangle((x, 10, x + w, TAB_H + 12), 14, fill=(53, 54, 58))
        else:
            d.line((x + w, 22, x + w, TAB_H - 10), fill=(80, 80, 85), width=2)
        d.ellipse((x + 18, 26, x + 40, 48), fill=(138, 180, 248) if i == 0 else (120, 120, 125))
        d.text((x + 52, 22), (t[:22] + '…') if len(t) > 23 else t, font=F(24), fill=(232, 234, 237) if i == 0 else (170, 172, 176))
        d.text((x + w - 34, 20), '×', font=F(26), fill=(170, 172, 176))
        x += w + 6
    y0 = TAB_H
    d.rectangle((0, y0, W, y0 + BAR_H), fill=(53, 54, 58))
    for k, g in enumerate(('←', '→')):
        d.text((22 + k * 56, y0 + 16), g, font=F(34), fill=(200, 202, 206))
    cy = y0 + BAR_H // 2                                                 # nút tải lại: cung tròn + mũi tên
    d.arc((136, cy - 15, 166, cy + 15), 40, 330, fill=(200, 202, 206), width=4)
    d.polygon([(160, cy - 20), (172, cy - 12), (158, cy - 6)], fill=(200, 202, 206))
    d.rounded_rectangle((190, y0 + 12, W - 70, y0 + BAR_H - 12), 27, fill=(32, 33, 36))
    d.rounded_rectangle((218, cy - 4, 240, cy + 13), 3, fill=(170, 172, 176))   # ổ khoá
    d.arc((221, cy - 16, 237, cy + 2), 180, 360, fill=(170, 172, 176), width=3)
    d.text((258, y0 + 19), url_text, font=F(29), fill=(232, 234, 237))
    if caret:
        cx = 258 + d.textlength(url_text, font=F(29)) + 3
        d.line((cx, y0 + 22, cx, y0 + BAR_H - 22), fill=(232, 234, 237), width=2)
    d.ellipse((W - 54, y0 + 22, W - 22, y0 + 54), fill=(95, 99, 104))   # avatar trung tính (không lộ tài khoản)
    return im


def load_cursors():
    out = {}
    for k in ('arrow', 'hand'):
        im = Image.open(os.path.join(HERE, 'assets', f'cursor-{k}.png'))
        s = CUR_SCALE
        out[k] = (im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS), [v * s for v in CUR[k]['hotspot']])
    return out


def resolve(shot, meta, v):
    if isinstance(v, str) and v.startswith('box:'):
        x, y, w, h = meta['boxes'][v[4:]]
        return x + w / 2, y + h / 2
    return v


def prep(vid, V):
    sh = json.load(open(os.path.join(V, 'shots.json'), encoding='utf-8'))['shots']
    for s in sh:
        p = os.path.normpath(os.path.join(V, s['img']))
        s['_im'] = Image.open(p).convert('RGB')
        s['_meta'] = json.load(open(p[:-4] + '.json', encoding='utf-8')) if os.path.exists(p[:-4] + '.json') else {'boxes': {}}
        s['_cam'] = []
        for k in s['cam']:
            x, y = (resolve(s, s['_meta'], k[1]) if isinstance(k[1], str) else (k[1], k[2]))
            w = k[-1]
            s['_cam'].append((k[0], x, y, w))
        s['_cur'] = []
        for k in s.get('cursor', []):
            if isinstance(k[1], str):
                x, y = resolve(s, s['_meta'], k[1]); rest = k[2:]
            else:
                x, y = k[1], k[2]; rest = k[3:]
            s['_cur'].append((k[0], x, y, 'click' in rest))
        s['_marks'] = []
        for m in s.get('marks', []):
            bx, by, bw, bh = m[2] if isinstance(m[2], list) else s['_meta']['boxes'][m[2][4:]]
            pad = m[3] if len(m) > 3 else 18
            s['_marks'].append((m[0], m[1], bx - pad, by - pad, bw + 2 * pad, bh + 2 * pad))
    return sh


def view(s, t):
    cx, cy, w = interp(s['_cam'], t)
    im = s['_im']
    w = min(w, im.width); h = w / ASPECT
    if h > im.height:
        h = im.height; w = h * ASPECT
    x0 = min(max(0, cx - w / 2), im.width - w); y0 = min(max(0, cy - h / 2), im.height - h)
    return x0, y0, w, h


MARK_STYLE = os.environ.get('MARK_STYLE', 'circle')


def draw_mark(out, d, style, box, dt, left):
    """Khoanh thông tin: 'circle' = vòng bút đỏ vẽ tay tự vẽ ra; 'marker' = bút dạ vàng quét dưới chữ;
    'spotlight' = làm tối phần còn lại, viền trắng quanh chỗ cần xem."""
    X0, Y0, X1, Y1 = box
    fade = 1 - ease((0.22 - left) / 0.22) if left < 0.22 else 1.0
    if style == 'circle':
        cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
        rx, ry = (X1 - X0) / 2 + 26, (Y1 - Y0) / 2 + 22
        p = ease(dt / 0.38)
        n = int(90 * 1.12 * p)
        pts = []
        for i in range(n + 1):
            a = -2.3 + i / 90 * 2 * math.pi
            k = 1 + 0.035 * math.sin(i * 0.21) + 0.05 * i / 100      # nét tay hơi lệch, vòng sau rộng hơn
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        if len(pts) > 1:
            col = (255, 45, 45, int(255 * fade))
            d.line([(x + 3, y + 4) for x, y in pts], fill=(0, 0, 0, int(70 * fade)), width=10, joint='curve')
            d.line(pts, fill=col, width=9, joint='curve')
            for x, y in (pts[0], pts[-1]):
                d.ellipse((x - 4.5, y - 4.5, x + 4.5, y + 4.5), fill=col)
    elif style == 'marker':
        p = ease(dt / 0.32)
        x1 = X0 - 8 + (X1 - X0 + 16) * p
        if x1 > X0:
            reg = (int(X0 - 8), int(Y0 + (Y1 - Y0) * 0.12), int(x1), int(Y1 - (Y1 - Y0) * 0.02))
            crop = out.crop(reg)
            ylw = Image.new('RGB', crop.size, (255, 236, 60))
            mix = ImageChops.multiply(crop, ylw)
            out.paste(Image.blend(crop, mix, 0.9 * fade), reg[:2])
    else:  # spotlight
        a = ease(dt / 0.3) * fade
        pad = 18
        shade = Image.new('L', (W, PAGE_H), int(120 * a))
        ImageDraw.Draw(shade).rounded_rectangle((X0 - pad, Y0 - pad - PAGE_Y, X1 + pad, Y1 + pad - PAGE_Y), 18, fill=0)
        black = Image.new('RGB', (W, PAGE_H), (0, 0, 0))
        page = out.crop((0, PAGE_Y, W, H))
        out.paste(Image.composite(black, page, shade), (0, PAGE_Y))
        d.rounded_rectangle((X0 - pad, Y0 - pad, X1 + pad, Y1 + pad), 18, outline=(255, 255, 255, int(255 * a)), width=5)


def frame(s, t, cursors, bg):
    out = Image.new('RGB', (W, H))
    off = int((t * 18) % 400)                                            # khói trôi chậm
    out.paste(bg.crop((0, off, W, off + TOP)), (0, 0))
    url = s['url']
    if s.get('type_url') and t - s['start'] < 0.9:
        n = int(len(url) * ease((t - s['start']) / 0.8)); url_txt, caret = url[:n], True
    else:
        url_txt, caret = url, False
    out.paste(chrome_bar(s.get('tab', url), s.get('tabs', []), url_txt, caret), (0, TOP))
    x0, y0, w, h = view(s, t)
    out.paste(s['_im'].crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, PAGE_H), Image.BILINEAR), (0, PAGE_Y))
    sc = W / w
    to_scr = lambda x, y: ((x - x0) * sc, (y - y0) * sc + PAGE_Y)
    d = ImageDraw.Draw(out, 'RGBA')
    for t0, t1, bx, by, bw, bh in s['_marks']:
        if t0 <= t < t1:
            X0, Y0 = to_scr(bx, by); X1, Y1 = to_scr(bx + bw, by + bh)
            draw_mark(out, d, MARK_STYLE, (X0, Y0, X1, Y1), t - t0, t1 - t)
    if s['_cur'] and t >= s['_cur'][0][0] - 0.01:
        cx, cy = interp([(k[0], k[1], k[2]) for k in s['_cur']], t)
        clicks = [k[0] for k in s['_cur'] if k[3]]
        near = [c for c in clicks if -0.55 <= t - c <= 0.35]
        kind = 'hand' if near else 'arrow'
        X, Y = to_scr(cx, cy)
        for c in clicks:                                                 # vòng gợn sóng khi bấm
            dt = t - c
            if 0 <= dt < 0.45:
                r = 18 + 70 * ease(dt / 0.45)
                d.ellipse((X - r, Y - r, X + r, Y + r), outline=(30, 134, 246, int(220 * (1 - dt / 0.45))), width=6)
        im, hs = cursors[kind]
        press = any(0 <= t - c < 0.12 for c in clicks)
        if press:
            im = im.resize((int(im.width * .88), int(im.height * .88)))
        out.paste(im, (int(X - hs[0]), int(Y - hs[1])), im)
    return out


def render(vid):
    V = os.path.join(ROOT, 'public', 'videos', vid)
    A = os.path.join(V, 'ad'); os.makedirs(A, exist_ok=True)
    shots = prep(vid, V)
    voice = os.path.join(V, 'voice.mp3')
    vd = MA.duration(voice)
    D = round(vd + MA.VOICE_DELAY + TAIL, 3)
    shots[-1]['end'] = D
    words = json.load(open(os.path.join(V, 'words.json'), encoding='utf-8'))['words']
    # phụ đề (không tiêu đề: video mẫu chỉ có cảnh quay + giọng)
    MA.SUB_Y = 1700
    ass = os.path.join(A, 'subs.ass')
    MA.write_ass(ass, [' '], words, D)
    txt = open(ass, encoding='utf-8-sig').read()
    txt = '\n'.join(l for l in txt.split('\n') if not l.startswith('Dialogue: 0') and not l.startswith('Dialogue: 1'))
    open(ass, 'w', encoding='utf-8-sig').write(txt)
    # âm thanh: giọng + tiếng click (chồng iu 25/10: bỏ nhạc nền)
    clicks = [k[0] for s in shots for k in s['_cur'] if k[3]]
    a_in = ['-i', voice] + sum([['-i', CLICK_SFX] for _ in clicks], [])
    fx = '[0:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-15:TP=-2:LRA=11,adelay=150|150,apad[v];'
    for k, c in enumerate(clicks):
        ms = int(c * 1000); fx += f'[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume=-12dB,adelay={ms}|{ms}[c{k}];'
    fx += f'[v]{"".join(f"[c{k}]" for k in range(len(clicks)))}amix=inputs={1 + len(clicks)}:duration=first:normalize=0,' \
          f'atrim=0:{D},loudnorm=I=-14:TP=-1.5:LRA=11[o]'
    mix = os.path.join(A, 'mix.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *a_in, '-filter_complex', fx, '-map', '[o]', '-ar', '48000', '-ac', '2', mix], check=True)
    # hình
    cursors, bg = load_cursors(), smoke()
    out = os.path.join(V, 'final.mp4')
    fontsdir = os.path.relpath(MA.FONTS, A).replace('\\', '/')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', mix, '-filter_complex', f'[0:v]ass=subs.ass:fontsdir={fontsdir},format=yuv420p[v]',
                          '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                          '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(D), out], stdin=subprocess.PIPE, cwd=A)
    n = int(D * FPS); prev = None
    for i in range(n):
        t = i / FPS
        k = next((j for j, s in enumerate(shots) if s['start'] <= t < s['end']), len(shots) - 1)
        fr = frame(shots[k], t, cursors, bg)
        if k > 0 and t - shots[k]['start'] < 0.12:                      # nối cảnh mềm 0,12s
            a = (t - shots[k]['start']) / 0.12
            fr = Image.blend(frame(shots[k - 1], t, cursors, bg), fr, a)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '1.0', '-i', out, '-frames:v', '1', '-q:v', '2', os.path.join(V, 'thumbnail.jpg')], check=True)
    print(f'✅ {vid}: {D}s, {len(shots)} cảnh, {len(clicks)} lần bấm → {out}')


if __name__ == '__main__':
    render(sys.argv[1])
