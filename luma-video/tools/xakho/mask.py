"""Che chữ giá trên ảnh chụp shop bằng nhãn vàng "<số> CÁ" (luật không chữ tiền, 29/10).
  mask(img, meta, {"165.000đ": "69 CÁ", "165.000đ#2": "165 CÁ"}) → ảnh mới (bản gốc giữ nguyên)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = str(Path(__file__).resolve().parents[1] / 'ads' / 'fonts' / 'BeVietnamPro-Black.ttf')


def mask(im, meta, labels):
    im = im.copy()
    d = ImageDraw.Draw(im)
    for key, text in labels.items():
        x, y, w, h = meta['boxes'][key]
        if x - 6 < 0 or x + w > im.width or y + h > im.height:    # nằm ngoài ảnh (băng chuyền trượt ngang)
            continue
        bg =im.getpixel((int(x) - 6, int(y + h / 2)))           # màu nền ngay cạnh chữ giá
        d.rectangle((x - 4, y - 4, x + w + 4, y + h + 4), fill=bg)
        f = ImageFont.truetype(FONT, int(h * 0.82))
        tw = d.textlength(text, font=f)
        pad = h * 0.32
        x1 = x + w + 4; x0 = x1 - tw - 2 * pad                     # canh phải như chữ giá gốc
        d.rounded_rectangle((x0, y - h * 0.12, x1, y + h * 1.12), radius=h * 0.5, fill=(255, 212, 0))
        d.text(((x0 + x1) / 2, y + h / 2), text, font=f, fill=(20, 20, 20), anchor='mm')
    return im


def cá(text):
    """'1.250.000đ' / 'Từ20.000đ' → '1250 CÁ' / 'TỪ 20 CÁ' (luật không chữ tiền)."""
    import re
    if '$' in text:                                        # USD → cá theo tỷ giá ngày dựng (31/10: 25.802)
        return f"{round(float(text.strip('$')) * 25802 / 1000)} CÁ"
    v = int(re.sub(r'\D', '', text)) // 1000
    return ('TỪ ' if text.startswith('Từ') else '') + f'{v} CÁ'


def mask_prices(im, meta, override=None):
    """Che MỌI chữ giá trong meta['prices'] (capture_prices.mjs). override: {chỉ_số: nhãn} hoặc {chữ_giá: nhãn}
    để đổi sang mức mới chồng iu chốt (vd mức 165.000đ đầu tiên trên trang → '69 CÁ')."""
    override = override or {}
    meta = dict(meta, boxes={})
    labels = {}
    for i, p in enumerate(meta['prices']):
        key = f'p{i}'
        meta['boxes'][key] = p['box']
        labels[key] = override.get(i, override.get(p['text'], cá(p['text'])))
    return mask(im, meta, labels)
