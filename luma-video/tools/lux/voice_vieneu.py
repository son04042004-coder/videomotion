"""Giọng offline cho luồng lux — VieNeu-TTS (--engine vieneu, mặc định) hoặc VoxCPM2 nhân bản giọng mẫu (--engine voxcpm): storyboard.json → voice.mp3 + words.json (cùng định dạng luma voice / Edge).

VieNeu không trả mốc từng chữ → đọc lại bằng faster-whisper (CPU int8) rồi khớp với chữ kịch bản (difflib),
chữ không khớp được nội suy giữa hai mốc. Chữ hiển thị giữ nguyên kịch bản (kể cả dấu câu, số); chỉ chữ ĐỌC
được đổi: số → chữ, thuật ngữ tiếng Anh → cách đọc (config/pronunciation.json: mục "edge" + ghi đè "vieneu").

  <venv-tts>/python tools/lux/voice_vieneu.py <id> [--voice "Adam bựa"] [--gap 0.28]
  <venv-tts>/python tools/lux/voice_vieneu.py <id> --engine voxcpm [--ref public/brand/cuhub/voice/cu-k.wav]   (giọng Cú Hub)
  <venv-tts>/python tools/lux/voice_vieneu.py --selftest
"""
import difflib, json, re, subprocess, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UNITS = "không một hai ba bốn năm sáu bảy tám chín".split()
PUNCT = '.,;:!?"“”‘’…()[]'


def norm(w):
    return re.sub(r"[^\w]+", "", unicodedata.normalize("NFC", w.lower()), flags=re.UNICODE)


def _under_1000(n, full=False):
    h, t, u = n // 100, (n // 10) % 10, n % 10
    out = []
    if h or full:
        out += [UNITS[h], "trăm"]
    if t == 0:
        if u and (h or full):
            out += ["linh", UNITS[u]]
        elif u:
            out.append(UNITS[u])
    elif t == 1:
        out.append("mười")
        if u:
            out.append("lăm" if u == 5 else UNITS[u])
    else:
        out += [UNITS[t], "mươi"]
        if u:
            out.append({1: "mốt", 4: "tư", 5: "lăm"}.get(u, UNITS[u]))
    return out


def num_vi(s):
    """'270' → 'hai trăm bảy mươi'; '0,03' → 'không phẩy không ba'; '1.000' → 'một nghìn'."""
    s = s.replace(".", "") if re.fullmatch(r"\d{1,3}(\.\d{3})+", s) else s
    if "," in s:
        a, b = s.split(",", 1)
        return num_vi(a) + " phẩy " + " ".join(UNITS[int(c)] for c in b)
    n = int(s)
    if n == 0:
        return "không"
    parts = []
    for size, name in ((10 ** 9, "tỷ"), (10 ** 6, "triệu"), (1000, "nghìn")):
        if n >= size:
            parts += _under_1000(n // size) + [name]
            n %= size
            if 0 < n < 100:
                parts += ["không", "trăm"] + _under_1000(n)
                n = 0
    if n:
        parts += _under_1000(n, full=bool(parts))
    return " ".join(parts)


def spoken_of(token, pron):
    core = token.strip(PUNCT)
    trail = token[len(token.rstrip(PUNCT)):]
    if core in pron:
        sp = pron[core]
    elif re.fullmatch(r"\d[\d.,]*", core):
        sp = num_vi(core)
    else:
        sp = core
    return (sp + trail).split()


def align(spoken, heard, t0, t1):
    """Mốc (start, end) cho từng chữ đọc: khớp với chữ whisper nghe được, phần còn lại nội suy."""
    a = [norm(t) for t in spoken]
    b = [norm(w["text"]) for w in heard]
    out = [None] * len(spoken)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                out[i1 + k] = (heard[j1 + k]["start"], heard[j1 + k]["end"])
    i = 0
    while i < len(out):
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < len(out) and out[j] is None:
            j += 1
        left = out[i - 1][1] if i > 0 else t0
        right = out[j][0] if j < len(out) else t1
        step = max(0.05, (right - left) / (j - i))
        for k in range(i, j):
            s = left + (k - i) * step
            out[k] = (s, s + step * 0.9)
        i = j
    for k in range(1, len(out)):  # tăng dần, không rỗng
        s, e = out[k]
        s = max(s, out[k - 1][1])
        out[k] = (s, max(e, s + 0.05))
    return out


def take_errors(expected, heard):
    """Số chữ lệch giữa lời kịch bản và lời Whisper nghe được (để chọn bản đọc rõ nhất)."""
    fix = lambda t: [w for w in (norm(x) for x in t.replace("ngàn", "nghìn").split()) if w]
    a, b = fix(expected), fix(heard)
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if tag != "equal")


def selftest():
    cases = {"270": "hai trăm bảy mươi", "280": "hai trăm tám mươi", "0,03": "không phẩy không ba", "1.000": "một nghìn",
             "15": "mười lăm", "21": "hai mươi mốt", "105": "một trăm linh năm", "2026": "hai nghìn không trăm hai mươi sáu", "10": "mười"}
    bad = {k: (num_vi(k), v) for k, v in cases.items() if num_vi(k) != v}
    sp = spoken_of("270", {}) + spoken_of("API,", {"API": "ây pi ai"})
    assert sp == ["hai", "trăm", "bảy", "mươi", "ây", "pi", "ai,"], sp
    al = align(["a", "b", "c"], [{"text": "a", "start": 0.0, "end": 0.2}, {"text": "c", "start": 0.6, "end": 0.8}], 0.0, 1.0)
    assert al[1][0] >= al[0][1] and al[1][1] <= 0.6 + 1e-9, al
    assert take_errors("sạch, bẩn hay nứt?", "sạch bận hay nứt") == 1 and take_errors("Một nghìn quả", "Một ngàn quả") == 0
    print("selftest", "OK" if not bad else f"FAIL {bad}")
    return not bad


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(0 if selftest() else 1)
    opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
    vid = args[0]
    engine = opt("--engine", "vieneu")  # vieneu | voxcpm
    voice = opt("--voice", "Adam bựa")
    gap = float(opt("--gap", 0.28))
    V = ROOT / "public" / "videos" / vid
    sb = json.loads((V / "storyboard.json").read_text(encoding="utf-8"))
    pj = json.loads((ROOT / "config" / "pronunciation.json").read_text(encoding="utf-8"))
    if engine == "voxcpm":
        # VoxCPM2 đọc thuật ngữ tiếng Anh tự nhiên → chỉ đổi số + mục "voxcpm"; giọng = nhân bản từ một wav mẫu (cả video một giọng)
        ref = opt("--ref", str(ROOT / "public" / "brand" / "cuhub" / "voice" / "cu-k.wav"))
        ref_text = Path(opt("--ref-text", str(Path(ref).with_suffix(".txt")))).read_text(encoding="utf-8").strip()
        pron, voice_id = pj.get("voxcpm", {}), f"voxcpm:{Path(ref).name}"
    else:
        pron, voice_id = {**pj.get("edge", {}), **pj.get("vieneu", {})}, voice
    tmp = V / ".tts" / engine
    tmp.mkdir(parents=True, exist_ok=True)

    import numpy as np
    from faster_whisper import WhisperModel
    tts = asr = None  # chỉ nạp model khi có câu cần tạo lại
    SR = 48000
    # lượt 1: câu nào cần tạo lại (bộ đệm theo giọng + lời đọc)
    scenes = []
    for k, sc in enumerate(sb["scenes"]):
        display = sc["say"].split()
        owner, spoken = [], []
        for i, d in enumerate(display):
            for s_ in spoken_of(d, pron):
                owner.append(i); spoken.append(s_)
        wav = tmp / f"s{k + 1:02d}.wav"
        key, kf, hf = f"{voice_id}\n{' '.join(spoken)}", tmp / f"s{k + 1:02d}.key", tmp / f"s{k + 1:02d}.heard.json"
        same = kf.exists() and kf.read_text(encoding="utf-8") == key
        cached = wav.exists() and hf.exists() and same  # câu không đổi → giữ nguyên giọng cũ
        seeded = wav.exists() and not kf.exists() and "--seed" in args  # --seed: nhận wav có sẵn làm bộ đệm (chỉ chạy lại whisper)
        scenes.append(dict(display=display, owner=owner, spoken=spoken, wav=wav, key=key, kf=kf, hf=hf, cached=cached, synth=not cached and not seeded))
    todo = [sc for sc in scenes if sc["synth"]]
    if todo and engine == "voxcpm":
        jobs = tmp / "jobs.json"
        seeds = [7, 11, 21, 33, 47][:max(1, int(opt("--takes", 2)))]  # nhiều bản / câu, giữ bản đọc rõ nhất
        jobs.write_text(json.dumps({"ref": ref, "refText": ref_text, "cfg": 2.0, "steps": 12,
                                    "jobs": [{"text": " ".join(sc["spoken"]), "seed": sd, "out": str(sc["wav"].with_suffix(f".t{sd}.wav"))}
                                             for sc in todo for sd in seeds]}, ensure_ascii=False), encoding="utf-8")
        py = ROOT / ".venv-voice" / "Scripts" / "python.exe"
        subprocess.run([str(py), "voxcpm_batch.py", str(jobs)], cwd=str(ROOT / "scripts"), check=True)
        asr = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
        for sc in todo:
            best = None
            for sd in seeds:
                take = sc["wav"].with_suffix(f".t{sd}.wav")
                segs, _ = asr.transcribe(str(take), language="vi", beam_size=5)
                e = take_errors(" ".join(sc["display"]), " ".join(x.text for x in segs))
                print(f"  bản seed {sd}: {e} chữ sai", flush=True)
                if best is None or e < best[0]:
                    best = (e, take)
            import shutil
            shutil.copyfile(best[1], sc["wav"])
    elif todo:
        from vieneu import Vieneu
        tts = Vieneu()
        for sc in todo:
            tts.save(tts.infer(" ".join(sc["spoken"]), voice=voice), str(sc["wav"]))
    # lượt 2: cắt lặng, khớp chữ, ghép
    pieces, words, t = [], [], 0.0
    for k, sc in enumerate(scenes):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(sc["wav"]), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32)
        nz = np.nonzero(np.abs(x) > 0.01)[0]  # cắt lặng đầu/cuối, chừa 30 ms
        x = x[max(0, nz[0] - int(0.03 * SR)):nz[-1] + int(0.03 * SR)] if len(nz) else x
        dur = len(x) / SR
        if sc["cached"]:
            heard = json.loads(sc["hf"].read_text(encoding="utf-8"))
        else:
            if asr is None:
                asr = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
            segs, _ = asr.transcribe(_resample16(x, SR), language="vi", word_timestamps=True, vad_filter=False, beam_size=5)
            heard = [{"text": w.word.strip(), "start": w.start, "end": w.end} for s_ in segs for w in (s_.words or []) if w.word.strip()]
            sc["hf"].write_text(json.dumps(heard, ensure_ascii=False), encoding="utf-8")
            sc["kf"].write_text(sc["key"], encoding="utf-8")
        sp_t = align(sc["spoken"], heard, 0.0, dur)
        for i, d in enumerate(sc["display"]):
            idx = [j for j, o in enumerate(sc["owner"]) if o == i]
            s0, e0 = sp_t[idx[0]][0], sp_t[idx[-1]][1]
            words.append({"text": d, "startMs": round((t + s0) * 1000), "endMs": round((t + e0) * 1000)})
        pieces.append(x)
        pieces.append(np.zeros(int(gap * SR), np.float32))
        t += dur + gap
        print(f"  câu {k + 1}: {dur:4.1f}s, nghe được {len(heard)}/{len(sc['spoken'])} chữ{' (giữ nguyên)' if sc['cached'] else ''}", flush=True)
    audio = np.concatenate(pieces[:-1])
    full = tmp / "voice.wav"
    import wave
    with wave.open(str(full), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(full), "-ar", "48000", "-b:a", "192k", str(V / "voice.mp3")], check=True)
    dur_ms = round(len(audio) / SR * 1000)
    (V / "words.json").write_text(json.dumps({"durationMs": dur_ms, "provider": f"{engine}:{voice_id}", "words": words}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ voice ({engine}: {voice_id}): {len(words)} chữ, {dur_ms / 1000:.1f}s → {V / 'voice.mp3'}")


def _resample16(x, sr):
    import numpy as np
    n = int(len(x) * 16000 / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


if __name__ == "__main__":
    main()
