"""Soát chữ dễ dính vi phạm TikTok (bán hàng, chỉ đường ra ngoài, mật mã giá) trong file của một video.

  python ../.claude/skills/tiktok-an-toan/check.py <thư mục video | file> …

Quét: caption*.txt, script.json, script.md, storyboard.json, plan.json, edl.json, beats.md, words.json (ghép lời đọc thật).
LỖI = phải sửa trước khi giao (thoát mã 1). XEM = đọc lại ngữ cảnh, đúng nghĩa bán hàng thì sửa.
Chữ nằm trong ẢNH (trang shop, thumbnail) không quét được: phải Read khung hình xuất ra (xem SKILL.md cạnh file này).
"""
import bisect, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NAMES = re.compile(r'^(caption.*\.txt|captions\.txt|script\.json|script\.md|storyboard\.json|plan\.json|edl\.json|beats\.md|words\.json)$', re.I)

# Chồng iu chốt 03/11/2026: giá đọc bằng "N cá" / "vài xu", và "lụm", "chốt" được dùng (lời, phụ đề, thẻ MG).
# Vẫn cấm: đơn vị tiền thật, chữ "tài khoản" và nhóm chữ bán hàng trực diện; caption không ghi giá.
LOI = [
    ('đơn vị tiền thật', r'\d[\d.,]*\s*(?:đ|₫|đồng|vnđ|vnd|usd|đô|củ|xị|k)(?!\w)|\$\s*\d'),
    ('chữ bán hàng trực diện', r'tài khoản|(?<!\w)nick(?!\w)|đăng nhập|mật khẩu|(?<!\w)tiền(?!\w)|miễn phí|(?<!\w)free(?!\w)|mua ngay|đặt hàng|giảm giá|khuyến mãi|(?<!\w)sale(?!\w)|báo giá|bảng giá|thanh toán|chuyển khoản'),
    ('cách giao hàng', r'bảo hành|(?<!\w)BH(?!\w)|giao tự động|mail chính chủ|nâng (?:thẳng )?mail|mail\s*\|\s*pass|chia (?:cho )?cả nhà|dùng thử kèm'),
    ('chỉ đường ra ngoài', r'zalo|telegram|(?<!\w)tele(?!\w)|t\.me/|messenger|(?<!\w)inbox(?!\w)|(?<!\w)ib(?!\w)|nhắn bot|@\w*bot(?!\w)|apihub247bot|shop\.apihub247|apihub247\.com|chấm com|https?://|www\.|link (?:ở |trong )?bio|(?<!\w)sđt(?!\w)|hotline|(?<!\d)0\d{9}(?!\d)'),
]
XEM = [
    ('chữ tiền', r'(?<!đánh )(?<!\w)giá(?!\w)(?!\s*trị)|(?<!\w)(?:mua|bán|rẻ)(?!\w)'),
    ('tiếng lóng bán (được dùng, xem có quá dày không)', r'nhấc (?:một|1) con|nhấc ngay|xả kho|(?<!\w)hời(?!\w)|liền tay'),
    ('hứa hẹn quá đà', r'không giới hạn|thả ga|100\s*%|gấp đôi|kiếm tiền|làm giàu|thu nhập'),
    ('tên nền tảng', r'facebook|youtube|instagram|whatsapp|tiktok shop|shopee|lazada'),
]
LOI = [(n, re.compile(p, re.I)) for n, p in LOI]
XEM = [(n, re.compile(p, re.I)) for n, p in XEM]


def texts(path):
    """[(vị trí, chữ)] — words.json ghép thành một câu dài, vị trí = giây; file khác theo dòng."""
    raw = open(path, encoding='utf-8-sig').read()
    if os.path.basename(path).lower() == 'words.json':
        words = json.loads(raw).get('words', [])
        starts, line, ms = [], '', []
        for w in words:
            starts.append(len(line)); ms.append(w.get('startMs', 0)); line += w.get('text', '') + ' '
        return [(lambda off: f'{ms[max(0, bisect.bisect_right(starts, off) - 1)] / 1000:.1f}s', line)]
    return [((lambda off, i=i: f'dòng {i}'), l) for i, l in enumerate(raw.splitlines(), 1)]


CAPTION_PRICE = re.compile(r'\d[\d.,]*\s*(?:cá|xu)(?!\w)|(?:vài|mấy|chục|trăm)\s+(?:cá|xu)(?!\w)', re.I)


def scan(path):
    hits = []
    is_caption = os.path.basename(path).lower().startswith('caption')
    for where, line in texts(path):
        if is_caption:                                    # caption + thumbnail không ghi giá (chồng iu chốt 03/11)
            for m in CAPTION_PRICE.finditer(line):
                hits.append(('LỖI', where(m.start()), 'giá trong caption', m.group(0), line[max(0, m.start() - 30):m.end() + 30].strip()))
        for level, rules in (('LỖI', LOI), ('XEM', XEM)):
            for name, rx in rules:
                for m in rx.finditer(line):
                    a = max(0, m.start() - 30)
                    hits.append((level, where(m.start()), name, m.group(0), line[a:m.end() + 30].strip()))
    return hits


def files(args):
    for a in args:
        if os.path.isdir(a):
            for f in sorted(os.listdir(a)):
                if NAMES.match(f):
                    yield os.path.join(a, f)
        elif os.path.isfile(a):
            yield a


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    fs, nloi, nxem = list(files(sys.argv[1:])), 0, 0
    for f in fs:
        for level, where, name, word, ctx in scan(f):
            nloi += level == 'LỖI'; nxem += level == 'XEM'
            print(f'{level}  {os.path.basename(f)} {where}  [{name}] «{word}»  …{ctx}…')
    print(f'\nĐã quét {len(fs)} file: {nloi} LỖI, {nxem} XEM.' + ('' if fs else ' (không thấy file nào để quét)'))
    sys.exit(1 if nloi or not fs else 0)


if __name__ == '__main__':
    main()
