# VideoMotion

Bộ công cụ cần để tạo video bằng skill **`/videomotion`**, tách từ workspace dựng video ngày **03/11/2026**. Bao gồm hai phong cách kênh (k1 vàng–đen, k2 sticker viền trắng cam–xanh), chụp web, camera/con trỏ, motion graphic, phụ đề, giọng Vibi, thumbnail và kiểm tra đầu ra.

## Nội dung

- `.claude/skills/` và `.agents/skills/`: `videomotion`, `tiktok-an-toan`, tài liệu EDL và bộ kiểm tra nội dung.
- `luma-video/tools/xakho/`: công cụ chính và hai bộ animation/thumbnail.
- `luma-video/tools/screenad/`: khung trình duyệt, con trỏ và TTS/alignment.
- `luma-video/tools/characters/vibi_tts.py`: kết nối Vibi Pro.
- `luma-video/tools/ads/`, `tools/lux/`: các module phụ trợ được pipeline import và font Be Vietnam Pro kèm OFL.
- `assets-manifest.json`: bảy SFX cần thiết, URL gốc và SHA-256; `scripts/download_assets.py` tải về máy sử dụng.

Không bao gồm Beeknoee, các workflow khác, video chiến dịch cũ, lịch sử Git cũ, môi trường Python/Node, API key hay trạng thái đăng nhập. SFX Mixkit không được phát tán kèm file nguồn; xem `sfx-library/LICENSES.md`.

## Cài đặt (Windows)

Cần Python 3.12 trở lên, Node.js, Microsoft Edge, FFmpeg + ffprobe trên PATH. Đây là bộ Windows hiện tại; chưa xác minh macOS/Linux. Trong thư mục repo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm ci
.\.venv\Scripts\python.exe scripts/download_assets.py
```

Tạo `luma-video/.env` theo `.env.example`, điền `VIBI_API_KEY` của chính bạn. Không đưa file này lên Git. Faster Whisper tải model `large-v3-turbo` lần đầu khi căn lời; cần mạng và dung lượng cho model. Font HTML được tải từ Google Fonts.

Mở repo trong Claude Code hoặc công cụ hỗ trợ agent skills, gọi `/videomotion`. Bản skill nằm trong repo; không cần skill riêng ở máy tác giả. Lệnh trong skill chạy từ `luma-video/` và Python của repo là `../.venv/Scripts/python.exe`.

## Quy trình thực tế

1. Đọc skill và tài liệu EDL, lấy nguồn mới, duyệt storyboard theo workflow hiện có.
2. Chụp trang bằng `tools/xakho/capture_prices.mjs`, hoặc thêm ảnh bằng `add_shot.py`.
3. Ghi `script.json` và `edl.json` vào `public/videos/<id>/`; tham khảo `examples/` và `.claude/skills/videomotion/edl-reference.md`.
4. Chạy giọng (có sử dụng credit Vibi):
   `../.venv/Scripts/python.exe tools/screenad/voice.py <id> --speed 1.1 --stability 0 --style 0.6`.
5. Dựng: `../.venv/Scripts/python.exe tools/xakho/render.py <id> --mg`.
6. Thumbnail: `../.venv/Scripts/python.exe tools/xakho/thumbs.py <id>`.
7. Kiểm tra: `../.venv/Scripts/python.exe tools/xakho/qa.py <id>` và `../.venv/Scripts/python.exe ../.claude/skills/tiktok-an-toan/check.py public/videos/<id>`; xem và nghe MP4 thật trước khi giao.

Giữ nguyên thẻ cảm xúc khi gọi TTS; chỉ bỏ ở chữ hiển thị/alignment. Giá, ngày và tỷ lệ nội dung trong skill là quy ước lịch sử của kênh tại ngày đóng gói, không phải dữ liệu sản phẩm mới hoặc bảo đảm chính sách nền tảng. Các tư liệu cũ và memory tài khoản riêng được nhắc trong skill không đi kèm. Drive cần kết nối tài khoản riêng.

## Demo kiểm tra không tốn credit TTS

Từ gốc repo, sau khi cài dependencies và tải SFX:

```powershell
.\.venv\Scripts\python.exe scripts/make_demo.py
cd luma-video
..\.venv\Scripts\python.exe tools/xakho/render.py 2000-01-01-vm-demo-k1 --mg
..\.venv\Scripts\python.exe tools/xakho/thumbs.py 2000-01-01-vm-demo-k1
..\.venv\Scripts\python.exe tools/xakho/qa.py 2000-01-01-vm-demo-k1
```

Đổi `k1` thành `k2` để kiểm tra bộ giao diện thứ hai. Demo dùng hình kiểm tra và âm sin; không phải video có giọng nói. Script từ chối ghi đè demo đã có. Sao lưu trước khi tự thay đổi hoặc dựng lại. Không tự động hoá bàn phím hệ thống.

Xem `VERIFICATION.md` cho phạm vi đã kiểm thử của bản công khai.
