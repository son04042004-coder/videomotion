"""Nhạc nền tổng hợp bằng numpy + SFX/riser THẬT từ kho sfx-library (Mixkit / Kenney CC0; thiếu file thì tự tổng hợp).

Dùng: python synth_audio.py <events.json> <out_dir>
events.json: {"duration": giây, "bpm": 110, "riserEnd": giây|null, "sfx": [{"t": giây, "type": "pop|tick|key|click|chime|whoosh"}]}
Ghi ra out_dir: music.wav, sfx.wav, riser.wav (48 kHz stereo 16-bit). Mức tuyệt đối: SFX đỉnh ~-12 dBFS, tick/key ~-18, riser ~-16;
nhạc được chuẩn hoá loudness ở bước mix. Kho SFX: biến môi trường SFX_LIB (mặc định C:/REMOTION VIDEO EDITING/sfx-library/).
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)  # cố định → kết quả lặp lại được
LIB = os.environ.get("SFX_LIB", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "sfx-library"))
# loại sự kiện → các file trong kho (xoay vòng) + mức đỉnh dBFS
REAL = {
    "pop": [("mixkit/pop/2356-dry-pop-up-notification-alert.wav", -9)],
    "tick": [("kenney/interface-sounds/Audio/tick_002.ogg", -9)],  # -14 bị nhạc lấn (đo 2026-10-11) → -9
    "key": [("mixkit/keyboard/2533-single-key-type.wav", -13), ("mixkit/keyboard/2541-single-key-press-in-a-laptop.wav", -13),
            ("mixkit/keyboard/2542-hard-single-key-press-in-a-laptop.wav", -14)],
    "click": [("mixkit/click/1113-mouse-click-close.wav", -6)],
    "chime": [("mixkit/pop/2867-confirmation-tone.wav", -11)],
    "whoosh": [("mixkit/transition/1492-cinematic-whoosh-fast-transition.wav", -13)],
    "swipe": [("mixkit/transition/1489-air-woosh.wav", -14)],   # cuộn trang: gió lướt mềm
    "check": [("mixkit/click/2573-interface-option-select.wav", -10)],  # tích xanh trong danh sách: tiếng UI trong, đủ dài
    "cross": [("kenney/interface-sounds/Audio/error_006.ogg", -11)],    # dòng cảnh báo ✕: trầm, không chói
    "tab": [("kenney/interface-sounds/Audio/toggle_001.ogg", -11)],     # chuyển tab tiến trình
    # tô vàng: tiếng "bling" kiểu UI — chồng iu chọn sau 2 đợt nghe thử A–F (2026-10-09)
    "marker": [("mixkit/pop/2357-bubble-pop-up-alert-notification.wav", -10)],
    # theme doc (video phân tích): cú lộ số lớn / tiêu đề → boom trầm; thẻ bay vào mạnh → hit; cú lộ chính → shimmer (tự tổng hợp)
    "dtick": [("mixkit/click/2568-cool-interface-click-tone.wav", -9)],  # theme doc: blip có tông (~2 kHz) khi chữ / chip / số bật ra, như video mẫu
    "boom": [("mixkit/impact/2909-cool-impact-movie-trailer.wav", -12)],
    "hit": [("mixkit/impact/2903-movie-whoosh-impact-presentation.wav", -13)],
}
TAIL = {"boom": 2.4, "hit": 1.6}  # cắt đuôi dài của tiếng impact (giây), có fade
RISER = ("mixkit/riser/790-cinematic-trailer-riser.wav", -16)
UI = {"pop", "tick", "dtick", "key", "click", "chime", "check", "cross", "tab", "marker"}  # tiếng giao diện: nhạc nép xuống quanh mỗi tiếng
DUCK_DB = -9


def duck_curve(n, events, extra=()):
    """Đường hạ nhạc: -9 dB quanh mỗi tiếng UI (vào 30 ms, giữ ~0,35 s, nhả 150 ms) → tiếng UI nổi ≥ +3 dB mà không phải đẩy quá to."""
    g = np.ones(n)
    low = 10 ** (DUCK_DB / 20)
    a, r = int(0.03 * SR), int(0.15 * SR)
    for e in events:
        if e["type"] not in UI and e["type"] not in extra:
            continue
        i0 = int((float(e["t"]) - 0.03) * SR)
        i1 = i0 + a + int((0.42 if e["type"] == "marker" else 0.32) * SR)
        ramp_in = np.linspace(1, low, a)
        ramp_out = np.linspace(low, 1, r)
        seg = np.concatenate([ramp_in, np.full(max(0, i1 - i0 - a), low), ramp_out])
        lo, hi = max(0, i0), min(n, i0 + len(seg))
        if hi > lo:
            g[lo:hi] = np.minimum(g[lo:hi], seg[lo - i0:hi - i0])
    return g


def load_real(rel, dbfs):
    """Đọc 1 file trong kho → mono 48 kHz, bỏ khoảng lặng đầu (để tiếng bắt đầu đúng mốc sự kiện); None nếu không có."""
    p = LIB + rel
    if not os.path.exists(p):
        return None
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    if not raw:
        return None
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    x = x[int(np.argmax(np.abs(x) > np.abs(x).max() * 0.3)):]
    return peak_to(x, dbfs)


def load_variant(v):
    """Một biến thể: (file, dBFS) hoặc danh sách lớp [(file, dBFS), …] trộn chung, căn điểm bắt đầu."""
    if isinstance(v, list):
        xs = [x for x in (load_real(f, db) for f, db in v) if x is not None]
        if not xs:
            return None
        y = np.zeros(max(len(x) for x in xs))
        for x in xs:
            y[:len(x)] += x
        return y
    return load_real(*v)


def env_exp(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def note(freq, dur, harmonics=6, detune=0.004):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        for dt in (-detune, detune):
            out += np.sin(2 * np.pi * freq * k * (1 + dt) * t) / (k ** 1.6)
    return out / harmonics


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def peak_to(sig, dbfs):
    p = np.max(np.abs(sig)) or 1.0
    return sig / p * (10 ** (dbfs / 20))


def music_doc(duration, bpm):
    """Nhạc theme doc: beat điện ảnh tối (Rê thứ), sub drone, kick + clap kiểu half-time, hat mỗi phách, pluck mờ — giống video mẫu phân tích (~136 BPM)."""
    n = int(duration * SR)
    buf = np.zeros(n)
    beat = 60.0 / bpm
    bar = 4 * beat
    chords = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (98.0, 116.54, 146.83), (110.0, 138.59, 164.81)]
    roots = [73.42, 58.27, 49.0, 55.0]
    t, k = 0.0, 0
    while t < duration:
        ch, rt = chords[(k // 2) % 4], roots[(k // 2) % 4]
        if k % 2 == 0:  # pad + sub đổi mỗi 2 nhịp lớn
            L = 2 * bar + 0.5
            pad = sum(note(f, L, harmonics=7, detune=0.006) for f in ch)
            a = np.minimum(1, np.arange(len(pad)) / (0.8 * SR)) * np.minimum(1, (len(pad) - np.arange(len(pad))) / (0.6 * SR))
            place(buf, lowpass(pad * a, 1400) * 0.20, t)
            tt = np.arange(int(L * SR)) / SR
            sub = np.sin(2 * np.pi * rt * tt) * (0.6 + 0.4 * np.sin(np.pi * tt / L)) * np.minimum(1, tt / 0.3) * np.minimum(1, (L - tt) / 0.4)
            place(buf, sub * 0.42, t)
        for b in (0.0, 2.5):  # kick half-time
            kt = np.arange(int(0.32 * SR)) / SR
            f = 42 + 90 * np.exp(-kt * 26)
            place(buf, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 11) * 0.7, t + b * beat)
        cl = int(0.35 * SR)  # clap phách 3: nhiễu dải giữa + đuôi
        clap = (highpass(lowpass(rng.standard_normal(cl), 4200), 900)) * (env_exp(cl, 0.025) + 0.25 * env_exp(cl, 0.16))
        place(buf, clap * 0.22, t + 2 * beat)
        for b in range(4):  # hat mỗi phách (khoảng 0,44 s ở 136 BPM), phách lẻ nhẹ hơn
            hd = int(0.045 * SR)
            hat = highpass(rng.standard_normal(hd), 7000) * env_exp(hd, 0.011)
            place(buf, hat * (0.10 if b % 2 == 0 else 0.07), t + b * beat)
        if k % 2 == 1:  # pluck mờ: rải hợp âm quãng tám trên
            for j, f in enumerate((ch[0] * 4, ch[1] * 4, ch[2] * 4, ch[1] * 4)):
                pd = int(0.5 * SR)
                pl = note(f, 0.5, harmonics=3, detune=0.0) * env_exp(pd, 0.12)
                place(buf, pl * 0.05, t + j * beat * 0.5)
        t += bar
        k += 1
    buf = lowpass(buf, 10000)
    buf[: int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))
    fo = min(n, int(1.2 * SR))
    buf[n - fo:] *= np.linspace(1, 0, fo)
    return peak_to(buf, -6)


def shimmer():
    """Chuỗi chuông lấp lánh nhiều hoạ âm 2–12 kHz, vào so le, tắt dần ~1,4 s (cú lộ chính trong video mẫu)."""
    d = int(1.6 * SR)
    s = np.zeros(d)
    for j, f0 in enumerate((2093, 2637, 3136, 4186, 5274, 6272, 8372, 10548, 12543)):
        off = int((j * 0.012 + rng.random() * 0.02) * SR)
        tt = np.arange(d - off) / SR
        s[off:] += np.sin(2 * np.pi * f0 * (1 + 0.002 * rng.standard_normal()) * tt) * np.exp(-tt * (2.2 + j * 0.25)) / (1 + j * 0.15)
    s += 0.05 * highpass(rng.standard_normal(d), 6000) * env_exp(d, 0.25)
    return peak_to(s, -15)


def music(duration, bpm):
    n = int(duration * SR)
    buf = np.zeros(n)
    beat = 60.0 / bpm
    # A thứ: Am – F – C – G, mỗi hợp âm 1 nhịp lớn (4 phách)
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 261.63, 329.63), (196.0, 246.94, 293.66)]
    roots = [110.0, 87.31, 130.81, 98.0]
    bar = 4 * beat
    t = 0.0
    k = 0
    while t < duration:
        ch = chords[k % 4]
        pad = sum(note(f, bar + 0.4, harmonics=5) for f in ch)
        a = np.minimum(1, np.arange(len(pad)) / (0.35 * SR)) * np.minimum(1, (len(pad) - np.arange(len(pad))) / (0.4 * SR))
        place(buf, pad * a * 0.22, t)
        for b in (0, 2):  # bass gảy phách 1 và 3
            bs = note(roots[k % 4], beat * 1.8, harmonics=3, detune=0.0) * env_exp(int(beat * 1.8 * SR), 0.35)
            place(buf, bs * 0.5, t + b * beat)
        for b in range(4):  # kick êm mỗi phách + hat nhẹ nhịp lẻ
            kt = np.arange(int(0.28 * SR)) / SR
            f = 45 + 75 * np.exp(-kt * 30)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 14)
            place(buf, kick * 0.55, t + b * beat)
            hat = highpass(rng.standard_normal(int(0.05 * SR)), 6000) * env_exp(int(0.05 * SR), 0.012)
            place(buf, hat * 0.08, t + b * beat + beat / 2)
        t += bar
        k += 1
    buf = lowpass(buf, 9000)
    buf[: int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))  # chỉ declick 5 ms
    fo = min(n, int(0.8 * SR))
    buf[n - fo:] *= np.linspace(1, 0, fo)
    return peak_to(buf, -6)


def sfx_sound(kind):
    if kind == "pop":
        d = int(0.12 * SR)
        tt = np.arange(d) / SR
        f = 260 + 420 * np.exp(-tt * 40)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 28) + 0.15 * highpass(rng.standard_normal(d), 3000) * np.exp(-tt * 90)
        return peak_to(s, -12)
    if kind in ("check", "tab"):
        d = int(0.22 * SR)
        tt = np.arange(d) / SR
        s = np.sin(2 * np.pi * (1568 if kind == "check" else 2400) * tt) * np.exp(-tt * 18)
        return peak_to(s, -15)
    if kind == "cross":
        d = int(0.16 * SR)
        tt = np.arange(d) / SR
        s = np.sign(np.sin(2 * np.pi * 220 * tt)) * np.exp(-tt * 20)
        return peak_to(lowpass(s, 2000), -16)
    if kind == "marker":
        d = int(0.32 * SR)
        x = highpass(rng.standard_normal(d), 2500) * np.sin(np.linspace(0, np.pi, d)) ** 0.7
        return peak_to(x, -17)
    if kind in ("tick", "key"):
        d = int(0.025 * SR)
        s = highpass(rng.standard_normal(d), 4000) * env_exp(d, 0.004)
        return peak_to(s, -18 if kind == "key" else -16)
    if kind == "click":
        d = int(0.06 * SR)
        tt = np.arange(d) / SR
        s = np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 70) + 0.6 * highpass(rng.standard_normal(d), 2500) * np.exp(-tt * 120)
        return peak_to(s, -12)
    if kind == "chime":
        d = int(1.1 * SR)
        tt = np.arange(d) / SR
        s = np.zeros(d)
        for f0, off in ((1318.5, 0.0), (1975.5, 0.09)):
            seg = tt - off
            m = seg >= 0
            s[m] += (np.sin(2 * np.pi * f0 * seg[m]) + 0.25 * np.sin(2 * np.pi * f0 * 2.76 * seg[m])) * np.exp(-seg[m] * 5)
        return peak_to(s, -12)
    if kind == "shimmer":
        return shimmer()
    if kind in ("boom", "hit"):
        d = int(0.9 * SR)
        tt = np.arange(d) / SR
        f = 40 + 110 * np.exp(-tt * 18)
        return peak_to(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4) + 0.2 * lowpass(rng.standard_normal(d), 600) * np.exp(-tt * 9), -12)
    if kind == "whoosh":
        d = int(0.5 * SR)
        x = lowpass(rng.standard_normal(d), 1800)
        e = np.sin(np.linspace(0, np.pi, d)) ** 2
        return peak_to(x * e, -13)
    return np.zeros(1)


def riser(duration, end):
    n = int(duration * SR)
    buf = np.zeros(n)
    length = min(2.5, end)
    d = int(length * SR)
    tt = np.arange(d) / SR
    noise = rng.standard_normal(d)
    # lọc thông thấp mở dần: cắt đoạn 4 lần, mỗi đoạn tần số cắt cao hơn
    parts = np.array_split(noise, 8)
    filt = np.concatenate([lowpass(p, 400 + 600 * i) for i, p in enumerate(parts)])
    tone = np.sin(2 * np.pi * np.cumsum(180 + 520 * (tt / length) ** 2) / SR) * 0.3
    sig = (filt + tone) * (tt / length) ** 2
    place(buf, sig, end - length)
    return peak_to(buf, -16) if np.any(buf) else buf


def write(path, mono):
    st = np.stack([mono, mono], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ev = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    dur = float(ev["duration"])
    n = int(dur * SR)
    n_ = int(dur * SR)
    mus = (music_doc if ev.get("style") == "doc" else music)(dur, float(ev.get("bpm", 110)))
    # theme doc: nhạc to hơn → nép cả quanh tiếng nhấn (boom / hit / whoosh / shimmer) cho tiếng rõ
    write(f"{out}/music.wav", mus * duck_curve(len(mus), ev.get("sfx", []), ("boom", "hit", "whoosh", "shimmer") if ev.get("style") == "doc" else ()))
    fx = np.zeros(n)
    cache = {}
    turn = {}
    real = 0
    for e in ev.get("sfx", []):
        k = e["type"]
        if k not in cache:
            vs = [x for x in (load_variant(v) for v in REAL.get(k, [])) if x is not None]
            if k in TAIL:  # impact thật có đuôi rất dài: cắt còn TAIL giây, fade 0,4 s cuối
                cut, fl = int(TAIL[k] * SR), int(0.4 * SR)
                vs = [np.concatenate([x[:cut - fl], x[cut - fl:cut] * np.linspace(1, 0, len(x[cut - fl:cut]))]) if len(x) > cut else x for x in vs]
            real += bool(vs)
            cache[k] = vs or [sfx_sound("whoosh" if k == "swipe" else k)]
        i = turn.get(k, 0)
        turn[k] = i + 1
        x = cache[k][i % len(cache[k])]
        # whoosh / swipe: căn ĐỈNH tiếng vào mốc (giữa cú lướt); còn lại căn điểm bắt đầu
        off = int(np.argmax(np.convolve(np.abs(x), np.ones(480) / 480, "same"))) if k in ("whoosh", "swipe") else 0
        place(fx, x, float(e["t"]) - off / SR)
    write(f"{out}/sfx.wav", np.clip(fx, -1, 1))
    rz = np.zeros(n)
    for end in ev.get("risers", []):  # theme doc: riser ngắn (~1,6 s) trước từng cú lộ lớn giữa video
        rs = load_real(*RISER)
        if rs is not None and end > 0.5:
            L = min(int(min(1.6, end) * SR), len(rs))
            seg = rs[-L:] * np.linspace(0.3, 1, L)
            place(rz, seg * 0.8, end - L / SR)
    if ev.get("riserEnd"):
        end = float(ev["riserEnd"])
        rs = load_real(*RISER)
        if rs is not None:
            rs = rs[-int(min(len(rs) / SR, end) * SR):]  # riser thật kết thúc đúng lúc hết hook
            place(rz, rs, end - len(rs) / SR)
        else:
            rz = riser(dur, end)
    write(f"{out}/riser.wav", rz)
    print(json.dumps({"music": f"{out}/music.wav", "sfx": len(ev.get("sfx", [])), "sfx_real_kinds": real, "duration": dur}))


if __name__ == "__main__":
    main()
