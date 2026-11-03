"""Dựng video quảng cáo ngắn kiểu TikTok từ clip anh tự quay: tiêu đề vàng phát sáng ở trên đầu + phụ đề chạy theo lời + giọng đọc.

  python tools/ads/make_ad.py <jobs.json> [id …]
  jobs.json: { "<video-id>": { "src": "<clip gốc>", "start": giây, "title": ["dòng 1", "dòng 2"?], "bpm": 100 } }

Mỗi video cần sẵn public/videos/<id>/voice.mp3 + words.json (tools/lux/voice_vieneu.py hoặc tools/characters/voice.mjs).
Kết quả: final.mp4 (1080×1920 30fps, tắt tiếng gốc, giọng + nhạc nền tổng hợp nhẹ, master −14 LUFS / TP −1),
thumbnail.jpg, ad/ (subs.ass, stems). Chữ vẽ bằng libass (phụ đề ASS) với font Be Vietnam Pro Black.
"""
import json, os, re, subprocess, sys
from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'lux'))
import synth_audio as SA  # noqa: E402  (nhạc nền tổng hợp dùng chung với lux)

W, H, FPS = 1080, 1920, 30
FONTS = os.path.join(ROOT, 'tools', 'ads', 'fonts')
FONT = os.path.join(FONTS, 'BeVietnamPro-Black.ttf')  # đủ dấu tiếng Việt (Comic Sans thiếu ả/ừ/ặ)
FONT_NAME = 'Be Vietnam Pro Black'
TITLE_TOP = 195        # đỉnh khối tiêu đề: dưới thanh tab TikTok, trên đầu người (không che mặt)
TITLE_SIZE = 104       # cỡ tối đa (đơn vị ASS ≈ 80px chữ); tiêu đề 2 dòng tối đa 96; dòng dài tự co cho vừa 940px
SUB_Y = 1265           # tâm phụ đề: vùng ngực, trên sticker góc dưới của clip và chữ mô tả TikTok
SUB_SIZE = 92
VOICE_DELAY = 0.15
TAIL = 0.8             # giữ hình sau khi đọc xong
YELLOW, WHITE, BLACK = '&H0000E5FF', '&H00FFFFFF', '&H000C0C0C'   # ASS: &HAABBGGRR
STICKER_LIB = os.path.join(os.path.dirname(ROOT), 'sticker-library')   # Lottie: Noto emoji + LottieFiles (LICENSES.md)
STICKER_SIZE, STICKER_DUR, STICKER_Y = 250, 1.9, 1075                   # 2 bên vùng ngực, trên phụ đề, không che mặt
STICKER_X = {'left': 75, 'right': W - 75 - 250}
POP_SFX = os.path.join(os.path.dirname(ROOT), 'sfx-library', 'mixkit', 'impact', '3005-explainer-video-pops-whoosh-light-pop.wav')
# (độ ưu tiên, sticker, điều kiện trên chữ thường đã bỏ dấu câu; w = chữ này, nx = chữ sau)
STICKER_RULES = [
    (1, 'noto-money-face', lambda w, nx: re.fullmatch(r'\d{2,3}', w) and nx in ('nghìn', 'triệu')),
    (1, 'noto-point-down', 'last-apihub'),
    (2, 'lf-check-celebrate', lambda w, nx: w == 'bảo' and nx == 'hành'),
    (3, 'noto-scream', lambda w, nx: w in ('xỉu', 'trời')),
    (3, 'noto-heart-eyes', lambda w, nx: w in ('mê', 'ái')),
    (3, 'noto-fire', lambda w, nx: w == 'khủng'),
    (4, 'noto-star-struck', lambda w, nx: w == '5tb'),
    (4, 'noto-zap', lambda w, nx: w == 'tự' and nx == 'động'),
    (5, 'noto-rocket', lambda w, nx: w == 'tốc' and nx == 'độ'),
    (5, 'noto-zap', lambda w, nx: w == 'code'),
]


def sh(*a, cwd=None):
    return subprocess.run(a, check=True, capture_output=True, text=True, cwd=cwd).stdout


def duration(path):
    return float(sh('ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path).strip())


def ts(t):
    t = max(0.0, t)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def fit_size(lines, size, maxw=940):
    """Cỡ ASS để dòng dài nhất vừa maxw (libass: cỡ chữ = ascent + descent; viền ~7px mỗi bên)."""
    f = ImageFont.truetype(FONT, 1000)
    asc, desc = f.getmetrics()
    em = lambda s: s * 1000 / (asc + desc)  # cỡ ASS → cỡ em của PIL
    widest = max(f.getlength(t) for t in lines) / 1000
    while size > 48 and widest * em(size) + 16 > maxw:
        size -= 2
    return size


def title_events(lines, dur):
    """2 lớp: quầng vàng mờ (viền dày + blur) dưới chữ trắng viền đen. Nảy vào 0,28s rồi 'thở' nhẹ ±4% mỗi 1,6s."""
    size = fit_size(lines, TITLE_SIZE if len(lines) == 1 else 96)
    anim = r'\fscx30\fscy30\t(0,140,\fscx112\fscy112)\t(140,280,\fscx100\fscy100)'
    t = 600
    while t + 1600 < dur * 1000:
        anim += rf'\t({t},{t + 800},\fscx104\fscy104)\t({t + 800},{t + 1600},\fscx100\fscy100)'
        t += 1600
    pos = rf'\an8\pos({W // 2},{TITLE_TOP})\fs{size}'
    text = r'\N'.join(lines)
    return [rf'Dialogue: 0,{ts(0)},{ts(dur)},Title,,0,0,0,,{{{pos}\bord{round(size * .2)}\3c{YELLOW}\1a&HFF&\blur{round(size * .14)}{anim}}}{text}',
            rf'Dialogue: 1,{ts(0)},{ts(dur)},Title,,0,0,0,,{{{pos}\bord{round(size * .09)}\3c{BLACK}{anim}}}{text}']


def chunks(words, max_words=3, max_chars=16):
    """Gom chữ thành cụm 1–3 chữ (≤ 16 ký tự), ngắt ở dấu câu."""
    out, cur = [], []
    for w in words:
        if cur and (len(cur) == max_words or len(' '.join(x['text'] for x in cur + [w])) > max_chars):
            out.append(cur); cur = []
        cur.append(w)
        if re.search(r'[,.!?:;…]$', w['text']):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def sub_events(words, dur):
    """Mỗi chữ một sự kiện: cả cụm hiện, chữ đang đọc màu vàng; cụm mới nảy nhẹ vào."""
    ev, cs = [], chunks(words)
    clean = lambda s: re.sub(r'[,.:;…]+$', '', s)
    for ci, c in enumerate(cs):
        nxt = cs[ci + 1][0]['startMs'] / 1000 if ci + 1 < len(cs) else dur
        c_end = min(nxt, c[-1]['endMs'] / 1000 + 0.6)
        for wi, w in enumerate(c):
            a = w['startMs'] / 1000
            b = c[wi + 1]['startMs'] / 1000 if wi + 1 < len(c) else c_end
            txt = ' '.join((rf'{{\c{YELLOW}}}{clean(x["text"])}{{\c{WHITE}}}' if k == wi else clean(x['text'])) for k, x in enumerate(c))
            pop = r'\fscx82\fscy82\t(0,110,\fscx100\fscy100)' if wi == 0 else ''
            ev.append(f'Dialogue: 2,{ts(a + VOICE_DELAY)},{ts(b + VOICE_DELAY)},Sub,,0,0,0,,{{\\an5\\pos({W // 2},{SUB_Y}){pop}}}{txt}')
    return ev


def plan_stickers(words, dur, max_n=5, gap=1.9):
    """Sticker tự động theo từ khoá: ưu tiên giá → apihub cuối → bảo hành → cảm xúc → công dụng; cách nhau ≥ gap giây."""
    low = [re.sub(r'[^\w]', '', w['text'].lower()) for w in words]
    cands = []
    for i, w in enumerate(low):
        nx = low[i + 1] if i + 1 < len(low) else ''
        for pri, name, cond in STICKER_RULES:
            if cond != 'last-apihub' and cond(w, nx):
                cands.append((pri, words[i]['startMs'] / 1000, name))
    last = [i for i, w in enumerate(low) if w == 'apihub']
    if last:
        cands.append((1, words[last[-1]]['startMs'] / 1000, 'noto-point-down'))
    picked = []
    for pri, t, name in sorted(cands):
        if len(picked) < max_n and t + 0.6 < dur and all(abs(t + VOICE_DELAY - 0.1 - p['at']) >= gap and name != p['name'] for p in picked):
            picked.append({'name': name, 'at': round(t + VOICE_DELAY - 0.1, 2)})
    picked.sort(key=lambda p: p['at'])
    for k, p in enumerate(picked):
        p['side'] = 'right' if k % 2 == 0 else 'left'
        p['dur'] = round(min(STICKER_DUR, dur - p['at']), 2) if k + 1 < len(picked) else round(dur - p['at'], 2)
    return picked


def render_sticker(name):
    """Dựng Lottie → chuỗi PNG (có đệm); trả về (thư mục, khung bắt đầu theo 'start' trong index.json)."""
    lib = json.load(open(os.path.join(STICKER_LIB, 'index.json'), encoding='utf-8'))
    out = os.path.join(STICKER_LIB, '.cache', f'{name}-{STICKER_SIZE}')
    sh('node', os.path.join(ROOT, 'tools', 'stickers', 'render_lottie.mjs'), os.path.join(STICKER_LIB, lib[name]['file']),
       out, '--size', str(STICKER_SIZE), cwd=ROOT)
    frames = json.load(open(os.path.join(out, 'meta.json'), encoding='utf-8'))['frames']
    return out, int(lib[name].get('start', 0) * frames)


def write_ass(path, title, words, dur):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,{FONT_NAME},{TITLE_SIZE},{WHITE},{WHITE},{BLACK},&H80000000,0,0,0,0,100,100,0,0,1,7,0,8,0,0,0,1
Style: Sub,{FONT_NAME},{SUB_SIZE},{WHITE},{WHITE},{BLACK},&H99000000,0,0,0,0,100,100,0,0,1,7,3,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write(head + '\n'.join(title_events(title, dur) + sub_events(words, dur)) + '\n')


def make(vid, job):
    V = os.path.join(ROOT, 'public', 'videos', vid)
    A = os.path.join(V, 'ad'); os.makedirs(A, exist_ok=True)
    voice = os.path.join(V, 'voice.mp3')
    D = round(duration(voice) + VOICE_DELAY + TAIL, 3)
    # 1. chữ: tiêu đề + phụ đề (ASS)
    words = json.load(open(os.path.join(V, 'words.json'), encoding='utf-8'))['words']
    write_ass(os.path.join(A, 'subs.ass'), job['title'], words, D)
    stickers = plan_stickers(words, D) if job.get('stickers') == 'auto' else job.get('stickers') or []   # mặc định không sticker; bật bằng "stickers": "auto"
    json.dump(stickers, open(os.path.join(A, 'stickers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 2. âm thanh: giọng −15 LUFS (trễ 0,15s) + nhạc nền nhẹ −30 LUFS + tiếng pop nhỏ lúc sticker hiện → master −14 / TP −1
    music = os.path.join(A, 'music.wav')
    SA.write(music, SA.music(D, float(job.get('bpm', 100))))
    mix = os.path.join(A, 'mix.wav')
    pops = [s for s in stickers if os.path.exists(POP_SFX)]
    a_in = ['-i', voice, '-i', music] + sum([['-i', POP_SFX] for _ in pops], [])
    a_fx = ('[0:a]aresample=48000,loudnorm=I=-15:TP=-2:LRA=11,adelay=150|150,apad[v];'
            '[1:a]aresample=48000,loudnorm=I=-30:TP=-6:LRA=11[m];')
    for k, s in enumerate(pops):
        ms = int(s['at'] * 1000)
        a_fx += f'[{k + 2}:a]aresample=48000,aformat=channel_layouts=stereo,volume=-16dB,adelay={ms}|{ms}[p{k}];'
    a_fx += f'[v][m]{"".join(f"[p{k}]" for k in range(len(pops)))}amix=inputs={2 + len(pops)}:duration=first:normalize=0,' \
            f'atrim=0:{D},loudnorm=I=-14:TP=-1.5:LRA=11[o]'
    sh('ffmpeg', '-y', '-v', 'error', *a_in, '-filter_complex', a_fx, '-map', '[o]', '-ar', '48000', '-ac', '2', mix)
    # 3. hình: đoạn clip gốc + sticker Lottie + chữ; tắt tiếng gốc. Chạy trong ad/ để đường dẫn filter không có ':' / dấu cách.
    out = os.path.join(V, 'final.mp4')
    fontsdir = os.path.relpath(FONTS, A).replace('\\', '/')
    v_in, v_fx = [], f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuva420p[b0];'
    for k, s in enumerate(stickers):
        d, first = render_sticker(s['name'])
        v_in += ['-framerate', str(FPS), '-loop', '1', '-start_number', str(first), '-t', str(s['dur']), '-i', os.path.join(d, 'f_%03d.png')]
        v_fx += (f'[{k + 2}:v]format=rgba,fade=in:st=0:d=0.15:alpha=1,fade=out:st={max(0, s["dur"] - 0.2):.2f}:d=0.2:alpha=1,'
                 f'setpts=PTS-STARTPTS+{s["at"]}/TB[s{k}];'
                 f'[b{k}][s{k}]overlay={STICKER_X[s["side"]]}:{STICKER_Y - STICKER_SIZE // 2}:eof_action=pass[b{k + 1}];')
    v_fx += f'[b{len(stickers)}]ass=subs.ass:fontsdir={fontsdir},format=yuv420p[v]'
    sh('ffmpeg', '-y', '-v', 'error', '-ss', str(job['start']), '-t', str(D), '-i', job['src'], '-i', mix, *v_in,
       '-filter_complex', v_fx,
       '-map', '[v]', '-map', '1:a', '-t', str(D), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
       '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out, cwd=A)
    sh('ffmpeg', '-y', '-v', 'error', '-ss', '1.0', '-i', out, '-frames:v', '1', '-q:v', '2', os.path.join(V, 'thumbnail.jpg'))
    print(f'✅ {vid}: {D}s từ giây {job["start"]} → {out}')


if __name__ == '__main__':
    jobs = json.load(open(sys.argv[1], encoding='utf-8'))
    for vid in sys.argv[2:] or jobs:
        make(vid, jobs[vid])
