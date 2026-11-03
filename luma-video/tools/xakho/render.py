"""Dựng video xả kho (29/10): khung quay màn hình kiểu lượt 25/10 (tools/screenad/render.py) + motion graphic kiểu C
+ khung trình duyệt cao 1000px để phụ đề nằm trong vùng an toàn TikTok + che giá bằng nhãn cá + làm mờ thông tin riêng.

  <venv-tts>/python tools/xakho/render.py <id>          → public/videos/<id>/final.mp4
  <venv-tts>/python tools/xakho/render.py <id> --mg     → render lại motion graphic trước khi dựng

public/videos/<id>/edl.json:
  "shots": [{ "line": i, "frac": 0.0, "img": "<tên ảnh trong 2026-10-29-xakho-shots>", "url", "tab", "tabs",
              "cam": [[dt, "box:<k>" | x, y, w], …], "cursor": [[dt, "box:<k>" | x, y, "click"?], …],
              "marks": [[dt0, dt1, "box:<k>"], …], "prices": {chỉ_số: "69 CÁ"} }]   dt tính từ đầu cảnh
  "mgs":   [{ "id", "type", "line": i, "word": "<chữ neo>", "offset": -0.1, "dur": 2.6 | "end" | "until": n, "data": {…}, "sfx": [["impact", 0.2]] }]
"""
import json, math, os, re, subprocess, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'xakho'))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('screenad_render', os.path.join(ROOT, 'tools', 'screenad', 'render.py'))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)   # khung Chrome, chuột, vòng bút đỏ của lượt 25/10
from mask import FONT as MASK_FONT, mask_prices  # noqa: E402

W, H, FPS = R.W, R.H, R.FPS
PAGE_H = 1000                         # trình duyệt y 392–1392; dưới là khói + phụ đề (vùng an toàn TikTok)
R.PAGE_H, R.ASPECT = PAGE_H, W / PAGE_H
SHOTS = os.path.join(ROOT, 'public', 'videos', '2026-10-29-xakho-shots')
CHANNELS = json.load(open(os.path.join(ROOT, 'tools', 'xakho', 'channels.json'), encoding='utf-8'))   # kênh: bộ MG / màu phụ đề / nền
SFXD = os.path.dirname(ROOT) + '/sfx-library/mixkit/'
SFX = {'impact': 'impact/2909-cool-impact-movie-trailer.wav', 'whoosh': 'transition/1490-fast-whoosh-transition.wav',
       'pop': 'pop/2364-hard-pop-click.wav', 'swipe': 'swipe/2627-fast-swipe-zoom.wav', 'ding': 'pop/2870-correct-answer-tone.wav',
       'sweep': 'transition/175-short-transition-sweep.wav'}
SFX_DB = {'impact': -8, 'whoosh': -14, 'pop': -12, 'swipe': -14, 'ding': -12, 'sweep': -16}


def load_img(name, prices, relabel=None):
    """Ảnh nguồn đã che giá (nhãn cá), đổi nhãn chữ (relabel: {hộp: chữ mới}) và làm mờ các hộp blur*."""
    im = Image.open(os.path.join(SHOTS, name + '.png')).convert('RGB')
    meta = json.load(open(os.path.join(SHOTS, name + '.json'), encoding='utf-8'))
    if meta.get('prices'):
        if prices != 'giu':   # "prices": "giu" → để nguyên giá thật trên trang, không đè nhãn cá (luật TikTok 02/11)
            im = mask_prices(im, meta, {int(k): v for k, v in (prices or {}).items()})
        for i, pr in enumerate(meta['prices']):
            meta['boxes'][f'price{i}'] = pr['box']
    for key, text in (relabel or {}).items():
        x, y, w, h = meta['boxes'][key]
        d = ImageDraw.Draw(im)
        d.rectangle((x - 3, y - 3, x + w + 30, y + h + 3), fill=im.getpixel((int(x) - 6, int(y + h / 2))))
        d.text((x, y + h / 2), text, font=ImageFont.truetype(MASK_FONT, int(h * 0.8)), fill=(30, 30, 40), anchor='lm')
    for k, (x, y, w, h) in meta.get('boxes', {}).items():
        if k.startswith('blur'):
            box = tuple(int(v) for v in (x, y, x + w, y + h))
            im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
    return im, meta


def line_starts(script, words):
    starts, i = [], 0
    for line in script['lines']:
        starts.append(words[i]['startMs'] / 1000 if i < len(words) else words[-1]['endMs'] / 1000)
        i += len(re.sub(r'\[[^\]]+\]', ' ', line).split())
    return starts


def word_time(script, words, line, word):
    """Thời điểm bắt đầu chữ `word` (lần đầu) trong câu `line`."""
    i = sum(len(re.sub(r'\[[^\]]+\]', ' ', l).split()) for l in script['lines'][:line])
    n = len(re.sub(r'\[[^\]]+\]', ' ', script['lines'][line]).split())
    for w in words[i:i + n]:
        if word.lower() in w['text'].lower():
            return w['startMs'] / 1000
    raise KeyError(f'không thấy "{word}" trong câu {line}')


def prep(V, edl, script, words, D):
    starts = line_starts(script, words)
    lens = starts[1:] + [D]
    shots = []
    for s in edl['shots']:
        a = starts[s['line']] + s.get('frac', 0) * (lens[s['line']] - starts[s['line']])
        s = dict(s, start=0.0 if not shots else a + R.MA.VOICE_DELAY - 0.05)
        im, meta = load_img(s['img'], s.get('prices'), s.get('relabel'))
        s['_im'], s['_meta'] = im, meta
        res = lambda v: R.resolve(s, meta, v)
        s['_cam'] = [(s['start'] + k[0], *(res(k[1]) if isinstance(k[1], str) else (k[1], k[2])), k[-1]) for k in s['cam']]
        s['_cur'] = []
        for k in s.get('cursor', []):
            x, y = res(k[1]) if isinstance(k[1], str) else (k[1], k[2])
            s['_cur'].append((s['start'] + k[0], x, y, 'click' in k))
        s['_marks'] = []
        for m in s.get('marks', []):
            bx, by, bw, bh = meta['boxes'][m[2][4:]]
            s['_marks'].append((s['start'] + m[0], s['start'] + m[1], bx - 10, by - 8, bw + 20, bh + 16))
        if s.get('punch'):                                    # crash-zoom-punch: {"at": dt, "to": "box:k" | [cx, cy, w], "mode": "bounce" | "shake"}
            p = s['punch']; to = p['to']
            if isinstance(to, str):
                bx, by, bw, bh = meta['boxes'][to[4:]]; to = [bx + bw / 2, by + bh / 2, max(bw * 1.25, 420)]
            s['_punch'] = (s['start'] + p['at'], *to, p.get('mode', 'bounce'))
        s['_cuts'] = [(s['start'] + c[0], *(res(c[1]) if isinstance(c[1], str) else (c[1], c[2])), c[-1]) for c in s.get('cuts', [])]   # beat-cut: cắt cứng + chớp trắng
        shots.append(s)
    for a, b in zip(shots, shots[1:]):
        a['end'] = b['start']
    shots[-1]['end'] = D
    return shots


_view0 = R.view


def _clamp_view(s, cx, cy, w):
    im = s['_im']; w = min(w, im.width); h = w / R.ASPECT
    if h > im.height:
        h = im.height; w = h * R.ASPECT
    return min(max(0, cx - w / 2), im.width - w), min(max(0, cy - h / 2), im.height - h), w, h


def view(s, t):
    """Camera thêm 2 kiểu học từ video-shotcraft: cắt cứng theo nhịp (cuts) và zoom giật (punch). Cảnh không khai báo thì như cũ."""
    cuts = [c for c in s.get('_cuts', []) if c[0] <= t]
    if cuts:                                                  # paparazzi: giữ khung cắt cuối, phóng 1.03 rồi lắng về 1 trong 0,2s
        t0, cx, cy, w = cuts[-1]
        return _clamp_view(s, cx, cy, w / (1 + 0.03 * (1 - R.ease((t - t0) / 0.2))))
    p = s.get('_punch')
    if p and t >= p[0] - 0.25:
        T, tx, ty, tw, mode = p
        x0, y0, w0, h0 = _view0(s, T - 0.25)
        bx, by, bw = x0 + w0 / 2, y0 + h0 / 2, w0
        if t < T:                                             # lùi nhẹ 3,5% lấy đà
            return _clamp_view(s, bx, by, bw * (1 + 0.035 * math.sin(math.pi / 2 * (t - T + 0.25) / 0.25)))
        k = min(1, (t - T) / 0.2); e = k ** 3                   # 6 khung ease-in: cú giật
        cx, cy, w = bx + (tx - bx) * e, by + (ty - by) * e, bw * 1.035 + (tw - bw * 1.035) * e
        if k >= 1:
            d = t - T - 0.2
            if mode == 'bounce':                              # vượt 4,5% rồi bật về
                w = tw * (1 - 0.045 * math.exp(-d / 0.08) * math.cos(d * 22))
            elif d < 0.25:                                    # đập dừng + rung tắt dần
                amp = 14 * (w / R.W) * math.exp(-d / 0.06)
                cx += amp * math.sin(d * 140); cy += amp * 0.6 * math.cos(d * 110)
        return _clamp_view(s, cx, cy, w)
    return _view0(s, t)


R.view = view


def flash_alpha(s, t):
    """Chớp trắng: mỗi cú cắt cứng 0.95 → 0 trong 4 khung."""
    a = 0.0
    for c in s.get('_cuts', []):
        if 0 <= t - c[0] < 0.14:
            a = max(a, 0.95 * (1 - (t - c[0]) / 0.14) ** 2)
    return a


def mg_frames(V):
    out = {}
    base = os.path.join(V, 'mg')
    for m in os.listdir(base) if os.path.isdir(base) else []:
        meta = os.path.join(base, m, 'meta.json')
        if os.path.exists(meta):
            out[m] = json.load(open(meta))['frames']
    return out


def _hblur(im, dist):
    """Nhoè chuyển động ngang: trộn các bản dịch ngang (nhoè theo hướng)."""
    n = max(2, min(14, int(abs(dist) / 12)))
    acc = None
    for i in range(n):
        sh = ImageChops.offset(im, int(dist * (i / (n - 1) - 0.5)), 0)
        acc = sh if acc is None else Image.blend(acc, sh, 1 / (i + 1))
    return acc


def transition(kind, a, b, dt, bottom_y):
    """Chuyển cảnh học từ video-shotcraft (shot-transitions, tear-streak). dt = giây so với điểm cắt (âm = trước cắt).
    Chỉ vùng trình duyệt chuyển động, khói nền đứng yên."""
    top = R.TOP
    box = (0, top, W, bottom_y)
    if kind == 'flash':                                        # chớp trắng che điểm cắt, ~5 khung mỗi bên
        base = a if dt < 0 else b
        return Image.blend(base, Image.new('RGB', base.size, (255, 255, 255)), 0.95 * max(0.0, 1 - abs(dt) / 0.17))
    if kind == 'whip':                                         # lia nhanh: phần lớn quãng đường lúc đầu, nhoè theo tốc độ, phanh đuôi dài
        p = min(1.0, max(0.0, (dt + 0.2) / 0.55))
        norm = 1 - math.exp(-5)
        x = (1 - math.exp(-5 * p)) / norm
        v = 5 * math.exp(-5 * p) / norm
        strip = Image.new('RGB', (W * 2, bottom_y - top))
        strip.paste(a.crop(box), (0, 0)); strip.paste(b.crop(box), (W, 0))
        off = int(x * W)
        vw = strip.crop((off, 0, off + W, bottom_y - top))
        if v > 0.6:
            vw = _hblur(vw, min(260, v * 60))
        out = (b if dt >= 0 else a).copy(); out.paste(vw, (0, top))
        return out
    if kind == 'glitch':                                       # 16 dải ngang lệch ±70px + bóng 2 màu, cắt cứng giữa lúc rung mạnh nhất
        src = a if dt < 0 else b
        env = max(0.0, 1 - abs(dt) / 0.2) ** 0.6
        out = src.copy(); band = src.crop(box)
        hh = bottom_y - top
        ys = [0] + sorted(int(hh * ((i * 0.618) % 1)) for i in range(1, 16)) + [hh]
        f = int((dt + 1) * 30)
        for i in range(16):
            y0, y1 = ys[i], ys[i + 1]
            if y1 - y0 < 4:
                continue
            hsh = ((i * 31 + f * 7) * 2654435761 % 1000) / 500 - 1
            energy = 0 if i % 5 == 0 else (1 if i % 3 == 0 else 0.35)
            dx = int(70 * env * energy * (abs(hsh) ** 0.6) * (1 if hsh > 0 else -1))
            row = band.crop((0, y0, W, y1))
            if abs(dx) > 25:
                r, g, bl = row.split()
                row = Image.merge('RGB', (ImageChops.offset(r, 12, 0), g, ImageChops.offset(bl, -12, 0)))
            out.paste(ImageChops.offset(row, dx, 0), (0, top + y0))
        return out
    return Image.blend(a, b, min(1, max(0, dt / 0.12)))


def render(vid, redo_mg=False):
    global SHOTS
    V = os.path.join(ROOT, 'public', 'videos', vid)
    A = os.path.join(V, 'ad'); os.makedirs(A, exist_ok=True)
    edl = json.load(open(os.path.join(V, 'edl.json'), encoding='utf-8'))
    SHOTS = os.path.join(ROOT, 'public', 'videos', edl.get('shots_dir', '2026-10-29-xakho-shots'))   # thư mục ảnh nguồn của đợt
    CH = CHANNELS[edl.get('channel', 'k1')]
    script = json.load(open(os.path.join(V, 'script.json'), encoding='utf-8'))
    words = json.load(open(os.path.join(V, 'words.json'), encoding='utf-8'))['words']
    voice = os.path.join(V, 'voice.mp3')
    D = round(R.MA.duration(voice) + R.MA.VOICE_DELAY + R.TAIL + 0.6, 3)
    # motion graphic: mốc theo chữ trong lời đọc
    mgs = []
    for m in edl['mgs']:
        t0 = word_time(script, words, m['line'], m['word']) + R.MA.VOICE_DELAY + m.get('offset', -0.1)
        starts = line_starts(script, words)
        if 'until' in m:                                       # kéo tới đầu câu `until` (+0,2s)
            dur = starts[m['until']] + R.MA.VOICE_DELAY + 0.2 - max(0, t0)
        else:
            dur = m['dur'] if m['dur'] != 'end' else D - t0
        for it in m['data'].get('items', []):                 # thẻ quyền lợi xuất hiện đúng lúc đọc tới
            if 'word' in it:
                it['at'] = round(word_time(script, words, it.get('line', m['line']), it['word']) + R.MA.VOICE_DELAY - max(0, t0), 2)
        if 'switchWord' in m['data']:
            m['data']['switchAt'] = round(word_time(script, words, m['line'], m['data']['switchWord']) + R.MA.VOICE_DELAY - max(0, t0), 2)
        mgs.append(dict(m, t0=max(0, t0), dur=round(dur, 2)))
    ids = [m['id'] for m in mgs]                              # trùng id thì khung MG sau ghi đè MG trước (lỗi 31/10)
    assert len(ids) == len(set(ids)), f'id motion graphic bị trùng: {ids}'
    if redo_mg or not os.path.isdir(os.path.join(V, 'mg')):
        jobs = os.path.join(A, 'mg-jobs.json')
        json.dump([{'id': m['id'], 'type': m['type'], 'dur': m['dur'], 'data': m['data']} for m in mgs],
                  open(jobs, 'w', encoding='utf-8'), ensure_ascii=False)
        subprocess.run(['node', os.path.join(ROOT, 'tools', 'xakho', 'mg', 'render_mg.mjs'), jobs, os.path.join(V, 'mg'), CH['anim']], check=True)
    nframes = mg_frames(V)
    shots = prep(V, edl, script, words, D)
    # phụ đề vàng chạy theo chữ, đặt trên dải khói dưới trình duyệt
    R.MA.SUB_Y = 1450
    R.MA.YELLOW = CH['sub_hl']                                 # chữ đang đọc: vàng (kênh 1) / xanh neon (kênh 2)
    ass = os.path.join(A, 'subs.ass')
    R.MA.write_ass(ass, [' '], words, D)
    txt = open(ass, encoding='utf-8-sig').read()
    txt = '\n'.join(l for l in txt.split('\n') if not l.startswith('Dialogue: 0') and not l.startswith('Dialogue: 1'))
    open(ass, 'w', encoding='utf-8-sig').write(txt)
    # âm thanh: giọng + click chuột + SFX motion graphic (không nhạc nền, như lượt 25/10)
    hits = [(k[0], R.CLICK_SFX, -12) for s in shots for k in s['_cur'] if k[3]]
    hits += [(s['start'], SFXD + SFX['sweep'], SFX_DB['sweep']) for s in shots[1:] if s['img'] != shots[shots.index(s) - 1]['img']]
    for m in mgs:
        for kind, dt in (m.get('sfx') or []):
            hits.append((m['t0'] + dt, SFXD + SFX[kind], SFX_DB[kind]))
    a_in = ['-i', voice] + sum([['-i', h[1]] for h in hits], [])
    fx = '[0:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-15:TP=-2:LRA=11,adelay=150|150,apad[v];'
    for k, (t, _, db) in enumerate(hits):
        ms = int(t * 1000); fx += f'[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB,adelay={ms}|{ms}[c{k}];'
    fx += f'[v]{"".join(f"[c{k}]" for k in range(len(hits)))}amix=inputs={1 + len(hits)}:duration=first:normalize=0,' \
          f'atrim=0:{D},loudnorm=I=-14:TP=-1.5:LRA=11[o]'
    mix = os.path.join(A, 'mix.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *a_in, '-filter_complex', fx, '-map', '[o]', '-ar', '48000', '-ac', '2', mix], check=True)
    # hình
    cursors, bg = R.load_cursors(), R.smoke()
    if CH.get('smoke_tint'):                                   # kênh 2: khói xanh tím thay khói xám
        bg = ImageOps.colorize(bg.convert('L'), *[tuple(c) for c in CH['smoke_tint']]).convert('RGB')
    low = bg.transpose(Image.FLIP_TOP_BOTTOM)
    out = os.path.join(V, 'final.mp4')
    fontsdir = os.path.relpath(R.MA.FONTS, A).replace('\\', '/')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', mix, '-filter_complex', f'[0:v]ass=subs.ass:fontsdir={fontsdir},format=yuv420p[v]',
                          '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                          '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(D), out], stdin=subprocess.PIPE, cwd=A)
    bottom_y = R.PAGE_Y + PAGE_H

    def compose(s, t):
        fr = R.frame(s, t, cursors, bg)
        off = int((t * 14) % 120)
        fr.paste(low.crop((0, off, W, off + H - bottom_y)), (0, bottom_y))
        return fr

    for i in range(int(D * FPS)):
        t = i / FPS
        k = next((j for j, s in enumerate(shots) if s['start'] <= t < s['end']), len(shots) - 1)
        fr = compose(shots[k], t)
        tr = shots[k + 1].get('trans') if k + 1 < len(shots) else None
        if tr and t > shots[k + 1]['start'] - 0.2:            # nửa trước của chuyển cảnh vào cảnh sau
            fr = transition(tr, fr, compose(shots[k + 1], t), t - shots[k + 1]['start'], bottom_y)
        elif k > 0 and shots[k].get('trans') and t - shots[k]['start'] < 0.35:
            fr = transition(shots[k]['trans'], compose(shots[k - 1], t), fr, t - shots[k]['start'], bottom_y)
        elif k > 0 and t - shots[k]['start'] < 0.12:
            fr = Image.blend(compose(shots[k - 1], t), fr, (t - shots[k]['start']) / 0.12)
        fa = flash_alpha(shots[k], t)
        if fa > 0:
            fr = Image.blend(fr, Image.new('RGB', fr.size, (255, 255, 255)), fa)
        fr = fr.convert('RGBA')
        for m in mgs:
            j = int((t - m['t0']) * FPS)
            if 0 <= j < nframes.get(m['id'], 0):
                fr.alpha_composite(Image.open(os.path.join(V, 'mg', m['id'], f'f{j:04d}.png')))
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    json.dump({'duration': D, 'shots': [{k: v for k, v in s.items() if not k.startswith('_')} for s in shots],
               'mgs': [{k: m[k] for k in ('id', 'type', 't0', 'dur')} for m in mgs]},
              open(os.path.join(V, 'render-manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'✅ {vid}: {D}s, {len(shots)} cảnh, {len(mgs)} motion graphic → {out}')


if __name__ == '__main__':
    render(sys.argv[1], '--mg' in sys.argv)
