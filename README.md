# VoiceSub Translator - Chuyển Đổi Định Dạng Phụ Đề

## Tính năng mới: Chuyển đổi định dạng phụ đề

Đã thêm tính năng chuyển đổi định dạng phụ đề từ các định dạng khác sang SRT:

1. **Thiết kế theo kiểu Provider**:
   - Dễ dàng mở rộng thêm các định dạng phụ đề mới
   - Tuân thủ nguyên tắc SOLID

2. **Định dạng được hỗ trợ hiện tại**:
   - VTT (WebVTT)

3. **Tích hợp vào giao diện**:
   - Thêm nút "Chuyển đổi phụ đề" vào giao diện chính
   - Dialog chuyển đổi riêng biệt với các tùy chọn

## Cách sử dụng

### Qua giao diện

1. Mở ứng dụng VoiceSub Translator
2. Nhấn nút "Chuyển đổi phụ đề"
3. Chọn thư mục chứa các file phụ đề cần chuyển đổi
4. Nhấn "Chuyển đổi"

### Qua dòng lệnh

```bash
python -m src.utils.subtitle_generator /đường/dẫn/thư/mục --convert
```

## Cấu trúc mã nguồn

```
src/
├── utils/
│   ├── subtitle_generator.py
│   ├── subtitle_format_converter/
│   │   ├── __init__.py
│   │   ├── converter.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   └── vtt_provider.py
```

## Thêm định dạng mới

Để thêm định dạng phụ đề mới:

1. Tạo file provider mới trong thư mục `providers/`
2. Kế thừa từ lớp `SubtitleFormatConverter`
3. Đăng ký provider trong `providers/__init__.py`