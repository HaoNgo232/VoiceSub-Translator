# Hướng Dẫn Quản Lý Dependencies - VoiceSub-Translator

## Tổng Quan

Dự án VoiceSub-Translator sử dụng file `requirements.txt` để quản lý các thư viện Python cần thiết. File này đã được tạo và cấu hình đúng để giải quyết vấn đề không thể tìm kiếm dependencies.

## Cấu Trúc Dependencies

### 1. Core Dependencies (AI & Machine Learning)
- **PyTorch**: Framework AI chính
  - `torch>=2.0.0` - Core PyTorch
  - `torchaudio>=2.0.0` - Xử lý audio
  - `torchvision>=0.15.0` - Xử lý video/image

- **Speech Recognition**
  - `openai-whisper>=20231117` - OpenAI Whisper
  - `faster-whisper>=0.9.0` - Faster Whisper (tối ưu hóa)

### 2. GUI Framework
- `customtkinter>=5.2.0` - Giao diện hiện đại
- `Pillow>=9.0.0` - Xử lý hình ảnh

### 3. Data Processing
- `numpy>=1.21.0` - Tính toán số học
- `scipy>=1.7.0` - Khoa học tính toán
- `pandas>=1.3.0` - Phân tích dữ liệu

### 4. API & Networking
- `requests>=2.25.0` - HTTP requests
- `openai>=1.0.0` - OpenAI API client

### 5. Audio/Video Processing
- `ffmpeg-python>=0.2.0` - FFmpeg wrapper
- `pydub>=0.25.0` - Xử lý audio

### 6. Utilities
- `pathlib2>=2.3.0` - Quản lý đường dẫn
- `typing-extensions>=4.0.0` - Type hints
- `psutil>=5.8.0` - System monitoring

### 7. Development Tools (Tùy chọn)
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage testing
- `black>=22.0.0` - Code formatter
- `flake8>=5.0.0` - Linter

## Cách Sử Dụng

### 1. Cài Đặt Tự Động (Khuyến nghị)

```bash
# Chạy script cài đặt tự động
python3 install_dependencies.py
```

Script này sẽ:
- Kiểm tra môi trường Python
- Nâng cấp pip
- Cài đặt dependencies theo thứ tự ưu tiên
- Xử lý xung đột và retry
- Xác minh cài đặt

### 2. Cài Đặt Thủ Công

```bash
# Cài đặt tất cả dependencies
pip install -r requirements.txt

# Hoặc cài đặt từng nhóm
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu
pip install openai-whisper faster-whisper
pip install customtkinter Pillow
pip install numpy scipy pandas
pip install requests openai
pip install ffmpeg-python pydub
pip install pathlib2 typing-extensions psutil
```

### 3. Kiểm Tra Dependencies

```bash
# Kiểm tra trạng thái tất cả dependencies
python3 check_dependencies.py

# Validate cú pháp requirements.txt
python3 validate_requirements.py

# Test requirements.txt
python3 test_requirements.py
```

## Quản Lý Môi Trường

### Tạo Môi Trường Ảo

```bash
# Tạo môi trường ảo
python3 -m venv venv

# Kích hoạt môi trường ảo
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies trong môi trường ảo
pip install -r requirements.txt
```

### Cập Nhật Dependencies

```bash
# Cập nhật tất cả packages
python3 update_deps.py

# Hoặc cập nhật thủ công
pip install --upgrade -r requirements.txt
```

## Xử Lý Sự Cố

### 1. Lỗi "externally-managed-environment"

**Nguyên nhân**: Hệ thống không cho phép cài đặt packages trực tiếp

**Giải pháp**:
```bash
# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt trong môi trường ảo
pip install -r requirements.txt
```

### 2. Xung Đột Phiên Bản

**Nguyên nhân**: Các packages có yêu cầu phiên bản khác nhau

**Giải pháp**:
```bash
# Cài đặt từng nhóm theo thứ tự ưu tiên
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 3. Lỗi Compile

**Nguyên nhân**: Một số packages cần compiler

**Giải pháp**:
```bash
# Cài đặt build tools
sudo apt-get install build-essential python3-dev

# Hoặc sử dụng pre-compiled wheels
pip install --only-binary=all -r requirements.txt
```

## Tùy Chỉnh

### Thêm Dependencies Mới

1. Thêm vào `requirements.txt`:
```
# New category
new-package>=1.0.0
```

2. Cập nhật `update_deps.py`:
```python
check_packages = [
    # ... existing packages
    'new_package'
]
```

### Loại Bỏ Dependencies

1. Xóa khỏi `requirements.txt`
2. Cập nhật `update_deps.py`
3. Chạy `pip uninstall package-name`

## Monitoring & Maintenance

### Kiểm Tra Phiên Bản

```bash
# Xem phiên bản đã cài đặt
pip list

# Kiểm tra dependencies cụ thể
python3 -c "import torch; print(torch.__version__)"
```

### Backup & Restore

```bash
# Backup requirements.txt
cp requirements.txt requirements_backup_$(date +%Y%m%d).txt

# Restore từ backup
cp requirements_backup_YYYYMMDD.txt requirements.txt
```

### Cleanup

```bash
# Xóa packages không sử dụng
pip autoremove

# Xóa cache pip
pip cache purge
```

## Kết Luận

File `requirements.txt` đã được tạo và cấu hình đúng để giải quyết vấn đề dependencies. Sử dụng các script tự động để cài đặt và quản lý dependencies một cách hiệu quả.

**Lưu ý quan trọng**:
- Luôn sử dụng môi trường ảo
- Cài đặt dependencies theo thứ tự ưu tiên
- Kiểm tra trạng thái trước khi chạy ứng dụng
- Backup requirements.txt trước khi thay đổi