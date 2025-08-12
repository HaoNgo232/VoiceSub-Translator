# VoiceSub-Translator

Công cụ giúp tự động xử lý và dịch phụ đề cho video.

## Cài đặt nhanh

1. Cài Python 3.10+ và [ffmpeg](https://ffmpeg.org/).
2. Tải mã nguồn và mở thư mục dự án:

   ```bash
   git clone <duong-dan-repo>
   cd VoiceSub-Translator
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env         # sửa lại nếu cần API key
   python run.py
   ```

3. Giao diện sẽ hiển thị, chọn thư mục và bắt đầu xử lý phụ đề.

## Kiểm tra (tùy chọn)

Sau khi cài đặt, có thể chạy bộ kiểm thử:

```bash
pytest
```

