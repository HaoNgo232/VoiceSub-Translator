# VoiceSub-Translator

Công cụ giúp tự động xử lý và dịch phụ đề cho video với **giao diện hiện đại**.

## ✨ Tính năng mới

### 🎨 Giao diện hiện đại
- **Dark theme** với thiết kế Material Design
- **Drag & Drop** file/folder trực quan
- **Real-time preview** phụ đề
- **Responsive layout** với sidebar
- **Keyboard shortcuts** cho thao tác nhanh

### 🌐 Dịch phụ đề nâng cao
- **10+ ngôn ngữ** với emoji flags
- **6 dịch vụ AI**: Novita, Google, Mistral, Groq, OpenRouter, Cerebras
- **Context-aware translation** thông minh
- **Batch processing** với tiến trình chi tiết

### 🚨 Xử lý lỗi thông minh
- **User-friendly error messages** với giải pháp cụ thể
- **Smart validation** với gợi ý tự động
- **Technical details** có thể mở rộng

### ⚙️ Cài đặt toàn diện
- **Default settings** cho workflow nhanh
- **Advanced options** cho người dùng chuyên nghiệp
- **Auto-backup** prompts và settings

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

## ⌨️ Phím tắt

| Phím tắt | Chức năng |
|----------|-----------|
| `Ctrl + G` | Tạo phụ đề |
| `Ctrl + T` | Dịch phụ đề |
| `Ctrl + O` | Chọn thư mục đầu vào |
| `Ctrl + S` | Mở cài đặt |
| `Ctrl + P` | Chọn file xem trước |
| `F1` | Hiện trợ giúp |
| `F5` | Làm mới giao diện |

## 💡 Mẹo sử dụng

- **Drag & Drop**: Kéo thả thư mục trực tiếp vào khu vực chọn file
- **Preview Panel**: Sử dụng panel bên phải để xem trước phụ đề
- **Settings**: Tùy chỉnh cài đặt mặc định để tiết kiệm thời gian
- **AI Services**: Thử các dịch vụ AI khác nhau để có kết quả tốt nhất
- **Backup**: Tự động backup prompts quan trọng

## Kiểm tra (tùy chọn)

Sau khi cài đặt, có thể chạy bộ kiểm thử:

```bash
pytest
```

