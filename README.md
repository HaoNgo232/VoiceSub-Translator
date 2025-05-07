# Công cụ xử lý video và dịch phụ đề

Công cụ này giúp tự động tạo phụ đề từ video và dịch sang tiếng Việt sử dụng Whisper và Groq API.

## Yêu cầu

- Python 3.8 trở lên
- FFmpeg
- CUDA (khuyến nghị)

## Cài đặt

1. Clone repository:

```bash
git clone https://github.com/yourusername/subtitle-processor.git
cd subtitle-processor
```

2. Tạo môi trường ảo và cài đặt dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

pip install -e .
```

3. Cấu hình API key:
   Tạo file `.env` trong thư mục gốc và thêm API key của Groq:

```
GROQ_API_KEY=your_api_key_here
```

## Sử dụng

### Xử lý video và tạo phụ đề

```bash
python main.py --input-dir "Khoa_hoc_mau" --output-dir "output"
```

### Xử lý video và dịch phụ đề

```bash
python main.py --input-dir "Khoa_hoc_mau" --output-dir "output" --translate
```

### Tùy chọn model Whisper

```bash
python main.py --input-dir "Khoa_hoc_mau" --output-dir "output" --model "medium.en"
```

Các model có sẵn:

- tiny, base, small, medium, large
- tiny.en, base.en, small.en, medium.en

## Cấu trúc thư mục

```
subtitle-processor/
├── src/
│   ├── processor/
│   │   └── video.py
│   ├── translator/
│   │   └── subtitle.py
│   └── utils/
│       └── logging.py
├── main.py
├── setup.py
├── requirements.txt
└── README.md
```

## Tính năng

1. Xử lý video:

   - Trích xuất audio từ video
   - Chuyển đổi audio thành text sử dụng Whisper
   - Lưu phụ đề dạng SRT

2. Dịch phụ đề:

   - Đọc file phụ đề SRT
   - Dịch sang tiếng Việt sử dụng Groq API
   - Lưu bản dịch với hậu tố \_vi

3. Xử lý hàng loạt:
   - Quét thư mục tìm video
   - Xử lý từng video
   - Báo cáo kết quả

## Lưu ý

- Đảm bảo đã cài đặt FFmpeg và thêm vào PATH
- Sử dụng GPU để tăng tốc độ xử lý
- API key của Groq có giới hạn số lượng request, hãy sử dụng hợp lý

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.

## Giấy phép

MIT License
