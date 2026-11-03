"""Giọng đọc qua Vibi (api.vibi.pro: ElevenLabs / MiniMax / CapCut). Key đọc từ VIBI_API_KEY trong luma-video/.env.

  python tools/characters/vibi_tts.py "<lời>" <out.mp3> --voice <voice_id> [--provider elevenlabs|minimax|capcut]
         [--model eleven_v4] [--lang vi] [--speed 1.0]

Dùng làm thư viện: synth(text, out, voice, provider, model, lang, speed) → đường dẫn mp3.
Vibi xử lý bất đồng bộ: POST /v1/text-to-speech/{voice} → id, hỏi /v1/history/{id} tới khi completed → tải audio_url.
"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
API = 'https://api.vibi.pro/v1'
UA = 'Mozilla/5.0 (luma-video vibi_tts)'
DEFAULT_MODEL = {'elevenlabs': 'eleven_v4', 'minimax': 'speech-2.8-hd', 'capcut': 'capcut'}


def key():
    for line in open(os.path.join(ROOT, '.env'), encoding='utf-8'):
        if line.startswith('VIBI_API_KEY='):
            return line.split('=', 1)[1].strip()
    raise SystemExit('Thiếu VIBI_API_KEY trong .env')


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'xi-api-key': key(), 'Content-Type': 'application/json', 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def synth(text, out, voice, provider='elevenlabs', model=None, lang='vi', speed=1.0, timeout=180, stability=None, style=None):
    """stability (ElevenLabs): 0.0 = Creative (biểu cảm nhất), 0.5 = Natural, 1.0 = Robust; style 0–1 = độ cường điệu cảm xúc."""
    vs = {'speed': speed}
    if stability is not None: vs['stability'] = stability
    if style is not None: vs['style'] = style
    body = {'text': text, 'provider': provider, 'model_id': model or DEFAULT_MODEL[provider],
            'language_code': 'Vietnamese' if provider == 'minimax' and lang == 'vi' else lang,
            'voice_settings': vs}
    task = call('POST', f'/text-to-speech/{voice}', body)
    t0 = time.time()
    while True:
        h = call('GET', f'/history/{task["id"]}')
        if h['status'] == 'completed':
            break
        if h['status'] == 'failed' or time.time() - t0 > timeout:
            raise RuntimeError(f'Vibi lỗi ({h["status"]}): {h.get("error")}')
        time.sleep(1.5)
    with urllib.request.urlopen(urllib.request.Request(h['result']['audio_url'], headers={'User-Agent': UA}), timeout=120) as r, open(out, 'wb') as f:
        f.write(r.read())
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    synth(a[0], a[1], opt('--voice'), opt('--provider', 'elevenlabs'), opt('--model'), opt('--lang', 'vi'), float(opt('--speed', 1.0)))
    print('✅', a[1])
