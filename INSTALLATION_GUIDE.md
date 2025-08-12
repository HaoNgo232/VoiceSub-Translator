# 🚀 VoiceSub-Translator - Hướng dẫn cài đặt đơn giản

## 📋 Tổng quan

Dự án này cung cấp các script tự động để giải quyết vấn đề conflict thư viện và đơn giản hóa quá trình cài đặt.

## 🛠️ Các script có sẵn

### 1. `smart_install.sh` - Script cài đặt thông minh
- ✅ Tự động phát hiện và giải quyết conflict thư viện
- ✅ Tạo môi trường ảo mới
- ✅ Cài đặt dependencies với phiên bản cụ thể
- ✅ Kiểm tra và xác minh cài đặt
- ✅ Tạo script khởi chạy tự động

**Sử dụng:**
```bash
chmod +x smart_install.sh
./smart_install.sh
```

### 2. `requirements.txt` - File dependencies
- 📦 Chứa tất cả thư viện cần thiết với phiên bản cụ thể
- 🔒 Tránh conflict giữa các phiên bản
- 🎯 Tối ưu hóa cho VoiceSub-Translator

### 3. `run_app.py` - Script chạy ứng dụng Python
- 🐍 Script Python để chạy ứng dụng
- 🔍 Tự động kiểm tra môi trường
- 🚀 Tự động phát hiện và chạy GUI phù hợp

**Sử dụng:**
```bash
source venv/bin/activate
python run_app.py
```

### 4. `check_env.py` - Kiểm tra môi trường
- 🔍 Kiểm tra toàn bộ môi trường
- 📊 Báo cáo chi tiết về dependencies
- ⚠️ Phát hiện vấn đề và đưa ra gợi ý

**Sử dụng:**
```bash
source venv/bin/activate
python check_env.py
```

### 5. `quick_run.sh` - Script chạy nhanh
- ⚡ Script bash để chạy ứng dụng nhanh
- 🔧 Tự động kích hoạt môi trường ảo
- 🎯 Chạy ứng dụng phù hợp nhất

**Sử dụng:**
```bash
chmod +x quick_run.sh
./quick_run.sh
```

## 🚀 Quy trình cài đặt đơn giản

### Bước 1: Cài đặt ban đầu
```bash
# Cấp quyền thực thi cho script
chmod +x smart_install.sh

# Chạy script cài đặt
./smart_install.sh
```

### Bước 2: Kích hoạt môi trường ảo
```bash
source venv/bin/activate
```

### Bước 3: Chạy ứng dụng
```bash
# Cách 1: Sử dụng script Python
python run_app.py

# Cách 2: Sử dụng script bash
./quick_run.sh

# Cách 3: Chạy trực tiếp
python run_modern_gui.py
```

## 🔧 Khắc phục sự cố

### Kiểm tra môi trường
```bash
python check_env.py
```

### Cài đặt lại dependencies
```bash
# Xóa môi trường ảo cũ
rm -rf venv

# Chạy lại script cài đặt
./smart_install.sh
```

### Cập nhật dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## 📚 Các lệnh hữu ích

```bash
# Kiểm tra phiên bản Python
python --version

# Kiểm tra pip
pip --version

# Liệt kê packages đã cài đặt
pip list

# Kiểm tra môi trường ảo
which python

# Xóa cache pip
pip cache purge
```

## 🎯 Lưu ý quan trọng

1. **Luôn kích hoạt môi trường ảo** trước khi chạy ứng dụng
2. **Không cài đặt packages globally** để tránh conflict
3. **Sử dụng script cài đặt** thay vì cài đặt thủ công
4. **Kiểm tra môi trường** nếu gặp lỗi

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. Chạy `python check_env.py` để kiểm tra
2. Xem log lỗi chi tiết
3. Chạy lại `./smart_install.sh`
4. Kiểm tra phiên bản Python (cần 3.8+)

## 🎉 Kết quả mong đợi

Sau khi cài đặt thành công:
- ✅ Môi trường ảo hoạt động
- ✅ Tất cả dependencies đã cài đặt
- ✅ Không có conflict thư viện
- ✅ Ứng dụng chạy mượt mà

---

**Chúc bạn có trải nghiệm sử dụng tuyệt vời với VoiceSub-Translator! 🎬✨**