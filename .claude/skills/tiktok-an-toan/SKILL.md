---
name: tiktok-an-toan
description: Dùng khi viết kịch bản, chữ trên hình, thumbnail, caption hoặc giao video để đăng TikTok cho kênh Cú Vọc AI, apihub247, dàn kênh nhân vật (Cú, Cáo, Thỏ, Cánh Cụt, Mèo, Gấu) hay /videomotion; hoặc khi chồng iu hỏi video có dễ bị TikTok gỡ, bị gậy, bị cảnh báo, bị khoá kênh không.
---

> Bản đóng gói công khai ngày 03/11/2026: chạy lệnh từ `<repo>/luma-video`; cài đặt theo `README.md` ở gốc repo. Những đường dẫn dự án/video/báo cáo riêng và memory Drive trong hướng dẫn gốc là tư liệu lịch sử, không có trong gói này. Dùng `examples/` và mẫu kiểm thử do `scripts/make_demo.py` tạo để bắt đầu; lấy nguồn sản phẩm mới cho mỗi video. Upload Drive chỉ thực hiện qua kết nối Drive hiện có.


# Luật đăng TikTok an toàn (từ 02/11/2026)

Kênh đã bị gỡ 3 video và bị cảnh báo trong 31/10–01/11/2026. Các vi phạm này còn tính tới khoảng **30/01/2027**; thêm một vi phạm cùng nhóm là có thể mất kênh. Báo cáo gốc có trích dẫn chính sách: `C:\Users\Admin\Downloads\BaoCao_ViPham_TikTok_2026-11-01.html`.

Nguyên nhân chính là video **bán gói AI** có chữ "tài khoản", giá bằng tiền thật, trang shop và bot Telegram. Từ 03/11 chồng iu cho dùng lại "cá", "xu", "lụm", "chốt" (xem bảng Ba loại video).

Luật áp dụng cho **mọi** chữ trong video: lời đọc, phụ đề, motion graphic, chữ trong ảnh, thumbnail, caption, hashtag.

## Ba loại video (chồng iu chốt lại 03/11/2026)

| | Video chia sẻ | Tin tức lồng bán khéo | Bán thẳng |
|---|---|---|---|
| Skill | `videomotion` (chia sẻ thuần), `video-trailer` | `videomotion` | `videomotion` |
| Giá | Không có ở đâu cả | 1–2 câu cuối dẫn khéo về gói, **được** nói giá bằng "N cá" / "vài xu" | Nói thẳng gói + giá bằng "N cá" / "xu", được dùng "lụm", "chốt" |
| Giá hiện ở đâu | — | Lời đọc, phụ đề, thẻ MG (kể cả thẻ so giá chính hãng `strike` / `math` / `choice`, ghi bằng "cá"). **Không** ghi giá trên thumbnail và caption. Giá thật trong ảnh trang shop để nguyên (`"prices": "giu"`) | Như cột bên trái |
| Câu kết | `videomotion`: câu hỏi giao lưu, không nhắc gói. Trailer: tên `apihub247`, không link | Mời xem **trang cá nhân kênh** | Mời xem **trang cá nhân kênh** |
| Thẻ kết trên hình | `stack` câu hỏi giao lưu / tên `apihub247` không `.com` | `stack` "apihub247 · thông tin ở trang cá nhân kênh" | như cột bên trái |

Chồng iu đã được nhắc rủi ro (báo cáo 01/11 coi mật mã giá là dấu hiệu lách) và vẫn chọn cho dùng "cá", "xu", "lụm", "chốt". Không nhắc lại rủi ro này nữa.

## Chữ cấm và cách thay

| KHÔNG dùng | Thay bằng |
|---|---|
| Đơn vị tiền thật: "99k", "69.000đ", "đồng", "VNĐ", "USD", "đô", "củ", "$" | "69 cá", "vài xu mỗi ngày" (chỉ ở video lồng bán / bán thẳng) |
| **"tài khoản"**, "nick", "đăng nhập", "mật khẩu", "tiền", "miễn phí/free", "mua ngay", "đặt hàng", "giảm giá", "khuyến mãi", "sale", "báo giá", "bảng giá", "thanh toán", "chuyển khoản" | "gói", "bản Pro", "nâng gói", "lụm", "chốt", "trên trang Google để … cá" |
| "mua", "bán", "rẻ", chữ "giá" đứng riêng | Nói con số bằng "cá": "chỉ 69 cá" (check.py để mức XEM vì hay trùng "giá trị", "đánh giá") |
| "nâng thẳng mail", "mail chính chủ", "giao tự động", "bảo hành / BH full", "chia cả nhà", "bản dùng thử kèm Pixel", "mail \| pass" | Không nói cách giao hàng hay cách nâng gói |
| Giá trong caption / thumbnail | Caption và thumbnail chỉ nói tính năng, tin, câu mời trang cá nhân |
| `shop.apihub247.com`, `apihub247.com`, "chấm com", `@apihub247bot`, "nhắn bot", "bot tele", `t.me`, Zalo, Telegram, inbox, "link bio", số điện thoại | Video chia sẻ: chỉ tên "apihub247". Video lồng bán: "trang cá nhân kênh" |
| Số trơ làm chữ to nhất: "10 TRIỆU" + "40 ngày", "1 TỶ" | Đơn vị đứng ngay cạnh, cùng cỡ chữ: "10 triệu **lượt tải**", "1 tỷ **người dùng**" |
| "xài thả ga", "không giới hạn", "gấp đôi hạn mức", "100%", "nhất" | Đúng điều trang chính thức ghi, kèm "theo trang X" |
| Hashtag thương hiệu người khác đi kèm bán hàng: `#meta`, `#chatgptpro` | Hashtag chủ đề: `#congcuai`, `#tinAI`, `#aiagent` |

## Hình ảnh
- Không dựng cảnh trang bot Telegram. Không gõ URL shop trên thanh địa chỉ. Ở cảnh trang shop, thanh địa chỉ chỉ hiện `apihub247` hoặc để trống.
- Trên ảnh trang shop: không khoanh giá, không cho con trỏ bấm vào giá hay nút mua. Giá nói bằng lời + thẻ MG "N CÁ" là đủ.
- Trong ảnh không được lộ các chữ: "thanh toán", "nhận hàng", "cách nhận hàng", "giao tự động", "mail | pass", "bảo hành", "tài khoản". Gặp thì phủ bằng hộp `blur*`.
- Bộ làm mờ tự động của trang shop từng để lọt chữ "thanh toán". Vì vậy phải soát trên **khung hình đã xuất**, không chỉ soát file kịch bản.

## Món hàng rủi ro cao
Có những món mà câu chữ nào cũng không cứu được, vì người kiểm duyệt xét bản chất giao dịch:
- tài khoản tạo hàng loạt từ mã giới thiệu, giao mail + mật khẩu (Muse "1 tỷ token");
- bản dùng thử đi kèm điện thoại (Pixel);
- gói chia sẻ gia đình kiểu "ADMIN … chia cả nhà".

Với những món này, hỏi chồng iu trắc nghiệm trước khi làm:
- A) Đổi sang video chia sẻ thuần về công cụ đó, không nhắc món hàng (Recommended)
- B) Bỏ chủ đề này
- C) Vẫn làm video lồng bán, chấp nhận rủi ro

## Khi chồng iu yêu cầu điều trong danh sách cấm
Chồng iu là người quyết. Nhắc rủi ro **một lần** bằng câu hỏi trắc nghiệm (A = cách an toàn, B = làm đúng như chồng iu nói). Sau đó làm theo lựa chọn, và ghi lại lựa chọn vào `project.md` của video.

## Soát trước khi giao (bắt buộc)
1. Chạy:
   ```bash
   python ../.claude/skills/tiktok-an-toan/check.py <thư mục video>
   ```
   - Lệnh quét kịch bản, caption, plan/edl, storyboard, và `words.json` (lời đọc thật sau khi thu giọng).
   - Phải ra **0 LỖI**.
   - Từng dòng XEM: đọc lại ngữ cảnh; nếu đúng nghĩa bán hàng thì sửa.
2. Read tờ khung QA, thumbnail và lưới thumbnail để soát chữ trong ảnh theo danh sách ở mục Hình ảnh.
   - Cảnh trang shop: trích thêm khung 2 khung/giây rồi Read từng khung, vì tờ khung QA có thể bỏ sót.
3. Ghi phần nhắc đăng dưới đây vào tin nhắn giao video. Khi giao nhiều video thì ghi thêm ở đầu file gộp `captions.txt`.
   - **Không** ghi vào `caption.txt` của từng video. File đó chỉ chứa đúng chữ chồng iu dán lên TikTok.

   Phần nhắc đăng:
   - Video có nhắc apihub247: bật **Tiết lộ nội dung thương mại → Thương hiệu của bạn**. Đây là quy định bắt buộc của TikTok và Luật Quảng cáo 75/2025/QH15; bật không làm giảm lượt xem.
   - Bật **Nội dung do AI tạo**, vì giọng TTS và cảnh trình duyệt dựng lại.
   - Mỗi kênh 1–3 video/ngày, cách nhau vài giờ, đăng tay bằng app. Không dùng công cụ hẹn giờ của bên thứ ba.
   - Tới 30/01/2027, mỗi kênh giữ ít nhất 4 video chia sẻ cho mỗi 1 video lồng bán.
   - Mỗi sáng xem **TikTok Studio → Account check** trước khi đăng; trạng thái xấu đi thì dừng.
   - Không đăng lại video đã bị gỡ hay bản na ná, không đem sang kênh khác. Các kênh cùng chủ, cùng số điện thoại bị TikTok coi là liên quan.
   - Không trả lời bình luận bằng link, tên bot hay giá. Ai hỏi thì mời xem trang cá nhân.

## Lỗi hay gặp
| Triệu chứng | Cách xử lý |
|---|---|
| Check báo LỖI ở `words.json` dù kịch bản đã sạch | Giọng thu từ kịch bản cũ: thu lại câu đó |
| Check báo «chấm com» | Bảng `spoken` còn cách đọc "shop.apihub247.com": xoá mục đó |
| Pill CTA lux hiện `apihub247.com` | Thiếu `plan.cta.url`: đặt `"url": "apihub247"` |
| Ảnh shop hiện nhãn vàng "N CÁ" | Shot trong `edl.json` thiếu `"prices": "giu"` |
