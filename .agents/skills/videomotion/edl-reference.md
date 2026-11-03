# edl.json: cảnh + motion graphic cho `tools/xakho/render.py`

Đặt tại `public/videos/<id>/edl.json`. Mốc thời gian lấy theo lời đọc (`words.json`), nên không cần đếm giây tay.

```json
{
 "shots_dir": "2026-11-02-vm-shots",
 "product": "gemini",
 "thumb": {"img": "gem-a-write-result", "variant": "v1", "tag": "TIN AI", "l1": "GEMINI 3 PRO<br>DEEP RESEARCH", "num": "2TB", "unit": "LƯU TRỮ", "sub": "theo trang Google One"},
 "shots": [
  {"line": 6, "frac": 0.0, "img": "shop-gemini-detail", "url": "apihub247",
   "tab": "ApiHub247", "tabs": ["Gemini", "ChatGPT"],
   "cam": [[0, 1700, 700, 2300], [1.6, 2300, 650, 1300]],
   "cursor": [[0.5, 1800, 900]],
   "prices": "giu"}
 ],
 "mgs": [ {"id": "mg1", "type": "slam", "line": 0, "word": "triệu", "offset": -0.1, "until": 1, "sfx": [["whoosh", 0], ["impact", 0.2]], "data": {}} ]
}
```

## Cảnh (`shots`)

**Bắt đầu cảnh:** câu `line` + `frac` (0–1) độ dài câu. Cảnh kết thúc khi cảnh sau bắt đầu.

**`img`:** tên ảnh trong `shots_dir`, đi kèm `<img>.json` (`boxes`, `prices`).
- Hộp tên `blur*` tự làm mờ.
- Mỗi giá trong `<img>.json` thành hộp `price{i}`.
- **Từ 02/11 luôn ghi `"prices": "giu"`** ở cảnh có giá: giá thật trên trang hiện nguyên, không đè nhãn "N CÁ". Không khoanh, không cho con trỏ bấm vào hộp `price{i}` (luật trong skill `tiktok-an-toan`).
- Thiếu `prices`, hoặc ghi `{chỉ_số: nhãn}` như mẫu cũ, thì giá bị đè nhãn vàng "N CÁ". Đây là cách cũ, nay đã cấm.

**`cam`:** `[dt, x, y, w]` hoặc `[dt, "box:<tên>", w]`.
- `dt` tính từ đầu cảnh; `x, y` là tâm, theo px ảnh; `w` là bề rộng khung nhìn.
- Khung trình duyệt có tỉ lệ 1080:1000, nên ảnh Chrome 1568×710 có `w` tối đa khoảng 767.

**`cursor`:** `[dt, x, y]` hoặc `[dt, "box:<tên>", "click"]`. Có `click` thì kèm tiếng click và vòng gợn.

**`marks`:** `[dt0, dt1, "box:<tên>"]`, vòng bút đỏ tự vẽ.

**`type_url`:** gõ URL trên thanh Chrome ở đầu cảnh. Không dùng ở cảnh trang shop.

**`relabel`:** thay chữ trên trang tại một hộp có sẵn.

**`url` / `tab` / `tabs`:** chữ trên thanh Chrome vẽ lại (URL, tab đang mở, các tab phụ).

## Motion graphic (`mgs`, kiểu C sticker)

**Mốc bắt đầu:** chữ `word` trong câu `line`, cộng `offset`. So khớp **chứa chuỗi, không phân biệt hoa thường, lấy lần đầu** → chọn chữ hiếm trong câu ("Kèm", "xả") để khỏi neo nhầm.

**Độ dài:** chọn một trong ba:
- `dur` (giây);
- `"dur": "end"` (tới hết video);
- `until: N` (tới đầu câu N + 0,2s).

**`sfx`:** `[[loại, dt], …]`, loại thuộc `impact`, `whoosh`, `pop`, `swipe`, `ding`, `sweep`.

| type | data |
|---|---|
| `slam` (con số đập) | `tag, prod, num, unit, sub`. `num` có 4 chữ số thì chữ tự nhỏ lại. `num` không phải tiền; `unit` là đơn vị thật ("LƯỢT TẢI", "TB") |
| `strike` (gạch giá chính hãng) | Dùng lại từ 03/11, giá ghi bằng "CÁ". `label, val, per, calcPre, count, calcUnit, stamp, strikeAt, countAt, stampAt` |
| `stack` (thẻ quyền lợi, thẻ kết) | `head, compact, top, items[{icon, title, sub, at \| word, line?}]`. `word` tìm trong câu `line` của item (mặc định câu của MG). `compact: true` + `top` khoảng 800 thì cảnh thật vẫn lộ phía trên |
| `math` (phép chia) | `expr` (ngắn, ví dụ "69 CÁ ÷ 18"), `value, dec, unit, emoji`. Đơn vị tiền chỉ được là "CÁ" / "XU" |
| `choice` (2 lựa chọn) | Dùng lại từ 03/11, nhưng **không** ghi "bảo hành / BH" (chữ cấm): đặt nhãn kiểu "1 THÁNG" / "18 THÁNG". `head, a{label, note, val}, b{…}, switchWord` |
| `end` (thẻ shop + bot) | **Cấm từ 02/11.** `big, lead, url, urlNote, or, bot, botNote` |

**Thẻ kết (thay `end`):**
```json
{"id": "mg9", "type": "stack", "line": 7, "word": "trang", "offset": -0.1, "dur": "end", "sfx": [["whoosh", 0], ["pop", 0.35]],
 "data": {"head": "XEM Ở TRANG CÁ NHÂN", "items": [{"icon": "user", "title": "apihub247", "sub": "thông tin gói ở trang cá nhân kênh"}]}}
```

Icon `stack`: `cloud spark book film code image search chart bolt mail user check globe plane`.

**Thứ tự gợi ý:**
1. `slam` (hook tin hot, con số có đơn vị);
2. `stack` (quyền lợi, tính năng);
3. `math` (tuỳ chọn, con số không phải tiền);
4. `stack` thẻ kết "XEM Ở TRANG CÁ NHÂN".

Video thứ 2 cùng sản phẩm nên bỏ bớt một loại hoặc đổi thứ tự cho khác video 1.
