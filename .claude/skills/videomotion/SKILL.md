---
name: videomotion
description: Dùng khi chồng iu gọi "/videomotion", hoặc muốn dựng video giới thiệu / xả kho / khuyến mãi cho một gói tài khoản AI của apihub247 (Gemini, ChatGPT, Claude, Veo, Cursor…) theo kiểu quay màn hình web thật + motion graphic sticker, để đăng TikTok.
---

> Bản đóng gói công khai ngày 03/11/2026: chạy lệnh từ `<repo>/luma-video`; cài đặt theo `README.md` ở gốc repo. Những đường dẫn dự án/video/báo cáo riêng và memory Drive trong hướng dẫn gốc là tư liệu lịch sử, không có trong gói này. Dùng `examples/` và mẫu kiểm thử do `scripts/make_demo.py` tạo để bắt đầu; lấy nguồn sản phẩm mới cho mỗi video. Upload Drive chỉ thực hiện qua kết nối Drive hiện có.


# /videomotion: tin AI hot + lồng giới thiệu gói khéo = quay web thật + motion graphic kiểu C

Cách dựng (quay web thật + sticker) lấy từ đợt 29/10/2026, chồng iu đã duyệt "rất ổn". Mẫu thật nằm ở `public/videos/2026-10-29-xakho-*`, storyboard ở `docs/storyboards/2026-10-29-xa-kho-6-video/`.

**Luật nội dung đổi từ 02/11/2026.** TikTok đã gỡ 3 video bán gói và cảnh báo kênh. **Bắt buộc Read `../tiktok-an-toan/SKILL.md` trước khi viết storyboard.** Các mẫu cũ (đợt 29–31/10) chỉ để học cách dựng; phần giá, shop, bot trong đó nay bị cấm.

Thư mục làm việc: `<repo>/luma-video`. Công cụ: `tools/xakho/`. Định dạng `edl.json` và dữ liệu từng loại motion graphic: xem `edl-reference.md` cạnh file này.

## Luật cứng
1. **Giá đọc bằng "cá" / "xu"** (chồng iu chốt lại 03/11, thay luật 02/11).
   - Video **tin tức lồng bán**: phần lớn là tin, 1–2 câu cuối dẫn khéo về gói, được nói giá ("gói này chỉ 69 cá", "tính ra vài xu mỗi ngày").
   - Video **bán thẳng**: nói thẳng gói + giá bằng "N cá", được dùng "lụm", "chốt".
   - Giá hiện ở lời đọc, phụ đề, thẻ MG (`slam`, `strike`, `math`, `choice` đều được, ghi "CÁ"). **Không** ghi giá trên thumbnail và caption.
   - **Vẫn cấm:** "tài khoản", "nick", "đăng nhập", "mật khẩu", "tiền", "đồng", "k", "USD", "đô", "mua ngay", "giảm giá", "khuyến mãi", "thanh toán", "chuyển khoản", "bảo hành", "giao tự động", "mail chính chủ". Danh sách đủ ở skill `tiktok-an-toan`.
   - Ảnh trang shop: ghi `"prices": "giu"`, không khoanh, không cho con trỏ bấm vào giá.
2. **Mỗi video một bộ cảnh riêng.** Hai video cùng sản phẩm không chung ảnh nguồn nào, và `qa.py` phải báo `chung-ảnh-A/B=[]`.
3. **Vùng an toàn TikTok:**
   - trình duyệt ở y 392–1392;
   - phụ đề ở y 1450;
   - motion graphic trong x 60–940.
4. **CTA = trang cá nhân kênh** (chồng iu chốt 02/11).
   - Không nhắc web, shop, bot ở lời, phụ đề, MG, caption: không `shop.apihub247.com`, không `@apihub247bot`, không cảnh trang bot Telegram.
   - Không gọi tên nền tảng (Zalo, Facebook, Tele/Telegram, YouTube, Instagram…). Không nói "link bio", "inbox".
   - Câu mời nhẹ ở cuối, ví dụ "Bác nào muốn thử Gemini Pro thì xem ở trang cá nhân kênh nhé".
   - Không dùng MG `end` (thẻ shop + bot). Kết bằng `stack` một mục, chạy tới hết video: `head: "XEM Ở TRANG CÁ NHÂN"`, item `{icon: "user", title: "apihub247", sub: "thông tin gói ở trang cá nhân kênh"}`.
   - Khoảng 70% là chia sẻ tin hot thật sự hữu ích; chỉ 1–2 câu cuối dẫn về gói.
   - **Mẫu theo luật mới:** `tools/xakho/projects/2026-11-02-vm.py`, có thẻ kết `ask()` / `profile()`, `prices: "giu"`, làm mờ trang shop bằng `SHOP_BLUR` và mờ giá trang chính hãng. Mẫu 31/10 chỉ để tham khảo mạch kể.
5. **Món hàng rủi ro cao** (tài khoản tạo từ mã giới thiệu giao mail + mật khẩu, bản dùng thử kèm điện thoại, gói chia sẻ gia đình): hỏi chồng iu trắc nghiệm theo skill `tiktok-an-toan` trước khi làm.
6. **Quy tắc toàn cục:** gọi "chồng iu", hỏi bằng trắc nghiệm, backup trước mọi lần sửa, không xoá khi chưa hỏi, verify bằng file thật.
7. **Tỉ lệ mỗi đợt (tới 30/01/2027):** ít nhất 4 video chia sẻ thuần cho mỗi 1 video lồng bán. Đợt 02/11 chồng iu chọn 5 + 1.
   - Video chia sẻ thuần dựng y như video lồng bán, nhưng bỏ câu dẫn về gói và cảnh trang shop, không nhắc apihub247.
   - Câu cuối là câu hỏi giao lưu, ví dụ "Các bác sẽ giao việc gì cho nó đầu tiên? Comment em biết nhé".
   - Thẻ kết `stack` chạy tới hết video: `head: "CÁC BÁC NGHĨ SAO?"`, item `{icon: "spark", title: "<câu hỏi ngắn>", sub: "comment cho em biết nhé"}`.
8. **Không tự động hoá bàn phím** (keybd_event, gửi phím, focus cửa sổ). Ngày 29/10 phím Alt bị kẹt, làm liệt bàn phím của chồng iu. Cảnh terminal nào cần bấm thì nhờ chồng iu, hoặc dùng trang chính thức.

## Bốn dạng video (học từ kênh @100dayvibecoding, chồng iu chọn ngày 02/11)
Kênh mẫu có 13 nghìn người theo dõi. Video nhiều view nhất là meme 16 giây (221 nghìn view, 2.255 lượt chia sẻ) và video khoe kết quả 19 giây (218 nghìn view). Mỗi đợt trộn cả 4 dạng.

| Dạng | Dài | Lời | Hình |
|---|---|---|---|
| Mẹo làm được ngay | 30–45s | có giọng | Thao tác thật ngay từ giây 0: gõ, bấm, kết quả hiện ra. Ví dụ: đổi `github` thành `gitdiagram` trên link là ra sơ đồ repo |
| Tin hot kể kiểu nói chuyện | 25–35s | có giọng | Trang thật + sticker như cách dựng hiện tại, nhưng lời là lời kể chuyện (xem mục Cách viết lời) |
| Meme phản ứng | 10–20s | không lời | Meme người phản ứng ghép lên đúng màn hình công cụ AI đang gây chuyện (ví dụ model mới chỉ mở cho gói Ultra), kèm 1 dòng chữ to |
| Khoe kết quả / trước–sau | 10–20s | không lời hoặc 1–2 câu | Thứ AI làm ra đang chạy thật (web 3D, app), hoặc giao diện trước → sau |

- Video không lời vẫn xuất kèm nhạc nền nhẹ. Đầu `captions.txt` nhắc chồng iu: khi đăng, chọn âm thanh đang thịnh hành trong app TikTok.
- Meme: chỉ ghép lên màn hình mình tự quay hoặc chụp, không đăng lại nguyên clip của người khác (luật nội dung không nguyên bản).
- Mẹo, meme và khoe kết quả đều tính là video chia sẻ trong tỉ lệ 4 : 1.

## Cách viết lời (giọng biểu cảm, chồng iu chốt 02/11)
- **Câu mở:** mở bằng phản ứng, chưa nói tin ngay: "Ủa…", "Khoan đã…", "Thật luôn?!". Câu sau mới vào chuyện.
- **Giọng văn:** kể như nói với bạn. Câu ngắn, có câu hỏi tu từ.
- **Câu đùa / câu than:** mỗi video có ít nhất một câu đùa hoặc câu than gần đời người xem, ví dụ "mình loay hoay cả tuần chưa xong cái landing page".
- **Thẻ cảm xúc:** mỗi câu một thẻ, đổi liên tục, không lặp một thẻ ở 2 câu liền. Thẻ dùng: `[shocked] [curious] [excited] [laughs] [sighs] [whispers] [mischievously] [sarcastic]`.
- **Dấu câu:** "…" trước chỗ bất ngờ, "?!" cho câu sốc, chốt ngắn kiểu "Hết!".
- **Thu giọng:** dùng Adam ở chế độ biểu cảm: `--speed 1.1 --stability 0 --style 0.6`. Ngày 02/11 chồng iu nghe thử Adam, Minh Son, Văn Thuc, Viet và chọn bản này.

## Quy ước đặt tên
- Id video: `yyyy-mm-dd-vm-<sản phẩm>-a` / `-b`; thư mục ảnh nguồn của đợt: `yyyy-mm-dd-vm-shots` (dùng chung cho cả đợt).
- Mọi `edl.json` phải có `"shots_dir"` (trùng giá trị `--dir` của add_shot) và `"product"` (để `qa.py` so A/B).
- `python` hệ thống cho capture/render/thumbs/qa; **chỉ** bước giọng dùng `.venv-tts`.

## Quy trình
1. **Đọc trang chính thức và shop.** Chụp trang công khai bằng `node tools/xakho/capture_prices.mjs public/videos/<đợt>-shots <tên> <url> --find "chữ cần khoanh" …`. Ghi lại:
   - danh sách quyền lợi, lấy từ trang chính thức;
   - điều kiện riêng của gói (ví dụ "mail dùng trên 2 tháng"), để biết món hàng có thuộc nhóm rủi ro cao không.
2. **Viết storyboard** (`docs/storyboards/<ngày>-<slug>/storyboard.md`).
   - Chạy `python ../.claude/skills/tiktok-an-toan/check.py <storyboard.md>` cho tới khi ra 0 LỖI.
   - Chồng iu duyệt bằng trắc nghiệm trước khi làm.
   - Độ dài theo dạng video ở bảng "Bốn dạng video"; lời viết theo "Cách viết lời". Giọng Adam kiểu "các bác".
   - Mạch lời (video có giọng, dạng tin hot / mẹo):
     1. hook: câu phản ứng ("Ủa…") rồi tới tin hot hoặc con số có đơn vị đi kèm ("10 triệu lượt tải");
     2. chuyện gì đang xảy ra, có bằng chứng là trang thật;
     3. làm được gì, kèm ví dụ cụ thể;
     4. mẹo hoặc ý nghĩa cho người xem;
     5. 1–2 câu dẫn khéo về gói: tính năng + giá bằng "cá" (ví dụ "bản Pro 18 tháng chỉ 69 cá"); video bán thẳng thì phần gói dài hơn, có so với trang chính hãng;
     6. CTA trang cá nhân.
   - Hai video lồng bán cùng một sản phẩm thì phải có 2 góc kể khác nhau, ví dụ "tin nóng" và "một ngày dùng thử / nỗi đau".
   - Cảnh kết cũng phải khác nhau: video A kết trên trang chính thức của sản phẩm, video B kết trên trang shop.
   - App desktop (Cursor IDE, terminal…): dùng trang chính thức có ảnh giao diện; cần quay app thật thì nhờ chồng iu tự thao tác, em chỉ chụp (`tools/xakho/termcap.py launch|grab`, không dùng lệnh `key`).
3. **Quay cảnh thật trên Chrome của chồng iu** (claude-in-chrome).
   - Luôn mở chat mới, prompt demo không dính chữ tiền.
   - Thu gọn thanh bên lịch sử.
   - Chụp `save_to_disk` với scale = 1. Scale nhỏ hơn 1 thì ảnh lưu ra cũng bị thu nhỏ.
   - Lưu từng ảnh bằng `python tools/xakho/add_shot.py <tên> <ảnh> khung=x,y,w,h blur1=… p:522.500đ=x,y,w,h --url … --dir <đợt>-shots`. `p:` khai báo hộp giá; với `"prices": "giu"` thì giá vẫn hiện nguyên.
   - Hộp tên `blur*` sẽ được làm mờ. Che: avatar, tên, "Mua tín dụng", "US$", và trên trang shop các chữ "thanh toán", "nhận hàng", "giao tự động", "mail | pass", "bảo hành", "tài khoản".
   - Cảnh trang shop trong `edl.json`: `"url": "apihub247"` (không hiện domain shop), không `type_url`.
4. **Thu giọng.**
   - Ghi `public/videos/<id>/script.json`: `lines` + `spoken`, ví dụ `"apihub247": "ây pi ai háp hai bốn bảy"`.
   - Chạy `../.venv/Scripts/python.exe tools/screenad/voice.py <id> --speed 1.1 --stability 0 --style 0.6`.
   - Thêm `--reuse` để giữ giọng đã thu, chỉ căn chữ lại. Đọc dòng "nghe:" để bắt từ đọc sai.
5. **Viết `edl.json`** (cảnh + motion graphic neo theo chữ) theo `edl-reference.md`. `tools/xakho/edls.py` là bộ EDL đợt 29/10 để **đọc tham khảo**; đợt mới thì copy thành `tools/xakho/projects/<đợt>.py`, đổi id/đường dẫn rồi chạy.
6. **Dựng.** `python tools/xakho/render.py <id> --mg` → `final.mp4`, khoảng 5 phút mỗi video. Chạy nền nếu dựng nhiều video.
7. **Thumbnail.** Khai báo `"thumb"` trong edl rồi chạy `python tools/xakho/thumbs.py <id>`. Xem `thumbnail-grid.jpg` ở cỡ lưới 3:4.
   - Không giá, không "N CÁ", không "XẢ KHO" trên thumbnail (giá chỉ nằm trong video).
   - Số luôn đi cùng đơn vị thật, cùng cỡ chữ: `num: "2TB"` + `unit: "LƯU TRỮ"`, `num: "10 TRIỆU"` + `unit: "LƯỢT TẢI"`.
8. **Caption.** Ghi `public/videos/<id>/caption.txt`:
   - 4–5 hashtag chủ đề;
   - câu mời xem trang cá nhân;
   - không giá, shop, bot, tên nền tảng.
9. **QA.**
   - Chạy `python tools/xakho/qa.py <id> …`. Phải đạt ✅ tất cả.
   - Chạy `python ../.claude/skills/tiktok-an-toan/check.py public/videos/<id>`. Phải ra 0 LỖI; từng dòng XEM thì đọc lại.
   - Đọc `qa/sheet.jpg` của từng video bằng mắt: thẻ bị xuống dòng, đè chữ, khung trống, lộ thông tin riêng.
   - Cảnh trang shop: trích khung 2 khung/giây rồi Read, tìm chữ cấm trong ảnh theo skill `tiktok-an-toan`.
10. **Giao.** Chép ra `Downloads/<SanPham>_<yyyy-mm-dd>/`: `01_<ID>.mp4`, `01_<ID>_thumbnail.jpg`… + `captions.txt` gộp caption mọi video; đối chiếu SHA256.
    - Đầu `captions.txt` ghi phần nhắc đăng của skill `tiktok-an-toan`: bật "Thương hiệu của bạn" và "Nội dung do AI tạo", nhịp đăng, Account check.
    - Gửi ảnh lưới thumbnail + 1 video mẫu bằng SendUserFile.
11. **Up Drive (tự làm, không cần hỏi; chồng iu chốt 02/11).**
    - Trong thư mục "Tài nguyên video", tạo thư mục con tên theo ngày `yyyy-mm-dd`. Ngày đó đã có thư mục thì dùng lại.
    - Up toàn bộ video, thumbnail và `captions.txt` vào thư mục đó. Cách up qua Claude in Chrome: memory "drive-upload-tai-nguyen-video" (chia mảnh 9 MB, so SHA-256 rồi mới thả).
    - Kiểm dung lượng trên Drive và mở thử 1 video phát được, rồi gửi chồng iu tên thư mục.

## Lỗi hay gặp
| Triệu chứng | Cách xử lý |
|---|---|
| Thẻ con số đập vào lúc đã sang cảnh khác | Neo `slam` vào chữ giữa câu hook và đặt `until: 1` |
| Thẻ phép chia / lựa chọn bị xuống dòng | Rút ngắn `expr` (ví dụ "2TB ÷ 5"), đưa đơn vị sang `unit` |
| Trang giá có ký hiệu ₫ tách khỏi con số | `--find "489.000"` rồi thêm vào `prices`, nới hộp sang trái khoảng 75px |
| Cảnh Chrome bị mờ | Ảnh 1568px: giữ `w` ≥ 640, cảnh cận dùng motion graphic thay vì zoom sâu |
| Thumbnail dính thẻ motion graphic | `thumbs.py` tự chọn khung trống; nếu báo lỗi thì đổi `thumb.img` |
| Whisper báo `faster_whisper` thiếu | Dùng `.venv` ở thư mục gốc repo, không dùng `.venv-voice` |
| Ảnh chụp trang docs (learn.chatgpt.com, blog Antigravity) trắng từ y≈2000 | Trang cuộn trong khung riêng: chụp lại với `capture_prices.mjs --vh <cao trang>`, rồi quét khung trắng ở mọi vị trí camera trước khi dựng |
| Quảng cáo che bài, giá nằm trong ảnh quảng cáo (VnExpress, GenK) | Chụp lại với `--noads` (ẩn iframe + khung fixed/sticky). Giá nằm trong ảnh (yen…) thì thêm hộp `blur*` |
| Job Vibi kẹt ở `processing` (đã trừ credit) | Không chạy lại `voice.py` (tốn gấp đôi). Gửi giọng bằng script tự theo dõi, kẹt quá 5 phút mới gửi lại 1 lần, rồi `voice.py --reuse` |
| Căn chữ lỗi `int('4.6')` | Thêm cách đọc số phiên bản vào `spoken`, ví dụ `"4.6": "bốn chấm sáu"` |
| Thẻ `stack` che cụm chữ đang khoanh | Đẩy camera xuống khoảng 0,27 × chiều cao khung để cụm chữ nằm nửa trên, bỏ `punch` ở cảnh đó (hàm `lift` trong project 31/10) |
| Logo nền tảng video (nút play đỏ) lọt vào khung | Làm mờ cũng không mất màu đỏ: dời camera né hẳn cột đó |
| Ảnh shop vẫn hiện nhãn vàng "N CÁ" | Shot thiếu `"prices": "giu"` |
| `check.py` báo LỖI ở `words.json` dù script đã sạch | Giọng thu từ kịch bản cũ: thu lại câu đó rồi `voice.py --reuse` |
| Thumbnail: đơn vị rơi xuống dòng, đè lên ảnh | `num` 1–2 ký tự thì `unit` ≤ 5 ký tự ("LẦN", "HÃNG", "TIẾNG"); `num` ≥ 4 ký tự thì bỏ `unit` dài. `sub` ≤ khoảng 26 ký tự |
| Thẻ `slam` mở đầu: dòng `sub` xuống dòng, đè phụ đề | Rút `sub` còn ≤ khoảng 28 ký tự; tên nhiều hãng thì đưa vào lời đọc, không nhét vào `sub` |
| Chụp trang ra "Not found" (bearblog chặn trình duyệt chạy ngầm) | Thêm `--ua` cho `capture_prices.mjs` |
| Trang có bảng cookie / quyền riêng tư che nội dung | `--hide` không hết thì đổi sang bài khác đưa cùng tin |
