#!/bin/bash

# Lưu thông tin hệ thống
echo "=== Thông tin hệ thống ===" > system_info.txt
echo "OS: $(lsb_release -d | cut -f2)" >> system_info.txt
echo "Python version: $(python3 --version)" >> system_info.txt
echo "CUDA version: $(nvidia-smi | grep "CUDA Version" | awk '{print $9}')" >> system_info.txt
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)" >> system_info.txt
echo "VRAM: $(nvidia-smi --query-gpu=memory.total --format=csv,noheader)" >> system_info.txt
echo "=========================" >> system_info.txt

# Kiểm tra và cài đặt ffmpeg nếu chưa có
if ! command -v ffmpeg &> /dev/null; then
    echo "Đang cài đặt ffmpeg..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
fi

# Tạo và kích hoạt môi trường ảo
echo "Tạo môi trường ảo Python..."
python3 -m venv venv
source venv/bin/activate

# Cài đặt các thư viện
echo "Cài đặt các thư viện cần thiết..."
pip install --upgrade pip
pip install -r requirements.txt

# Kiểm tra cài đặt
echo "Kiểm tra cài đặt..."
python3 -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')" >> system_info.txt

echo "Cài đặt hoàn tất! Kiểm tra file system_info.txt để xem thông tin chi tiết." 