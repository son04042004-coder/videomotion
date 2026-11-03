"""Giọng cho video quay-màn-hình: cả kịch bản đọc MỘT lần qua Vibi (ElevenLabs, có thẻ cảm xúc [excited] …),
rồi faster-whisper lấy mốc từng chữ và khớp với chữ hiển thị (thẻ cảm xúc bị bỏ khỏi phụ đề).

  <venv-tts>/python tools/screenad/voice.py <id> [--voice pNInz6obpgDQGcFmaJgB] [--model eleven_v4] [--speed 1.0] [--stability 0] [--style 0.6]
  --stability 0 --style 0.6: chế độ biểu cảm (chồng iu chọn 02/11 cho /videomotion); bỏ trống = mặc định của ElevenLabs.
Đọc public/videos/<id>/script.json: { "lines": ["[excited] Ủa alo các bác! …", …], "spoken": {"apihub247": "…"} }
Ra: voice.mp3 + words.json (cùng định dạng các luồng khác).
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'characters'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'lux'))
import vibi_tts  # noqa: E402
from voice_vieneu import align, norm, num_vi  # noqa: E402
TAG = re.compile(r'\[[^\]]+\]')


def main():
    a = sys.argv[1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    vid = a[0]
    V = os.path.join(ROOT, 'public', 'videos', vid)
    sc = json.load(open(os.path.join(V, 'script.json'), encoding='utf-8'))
    spoken_map = sc.get('spoken', {})
    text = ' '.join(sc['lines'])
    for k, v in spoken_map.items():           # cách đọc riêng (chỉ phần gửi đi đọc)
        text = text.replace(k, v)
    raw = os.path.join(V, 'voice.raw.mp3')
    if not ('--reuse' in a and os.path.exists(raw)):        # --reuse: giữ giọng đã thu, chỉ căn chữ lại
      num = lambda k: None if opt(k) is None else float(opt(k))
      vibi_tts.synth(text, raw, opt('--voice', 'pNInz6obpgDQGcFmaJgB'), 'elevenlabs', opt('--model', 'eleven_v4'),
                   'vi', float(opt('--speed', 1.0)), stability=num('--stability'), style=num('--style'))
    # cắt lặng đầu/cuối, chuẩn hoá về mp3 48 kHz
    out = os.path.join(V, 'voice.mp3')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                    '-ar', '48000', '-b:a', '192k', out], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out],
                               capture_output=True, text=True).stdout)
    # chữ hiển thị (bỏ thẻ) → chữ "đọc" để khớp với whisper (số → chữ, áp cách đọc riêng)
    display = TAG.sub(' ', ' '.join(sc['lines'])).split()
    owner, spoken = [], []
    for i, d in enumerate(display):
        core = d.strip('.,;:!?…"“”()')
        sp = spoken_map[core] if core in spoken_map else num_vi(core) if re.fullmatch(r'\d[\d.,]*', core) else core
        for s in sp.split():
            owner.append(i); spoken.append(s)
    from faster_whisper import WhisperModel
    asr = WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')
    segs, _ = asr.transcribe(out, language='vi', word_timestamps=True, beam_size=5)
    heard = [{'text': w.word.strip(), 'start': w.start, 'end': w.end} for s in segs for w in (s.words or []) if w.word.strip()]
    times = align(spoken, heard, 0.0, dur)
    words = []
    for i, d in enumerate(display):
        idx = [j for j, o in enumerate(owner) if o == i]
        words.append({'text': d, 'startMs': round(times[idx[0]][0] * 1000), 'endMs': round(times[idx[-1]][1] * 1000)})
    json.dump({'durationMs': round(dur * 1000), 'provider': 'vibi:elevenlabs', 'words': words},
              open(os.path.join(V, 'words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    hits = sum(1 for x in heard)
    print(f'✅ {vid}: {dur:.1f}s, {len(words)} chữ, whisper nghe {hits} chữ')
    print('   nghe:', ' '.join(h['text'] for h in heard))


if __name__ == '__main__':
    main()
