# 🎯 HƯỚNG DẪN CÀI ĐẶT CUDA WHISPER - PHIÊN BẢN STABLE

## ⚡ Cài đặt nhanh (khuyến nghị)

```bash
# Clone project (nếu chưa có)
cd /media/hao/Work/Documents/Apps/VoiceSub-Translator

# Chạy script tự động
chmod +x install_stable.sh
./install_stable.sh
```

## 📋 Cài đặt thủ công từng bước

### Bước 1: Tạo môi trường ảo
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### Bước 2: Core Dependencies
```bash
pip install numpy==1.26.4 filelock==3.18.0 typing-extensions==4.13.2 fsspec==2025.5.1
```

### Bước 3: PyTorch với CUDA (QUAN TRỌNG: cài trước Triton)
```bash
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
```

### Bước 4: Triton (sau PyTorch)
```bash
pip install triton==2.1.0
```

### Bước 5: Whisper Models
```bash
pip install openai-whisper==20231117 faster-whisper==1.1.1
```

### Bước 6: Các thư viện còn lại
```bash
pip install -r requirements_stable.txt
```

## 🧪 Kiểm tra cài đặt

### Test CUDA
```bash
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Test Whisper
```bash
python3 -c "import whisper; model = whisper.load_model('base.en', device='cuda'); print('Whisper OK')"
```

### Test ứng dụng
```bash
python3 src/gui/app.py
```

## 🔧 Versions đã test thành công

| Package | Version | Link |
|---------|---------|------|
| PyTorch | 2.1.0+cu118 | https://download.pytorch.org/whl/cu118 |
| Triton | 2.1.0 | PyPI |
| NumPy | 1.26.4 | PyPI |
| OpenAI Whisper | 20231117 | PyPI |
| Faster Whisper | 1.1.1 | PyPI |

## ❌ Xử lý lỗi thường gặp

### Lỗi Triton version conflict
```bash
pip uninstall triton
pip install triton==2.1.0
```

### Lỗi NumPy compatibility
```bash
pip install "numpy<2.0"
```

### Lỗi CUDA not found
- Kiểm tra NVIDIA driver: `nvidia-smi`
- Reinstall PyTorch với CUDA: xem Bước 3

### Reset hoàn toàn
```bash
rm -rf .venv
./install_stable.sh
```

## 🎯 Cách sử dụng

### GUI Application
```bash
source .venv/bin/activate
python3 src/gui/app.py
```

### Command Line
```bash
source .venv/bin/activate
python3 src/utils/whisper_transcriber.py input.mp4 --model base.en --device cuda
```

## 📊 Yêu cầu hệ thống

- Ubuntu 18.04+ hoặc Linux tương tự
- Python 3.8+
- NVIDIA GPU với CUDA 11.8+
- RAM: 8GB+ (khuyến nghị 16GB)
- Disk: 5GB+ free space

## 🔍 Debug

### Kiểm tra GPU
```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Kiểm tra versions
```bash
pip list | grep -E "(torch|triton|whisper|numpy)"
```

### Log debug
```bash
export LOG_LEVEL=DEBUG
python3 src/gui/app.py
```

---
**Lưu ý:** File này đã được test trên hệ thống Ubuntu với GTX 1650 Ti. Nếu gặp vấn đề, hãy chạy lại script `install_stable.sh`.
